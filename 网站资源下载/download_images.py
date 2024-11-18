import requests
import os
import time
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session():
    """
    创建一个带有重试机制的会话
    """
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    })
    
    return session

def extract_pattern(url):
    """
    从示例URL中提取模式
    """
    # 查找包含数字的部分
    pattern = re.search(r'(_\d{3}_)', url)
    if not pattern:
        raise ValueError("无法从URL中识别出编号模式！请确保URL中包含类似'_001_'的数字编号。")
    
    # 替换数字部分为占位符
    pattern_str = url.replace(pattern.group(), '_{:03d}_')
    return pattern_str

def download_image(session, url_pattern, number):
    """
    下载指定编号的图片
    
    Args:
        session: 请求会话
        url_pattern: URL模式字符串
        number (int): 图片编号
    """
    # 使用提供的模式生成URL
    url = url_pattern.format(number)
    
    try:
        print(f"正在下载: {url}")
        response = session.get(url, timeout=15)
        
        if response.status_code == 200:
            if 'image' in response.headers.get('Content-Type', ''):
                if not os.path.exists('downloaded_images'):
                    os.makedirs('downloaded_images')
                
                # 从URL中提取文件名
                filename = url.split('/')[-1]
                save_path = os.path.join('downloaded_images', filename)
                
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✓ 成功下载图片: {filename}")
                return True
            else:
                print(f"✗ 错误: URL返回的不是图片内容")
        else:
            print(f"✗ 错误: 状态码 {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"✗ 下载失败: {e}")
    
    return False

def get_number_range():
    """
    获取用户输入的数字范围
    """
    while True:
        try:
            range_input = input("请输入下载范围（格式：起始编号-结束编号，例如1-6）: ")
            start, end = map(int, range_input.split('-'))
            if start > end:
                print("起始编号不能大于结束编号！")
                continue
            if start < 1:
                print("起始编号不能小于1！")
                continue
            if end > 999:
                print("结束编号不能大于999！")
                continue
            return start, end
        except ValueError:
            print("格式错误！请使用正确的格式，例如：1-6")

def main():
    """
    主函数：处理用户输入并下载图片
    """
    try:
        # 获取示例URL
        example_url = input("请输入示例URL（包含编号，例如: https://example.com/image_001.png）: ")
        
        # 获取下载范围
        start_num, end_num = get_number_range()
        
        # 提取URL模式
        url_pattern = extract_pattern(example_url)
        print(f"\n识别到的URL模式: {url_pattern}")
        print(f"将下载范围: {start_num} 到 {end_num}\n")
        
        # 确认
        confirm = input("是否确认开始下载？(y/n): ")
        if confirm.lower() != 'y':
            print("已取消下载")
            return
        
        print("\n=== 开始下载图片 ===")
        session = create_session()
        success_count = 0
        total_count = end_num - start_num + 1
        
        for i in range(start_num, end_num + 1):
            retry_count = 3
            while retry_count > 0:
                if download_image(session, url_pattern, i):
                    success_count += 1
                    break
                retry_count -= 1
                if retry_count > 0:
                    print(f"将在2秒后重试... (剩余重试次数: {retry_count})")
                    time.sleep(2)
            
            # 每张图片下载之间暂停1秒
            if i < end_num:
                time.sleep(1)
        
        print("\n=== 下载任务完成 ===")
        print(f"成功下载: {success_count}/{total_count} 张图片")
        print(f"图片保存在 'downloaded_images' 文件夹中")
        
    except KeyboardInterrupt:
        print("\n\n下载已被用户中断")
    except Exception as e:
        print(f"\n发生错误: {e}")

if __name__ == "__main__":
    main()
