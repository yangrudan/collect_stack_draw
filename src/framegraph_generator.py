import json
import logging
import subprocess

import os
import sys
sys.path.append(".")
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
target_subdir = 'debug'
target_dir = os.path.join(project_root, target_subdir)

from tire_stack import merge_stacks

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
        out_stacks = [[]]
        for rank in data:
            local_stack = []
            for entry in rank:
                stack = []
                if 'CFrame' in entry:
                    frame = entry['CFrame']
                    stack.append(f"{frame['func']} ({frame['file']}:{frame['lineno']})")
                elif 'PyFrame' in entry:
                    frame = entry['PyFrame']
                    stack.append(f"{frame['func']} ({frame['file']}:{frame['lineno']})")
                
                # 将调用栈路径添加到列表中
                if stack:
                    local_stack.append(';'.join(stack))  # 当前rank的堆栈
            out_stacks.append(local_stack)  # 将当前rank的堆栈添加到总堆栈列表中
            
        
        # 翻转堆栈顺序
        for stack in out_stacks:
            stack.reverse()  # 直接修改原列表
        
        # 将堆栈数据写入输出文件
        prepare_stacks = []
        for rank in out_stacks:
            if rank != []:
                data = ""
                for stack in rank:
                        data += f"{stack};"
                prepare_stacks.append(data)
        
        # 合并堆栈
        trie = merge_stacks(prepare_stacks)
        with open(self.output_file, "w") as f:
            for stack in trie:
                f.write(f"{stack}; 1\n")
    
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
            cmd = [self.flamegraph_bin, "--title=Cluster stack information", "--colors=java", "--hash", self.output_file]
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

    # generator = FlameGraphGenerator(input_json="./debug_4ranks_stack_data.json", 
    #                                 output_file="./debug_4stacks.txt")
    # generator.generate_flamegraph("./debug_flamegraph_4ranks.svg")  

    
    target_json_path = os.path.join(target_dir, 'debug_4ranks_stack_data.json')
    target_txt_path = os.path.join(target_dir, 'debug_4stacks.txt')
    target_svg_path = os.path.join(target_dir, 'debug_flamegraph_4ranks.svg')
    generator = FlameGraphGenerator(input_json=target_json_path, 
                                    output_file=target_txt_path)
    generator.generate_flamegraph(target_svg_path)  


    