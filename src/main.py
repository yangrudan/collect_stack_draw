import argparse
import json
import logging
import sys

sys.path.append(".")
from collect_stack_info import StackCollector
from framegraph_generator import FlameGraphGenerator

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="分布式堆栈信息收集与火焰图生成工具")
    parser.add_argument("--config", default="../config/config.json", help="配置文件路径")
    parser.add_argument("--output", default="flamegraph.svg", help="输出火焰图文件名")
    args = parser.parse_args()
    
    try:
        # 读取配置文件
        with open(args.config, 'r') as f:
            config = json.load(f)
            
        endpoints = config.get("endpoints", [])
        if not endpoints:
            logger.error("配置文件中未找到端点列表")
            return
            
        # 收集数据
        collector = StackCollector(timeout=config.get("timeout", 10))
        stack_data = collector.collect_from_multiple_endpoints(
            endpoints, 
            max_workers=config.get("max_workers", 5)
        )
        
        # 生成火焰图
        flamegraph_bin = config.get("flamegraph_bin", "flamegraph.pl")
        generator = FlameGraphGenerator(flamegraph_bin=flamegraph_bin)
        generator.generate_flamegraph(stack_data, args.output)
        
        logger.info("任务完成")
        
    except Exception as e:
        logger.error(f"执行过程中发生错误: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()    