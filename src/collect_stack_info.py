import requests
import json
import time
import logging
from concurrent.futures import ProcessPoolExecutor
from typing import List, Dict, Any

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StackCollector:
    def __init__(self, timeout: int = 10):
        """初始化堆栈收集器
        
        Args:
            timeout: 请求超时时间(秒)
        """
        self.timeout = timeout
        
    def fetch_stack_data(self, endpoint: str) -> Dict[str, Any]:
        """从单个端点获取堆栈数据
        
        Args:
            endpoint: 数据接口URL
            
        Returns:
            包含堆栈信息的字典
            
        Raises:
            Exception: 请求失败或解析异常
        """
        try:
            logger.info(f"正在从 {endpoint} 获取堆栈数据")
            response = requests.get(endpoint, timeout=self.timeout)
            response.raise_for_status()  # 检查请求是否成功
            return response.json()
        except Exception as e:
            logger.error(f"从 {endpoint} 获取数据失败: {str(e)}")
            return {"error": str(e), "endpoint": endpoint}
    
    def collect_from_multiple_endpoints(self, endpoints: List[str], max_workers: int = 5) -> List[Dict[str, Any]]:
        """并行从多个端点收集堆栈数据
        
        Args:
            endpoints: 端点URL列表
            max_workers: 最大并行进程数
            
        Returns:
            包含所有端点堆栈信息的列表
        """
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.fetch_stack_data, endpoints))
        return results
    
    def save_to_json(self, data: List[Dict[str, Any]], filename: str) -> None:
        """将收集的数据保存到JSON文件
        
        Args:
            data: 要保存的数据
            filename: 目标文件名
        """
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info(f"数据已保存到 {filename}")

if __name__ == "__main__":
    # 示例使用
    endpoints = [
        "http://127.0.0.1:9922/apis/pythonext/callstack",
        "http://127.0.0.1:9922/apis/pythonext/callstack",
        "http://127.0.0.1:9922/apis/pythonext/callstack",
        "http://127.0.0.1:9922/apis/pythonext/callstack",
    ]
    
    collector = StackCollector(timeout=15)
    stack_data = collector.collect_from_multiple_endpoints(endpoints)
    collector.save_to_json(stack_data, "4ranks_stack_data.json")    