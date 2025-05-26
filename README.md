# collect_stack_draw
收集集群中的堆栈信息,绘制火焰图🔥

# Step 1
分布式收集集群中各个节点的堆栈信息

# Step 2
绘制火焰图

```bash
python read_json_2_stack.py
/home/yang/Downloads/FlameGraph-1.0/flamegraph.pl stacks.txt > flamegraph.svg
```
