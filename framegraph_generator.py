import json
import logging
from typing import List, Dict, Any
import subprocess
import os
import tempfile

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FlameGraphGenerator:
    def __init__(self, flamegraph_bin: str = "flamegraph.pl"):
        """初始化火焰图生成器
        
        Args:
            flamegraph_bin: FlameGraph工具的路径
        """
        self.flamegraph_bin = flamegraph_bin
        
    def convert_to_flamegraph_format(self, stack_data: List[Dict[str, Any]]) -> str:
        """将堆栈数据转换为FlameGraph工具接受的格式
        
        Args:
            stack_data: 堆栈数据列表
            
        Returns:
            格式化的字符串
        """
        formatted_data = []
        
        for data in stack_data:
            if "error" in data:
                continue
                
            # 提取堆栈帧列表
            stack_frames = data.get("stack", [])
            if not stack_frames:
                continue
                
            # 构建调用链
            callchain = []
            for frame in stack_frames:
                if "CFrame" in frame:
                    func = frame["CFrame"].get("func", "unknown")
                    # 尝试从长函数名中提取关键部分
                    if "pybind11::cpp_function::dispatcher" in func:
                        func = "pybind11_dispatcher"
                    elif "pybind11::cpp_function::initialize" in func:
                        func = "pybind11_initializer"
                    callchain.append(func)
                elif "PyFrame" in frame:
                    func = frame["PyFrame"].get("func", "unknown")
                    file = frame["PyFrame"].get("file", "unknown")
                    # 简化文件名，只保留最后一部分
                    if file != "unknown":
                        file = os.path.basename(file)
                    callchain.append(f"{func} ({file})")
            
            # 忽略过短的调用链
            if len(callchain) < 2:
                continue
                
            # 将调用链转换为FlameGraph格式
            stack_str = ";".join(callchain)
            # 假设每个堆栈样本权重为1
            formatted_data.append(f"{stack_str} 1")
            
        return "\n".join(formatted_data)
    
    def generate_flamegraph(self, stack_data: List[Dict[str, Any]], output_file: str) -> None:
        """生成火焰图
        
        Args:
            stack_data: 堆栈数据列表
            output_file: 输出SVG文件名
        """
        # 转换数据格式
        flamegraph_input = self.convert_to_flamegraph_format(stack_data)
        
        # 创建临时文件存储转换后的数据
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            temp_file = f.name
            f.write(flamegraph_input)
            
        try:
            # 调用FlameGraph工具生成SVG
            cmd = [self.flamegraph_bin, temp_file]
            with open(output_file, 'w') as out:
                subprocess.run(cmd, stdout=out, stderr=subprocess.PIPE, check=True)
            logger.info(f"火焰图已生成: {output_file}")
        except subprocess.CalledProcessError as e:
            logger.error(f"生成火焰图失败: {e.stderr.decode('utf-8')}")
            raise
        finally:
            # 清理临时文件
            os.unlink(temp_file)

if __name__ == "__main__":
    with open("output.json", "r") as f:
        stack_data = json.load(f)
    
    generator = FlameGraphGenerator()
    generator.generate_flamegraph(stack_data, "flamegraph.svg")    