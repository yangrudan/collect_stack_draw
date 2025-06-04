class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_stack = False
        self.ranks = set()

    def add_rank(self, rank):
        self.ranks.add(rank)

class StackTrie:
    def __init__(self,all_ranks):
        self.root = TrieNode()
        self.all_ranks = all_ranks

    def insert(self, stack, rank):
        node = self.root
        for frame in stack:
            if frame not in node.children:
                node.children[frame] = TrieNode()
            node = node.children[frame]
            node.add_rank(rank)
        node.is_end_of_stack = True
        node.add_rank(rank)

    def _format_rank_str(self, ranks):
        ranks = sorted(ranks)
        leak_ranks = sorted(self.all_ranks - set(ranks))  # 将 ranks 转换为集合

        def _inner_format(ranks):
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
        for frame, child in node.children.items():
            rank_str = self._format_rank_str(child.ranks)
            if child.is_end_of_stack:
                yield ";".join(path + [frame]) + rank_str
            frame += rank_str
            yield from self._traverse_with_all_stack(child, path + [frame])

    def __iter__(self):
        yield from self._traverse_with_all_stack(self.root, [])

def merge_stacks(stacks):
    all_ranks = set(range(len(stacks)))
    trie = StackTrie(all_ranks)
    for rank, stack in enumerate(stacks):
        stack_frames = stack.split(";")
        trie.insert(stack_frames, rank)
    return trie

def read_file_to_list(file_path):
    """
    读取文件，将每一行作为列表的一个元素。
    :param file_path: 文件路径
    :return: 包含文件每一行内容的列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()  # 读取所有行
            lines = [line.strip() for line in lines]  # 去除每行的首尾空白字符
        return lines
    except FileNotFoundError:
        print(f"文件未找到: {file_path}")
        return []
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        return []




def main():
    stacks = [
         "main;func1;func2;func3",
         "main;func1;func2;func4",
         "main;func1;func3;func5",
         "main;func1;func3;func6"
    ]

    trie = merge_stacks(stacks)

    # 输出合并后的堆栈信息
    with open("merged_stacks.txt", "w") as f:
        for stack in trie:
            f.write(f"{stack} 1\n")

if __name__ == "__main__":
    main()
    
# /home/yang/Downloads/FlameGraph-1.0/flamegraph.pl merged_stacks.txt > mmm.svg
