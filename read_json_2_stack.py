import json

def parse_json_to_stacks(json_file, output_file):
    # 读取 JSON 文件
    with open(json_file, 'r') as f:
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
    
    # 写入输出文件
    with open(output_file, 'w') as f:
        for stack in stacks:
            f.write(f"{stack} 1\n")

if __name__ == "__main__":
    json_file = "output.json"  # 输入的 JSON 文件
    output_file = "stacks.txt"  # 输出的堆栈文件
    parse_json_to_stacks(json_file, output_file)
    print(f"堆栈文件已生成: {output_file}")