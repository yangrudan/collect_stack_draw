import json
import logging
import subprocess

import sys
sys.path.append(".")

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_stack = False
        self.ranks = set()

    def add_rank(self, rank):
        self.ranks.add(rank)


class StackTrie:
    def __init__(self, all_ranks):
        self.root = TrieNode()
        self.all_ranks = all_ranks

    def insert(self, words, rank):
        node = self.root
        for word in words:
            if "lto_priv" in word:
                break
            if word not in node.children:
                node.children[word] = TrieNode()
            node = node.children[word]
            node.ranks.add(rank)
        node.is_end_of_stack = True
        node.add_rank(rank)

    def _format_rank_str(self, ranks):

        leak_ranks = list(self.all_ranks - set(ranks))
        ranks = list(ranks)

        def _inner_format(ranks):
            """fold continuous ranks, [0,1,2,5,6,7]->[0-2,5-7]
            return has stack and leak stack, suppose we have 8 ranks(0-7)
            [0,1,2,5,6,7]->0-2/5-7|3-4, means rank 0-2,5-7 has this stacktrace,
            while rank 3-4 do not have this stacktrace
            """
            ranks = sorted(ranks)
            str_buf = []
            low = 0
            high = 0
            total = len(ranks)
            while high < total - 1:
                low_value = ranks[low]
                high_value = ranks[high]
                while high < total - 1 and high_value + 1 == ranks[high + 1]:
                    high += 1
                    high_value = ranks[high]
                low = high + 1
                high += 1
                if low_value != high_value:
                    str_buf.append(f"{low_value}-{high_value}")
                else:
                    str_buf.append(str(low_value))
            if high == total - 1:
                str_buf.append(str(ranks[high]))
            return "/".join(str_buf)

        has_stack_ranks = _inner_format(ranks)
        leak_stack_ranks = _inner_format(leak_ranks)
        return f"@{'|'.join([has_stack_ranks, leak_stack_ranks])}"

    def _traverse_with_all_stack(self, node, path):
        for word, child in node.children.items():
            rank_str = self._format_rank_str(child.ranks)
            if child.is_end_of_stack:
                yield ";".join(path + [word]) + rank_str
            word += rank_str
            yield from self._traverse_with_all_stack(child, path + [word])

    def __iter__(self):
        yield from self._traverse_with_all_stack(self.root, [])

class StackViewer:
    def __init__(self, input_path):
        self.path = input_path
        self.world_size = int(4)
        self.all_ranks = set(range(self.world_size))

        self._parse()

    def _parse(self):
        self.stack_trie = StackTrie(self.all_ranks)
        with open(self.path, 'r') as file:
            lines = file.readlines()
        i = 0
        for line in lines:
            self._parse_one(line, i)
            i += 1
        with open("deal_stack", "w") as f:
            for stack in self.stack_trie:
                f.write(f"{stack} 1\n")

    def _frame_hash(self, stracetrace, rank):
        stack = stracetrace.split(";")
        stack_name = stack[:-1] 
        for name in stack_name:
            self.stack_trie.insert(name, rank)


    def _parse_one(self, rank_line, rank_id):
        self._frame_hash(rank_line, rank_id)



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
        
        # 写入输出文件
        with open(self.output_file, 'w') as f:
            for rank in out_stacks:
                if rank != []:
                    for stack in rank:
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

    StackViewer("./debug_4stacks.txt")