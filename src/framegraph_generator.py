import json
import logging
import subprocess


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FlameGraphGenerator:
    def __init__(self, flamegraph_bin: str = "/home/yang/Downloads/FlameGraph-1.0/flamegraph.pl"
                 ,input_json:str = "output.json"
                 ,output_file: str = "stacks.txt"):
        """初始化火焰图生成器
        
        Args:
            flamegraph_bin: FlameGraph工具的路径
        """
        self.flamegraph_bin = flamegraph_bin
        self.input_json = input_json
        self.output_file = output_file
        
    def convert_to_flamegraph_format(self):
        """将堆栈数据转换为FlameGraph工具接受的格式
        
        Args:
            stack_data: 堆栈数据列表
            
        Returns:
            格式化的字符串
        """
       # 读取 JSON 文件
        with open(self.input_json, 'r') as f:
            data = json.load(f)
        
        # 解析调用栈
        stacks = []
        for entry in data:
            stack = []
            if 'CFrame' in entry:
                frame = entry['CFrame']
                stack.append(f"{frame['func']} ({frame['file']}:{frame['lineno']})")
            elif 'PyFrame' in entry:
                frame = entry['PyFrame']
                stack.append(f"{frame['func']} ({frame['file']}:{frame['lineno']})")
            
            # 将调用栈路径添加到列表中
            if stack:
                stacks.append(';'.join(stack))
        
        # 翻转堆栈顺序
        stacks.reverse()
        
        # 写入输出文件
        with open(self.output_file, 'w') as f:
            for stack in stacks:
                f.write(f"{stack};")
            f.write(" 1\n") 
    
    def generate_flamegraph(self, output_file: str) -> None:
        """生成火焰图
        
        Args:
            stack_data: 堆栈数据列表
            output_file: 输出SVG文件名
        """
        # 转换数据格式
        flamegraph_input = self.convert_to_flamegraph_format()
             
        try:
            # 调用FlameGraph工具生成SVG
            cmd = [self.flamegraph_bin, self.output_file]
            logger.info(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            with open(output_file, 'w') as out:
                out.write(result.stdout.decode('utf-8'))
            logger.info(f"火焰图已生成: {output_file}")
        except subprocess.CalledProcessError as e:
            logger.error(f"生成火焰图失败: {e.stderr.decode('utf-8')}")


if __name__ == "__main__":
    # generator = FlameGraphGenerator(input_json="./tmp/output.json", output_file="./tmp/stacks.txt")
    # generator.generate_flamegraph("./tmp/flamegraph.svg")    

    generator = FlameGraphGenerator(input_json="../tmp/4ranks_stack_data.json", output_file="../tmp/4stacks.txt")
    generator.generate_flamegraph("../tmp/flamegraph_4ranks.svg")  