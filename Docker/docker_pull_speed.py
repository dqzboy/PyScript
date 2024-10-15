import docker
import sys
import re
import time
from collections import defaultdict
import requests
from datetime import datetime
from colorama import init, Fore, Style
from rich.console import Console
from rich.table import Table

# 需要安装的模块：pip install docker requests colorama rich


# 初始化 colorama
init(autoreset=True)

def format_size(bytes):
    """
    格式化字节数为可读的单位
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024:
            formatted = f"{bytes:.2f}{unit}"
            return formatted
        bytes /= 1024
    formatted = f"{bytes:.2f}PB"
    return formatted

def parse_size(size_str):
    """
    解析大小字符串，将其转换为字节数。
    例如：'500kB' -> 500 * 1024
    """
    size_str = size_str.strip()
    match = re.match(r'([\d\.]+)([KMGTP]?B)', size_str, re.IGNORECASE)
    if not match:
        return 0
    number, unit = match.groups()
    number = float(number)
    unit_multipliers = {
        'B': 1,
        'KB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4,
        'PB': 1024**5,
    }
    return number * unit_multipliers.get(unit.upper(), 1)

def get_public_ip_info():
    """获取本机的公网IP地址、地理区域和运营商"""
    try:
        # 获取公网IP地址
        ip_response = requests.get('http://members.3322.org/dyndns/getip', timeout=5)
        if ip_response.status_code == 200:
            ip = ip_response.text.strip()
            # 验证IP格式
            if re.match(r'\d+\.\d+\.\d+\.\d+', ip):
                # 获取地理位置信息，使用 ip-api.com
                geo_response = requests.get(f'http://ip-api.com/json/{ip}?lang=zh-CN', timeout=5)
                if geo_response.status_code == 200:
                    geo_data = geo_response.json()
                    if geo_data['status'] == 'success':
                        region = f"{geo_data.get('regionName', '')} {geo_data.get('city', '')}"
                        isp = geo_data.get('isp', '未知运营商')
                        return ip, region.strip(), isp
                    else:
                        return ip, '无法获取区域信息', '无法获取运营商信息'
                else:
                    return ip, '无法获取区域信息', '无法获取运营商信息'
            else:
                return '未知', '无法解析公网IP', '无法获取运营商信息'
        else:
            return '未知', '无法获取公网IP', '无法获取运营商信息'
    except Exception as e:
        return '未知', f"无法获取公网IP及区域信息: {e}", '无法获取运营商信息'

def docker_pull_with_speed(image):
    try:
        client = docker.from_env()
    except docker.errors.DockerException as e:
        print(f"{Fore.RED}无法连接到Docker守护进程。请确保Docker已安装并正在运行。")
        sys.exit(1)

    # 检查镜像是否已存在
    try:
        existing_image = client.images.get(image)
        print(f"{Fore.GREEN}镜像 {Fore.YELLOW}{image} {Fore.GREEN}已存在，无需拉取。")
        return
    except docker.errors.ImageNotFound:
        pass  # 镜像不存在，继续拉取
    except docker.errors.APIError as e:
        print(f"{Fore.RED}无法检查镜像是否存在：{e.explanation}")
        sys.exit(1)

    # 如果用户没有指定标签，默认使用 'latest'
    if ':' not in image:
        image += ':latest'
        print(f"{Fore.YELLOW}未指定标签，默认使用 'latest' 标签。")

    # 使用低级 API 以便获取详细的拉取信息
    low_level_client = docker.APIClient(base_url='unix://var/run/docker.sock')

    print(f"{Fore.CYAN}开始拉取镜像: {Fore.YELLOW}{image}")

    # 获取并显示公网IP地址、区域和运营商
    ip_address, region, isp = get_public_ip_info()

    # 使用 rich 来显示美化的表格
    console = Console()
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("IP地址", style="yellow", justify="center")
    table.add_column("IP区域", style="yellow", justify="center")
    table.add_column("运营商", style="yellow", justify="center")

    table.add_row(f"[bold yellow]{ip_address}[/]", f"[bold yellow]{region}[/]", f"[bold yellow]{isp}[/]")

    console.print(table)

    # 打印开始时间
    start_time = time.time()
    start_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{Fore.GREEN}开始时间: {start_datetime}")

    # 初始化变量
    total_downloaded = 0
    layer_downloaded = defaultdict(float)  # 存储每个层已下载的字节数
    layer_totals = defaultdict(float)      # 存储每个层的总字节数

    try:
        for line in low_level_client.pull(image, stream=True, decode=True):
            if 'status' in line:
                status = line['status']
                id = line.get('id', '')
                progress_detail = line.get('progressDetail', {})
                current = progress_detail.get('current', 0)
                total = progress_detail.get('total', 0)

                if 'Downloading' in status or 'Extracting' in status:
                    if id:
                        if current > layer_downloaded[id]:  # 更新递增的下载量
                            layer_downloaded[id] = current
                            layer_totals[id] = total

                    # 计算总已下载字节数
                    total_downloaded = sum(layer_downloaded.values())

                    # 计算下载速度
                    current_time = time.time()
                    elapsed_time = current_time - start_time
                    if elapsed_time > 0:
                        speed = total_downloaded / elapsed_time
                    else:
                        speed = 0

                    # 显示进度和速度
                    total_formatted = format_size(total_downloaded)
                    speed_formatted = format_size(speed)

                    # 构建输出字符串，并添加 '\033[K' 清除行尾
                    output_str = (f"\r{Fore.MAGENTA}已下载: {Fore.YELLOW}{total_formatted} | "
                                  f"{Fore.CYAN}速度: {Fore.YELLOW}{speed_formatted}/s\033[K")
                    # 使用 sys.stdout.write 输出并刷新
                    sys.stdout.write(output_str)
                    sys.stdout.flush()

        print(f"\n{Fore.GREEN}镜像拉取完成。")

        # 计算并显示结束时间和总耗时
        end_time = time.time()
        end_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        total_time = end_time - start_time
        print(f"{Fore.GREEN}结束时间: {end_datetime}")
        print(f"{Fore.GREEN}总耗时: {Fore.YELLOW}{total_time:.2f} 秒")

    except docker.errors.APIError as e:
        print(f"\n{Fore.RED}发生错误: {e.explanation}")
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}用户中断操作。")
    finally:
        client.close()

def main():
    print(f"{Fore.BLUE}欢迎使用 Docker 镜像拉取速度监控脚本！")
    image_input = input(f"{Fore.BLUE}请输入要拉取的 Docker 镜像名称和标签（例如：ubuntu:latest）：{Style.RESET_ALL}").strip()
    if not image_input:
        print(f"{Fore.RED}镜像名称不能为空。")
        sys.exit(1)

    # 如果用户没有指定标签，默认使用 'latest'
    if ':' not in image_input:
        image_input += ':latest'
        print(f"{Fore.YELLOW}未指定标签，默认使用 'latest' 标签。")

    docker_pull_with_speed(image_input)

if __name__ == "__main__":
    main()
