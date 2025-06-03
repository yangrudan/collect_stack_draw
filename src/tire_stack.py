class TrieNode:
    def __init__(self):
        self.children = {}
        self.ranks = set()

    def add_rank(self, rank):
        self.ranks.add(rank)

class StackTrie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, stack, rank):
        node = self.root
        for frame in stack:
            if frame not in node.children:
                node.children[frame] = TrieNode()
            node = node.children[frame]
            node.add_rank(rank)
        node.add_rank(rank)

    def _format_rank_str(self, ranks, all_ranks):
        ranks = sorted(ranks)
        leak_ranks = sorted(all_ranks - set(ranks))  # 将 ranks 转换为集合

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

    def _traverse_with_all_stack(self, node, path, all_ranks):
        for frame, child in node.children.items():
            rank_str = self._format_rank_str(child.ranks, all_ranks)
            if child.children:
                yield from self._traverse_with_all_stack(child, path + [frame], all_ranks)
            else:
                yield ";".join(path + [frame]) + rank_str

    def __iter__(self):
        yield from self._traverse_with_all_stack(self.root, [], self.all_ranks)

def merge_stacks(stacks):
    trie = StackTrie()
    all_ranks = set(range(len(stacks)))
    trie.all_ranks = all_ranks
    for rank, stack in enumerate(stacks):
        stack_frames = stack.split(";")
        trie.insert(stack_frames, rank)
    return trie

def main():
    # 示例输入：每行表示一个rank的堆栈信息
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
            f.write(f"{stack}\n")

if __name__ == "__main__":
    main()