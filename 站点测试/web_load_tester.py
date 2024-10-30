"""
Async Web Load Tester (AWLT)
----------------------------
一个异步的网站负载测试工具，用于评估网站性能和承载能力。

特性:
- 支持高并发异步请求
- 详细的性能指标统计
- 实时进度显示
- 完整的错误追踪
- 可配置的测试参数

作者: [Ding Qinzheng]
版本: 1.0.0
日期: [2024-10-30]
许可: MIT
"""

import asyncio
import aiohttp
import time
import argparse
from datetime import datetime
from collections import defaultdict
import statistics

class LoadTester:
    def __init__(self, url, total_requests, concurrent_requests, timeout=30):
        self.url = url
        self.total_requests = total_requests
        self.concurrent_requests = concurrent_requests
        self.timeout = timeout
        self.results = []
        self.errors = defaultdict(int)
        self.start_time = None
        self.end_time = None
        
    async def make_request(self, session, request_id):
        start_time = time.time()
        try:
            async with session.get(self.url) as response:
                response_time = time.time() - start_time
                status = response.status
                if status != 200:
                    self.errors[status] += 1
                return {
                    'request_id': request_id,
                    'status': status,
                    'response_time': response_time
                }
        except Exception as e:
            self.errors[str(e)] += 1
            return {
                'request_id': request_id,
                'status': 'error',
                'response_time': time.time() - start_time,
                'error': str(e)
            }

    async def run_batch(self, start_id):
        connector = aiohttp.TCPConnector(limit=None, ssl=False)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = []
            for i in range(self.concurrent_requests):
                request_id = start_id + i
                if request_id < self.total_requests:
                    tasks.append(self.make_request(session, request_id))
            return await asyncio.gather(*tasks)

    async def run_test(self):
        print(f"\n开始测试 URL: {self.url}")
        print(f"总请求数: {self.total_requests}")
        print(f"并发数: {self.concurrent_requests}")
        print("测试进行中...\n")

        self.start_time = datetime.now()
        
        for i in range(0, self.total_requests, self.concurrent_requests):
            batch_results = await self.run_batch(i)
            self.results.extend(batch_results)
            
            # 显示进度
            completed = min(i + self.concurrent_requests, self.total_requests)
            progress = (completed / self.total_requests) * 100
            print(f"\r进度: {progress:.1f}% ({completed}/{self.total_requests})", end="")
            
        self.end_time = datetime.now()
        print("\n\n测试完成！")
        self.print_results()

    def print_results(self):
        # 计算统计数据
        response_times = [r['response_time'] for r in self.results if r['status'] == 200]
        if not response_times:
            print("没有成功的请求！")
            return

        successful_requests = len(response_times)
        failed_requests = len(self.results) - successful_requests
        total_time = (self.end_time - self.start_time).total_seconds()
        
        print("\n=== 测试结果摘要 ===")
        print(f"测试持续时间: {total_time:.2f} 秒")
        print(f"成功请求数: {successful_requests}")
        print(f"失败请求数: {failed_requests}")
        print(f"实际RPS (Requests Per Second): {len(self.results) / total_time:.2f}")
        
        if response_times:
            print(f"\n响应时间统计 (秒):")
            print(f"最小: {min(response_times):.3f}")
            print(f"最大: {max(response_times):.3f}")
            print(f"平均: {statistics.mean(response_times):.3f}")
            print(f"中位数: {statistics.median(response_times):.3f}")
            
            # 计算百分位数
            percentiles = [50, 75, 90, 95, 99]
            sorted_times = sorted(response_times)
            for p in percentiles:
                index = int(len(sorted_times) * (p / 100))
                print(f"P{p}: {sorted_times[index]:.3f}")

        if self.errors:
            print("\n错误统计:")
            for error, count in self.errors.items():
                print(f"{error}: {count} 次")

def main():
    parser = argparse.ArgumentParser(description='Website Load Testing Tool')
    parser.add_argument('url', help='要测试的网站URL')
    parser.add_argument('-n', '--requests', type=int, default=100, help='总请求数 (默认: 100)')
    parser.add_argument('-c', '--concurrent', type=int, default=10, help='并发请求数 (默认: 10)')
    parser.add_argument('-t', '--timeout', type=int, default=30, help='请求超时时间(秒) (默认: 30)')
    
    args = parser.parse_args()
    
    # 安全提示
    print("\n=== 安全提示 ===")
    print("1. 请确保您有权限对目标网站进行负载测试")
    print("2. 建议在测试环境中使用此工具")
    print("3. 过度的负载测试可能会影响服务器性能")
    print("4. 请负责任地使用此工具\n")
    
    confirm = input("您确认要继续测试吗? (yes/no): ")
    if confirm.lower() != 'yes':
        print("测试已取消")
        return

    tester = LoadTester(args.url, args.requests, args.concurrent, args.timeout)
    asyncio.run(tester.run_test())

if __name__ == '__main__':
    main()
