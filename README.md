# collect_stack_draw
收集集群中的堆栈信息,绘制火焰图🔥

[原始单rank stack](./pics/stack%202025-05-26%2010-37-55.png)

# Step 1
分布式收集集群中各个节点的堆栈信息

# Step 2
绘制火焰图

## Verison 0.1
```bash
python read_json_2_stack.py
/home/yang/Downloads/FlameGraph-1.0/flamegraph.pl stacks.txt > flamegraph.svg
```

## Version 0.2
```bash
❯ python framegraph_generator.py
2025-05-26 10:31:24,273 - __main__ - INFO - 执行命令: /home/yang/Downloads/FlameGraph-1.0/flamegraph.pl ./tmp/stacks.txt
2025-05-26 10:31:24,285 - __main__ - INFO - 火焰图已生成: ./tmp/flamegraph.svg
```

[V0_2 单rank stack](./pics/V0_2%202025-05-26%2010-40-15.png)
