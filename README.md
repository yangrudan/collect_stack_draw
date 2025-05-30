# collect_stack_draw
收集集群中的堆栈信息,绘制火焰图🔥

原始数据
![原始单rank stack](./pics/stack%202025-05-26%2010-37-55.png)

区分C++ python 火焰图
![区分C++ python](./pics/V0_3%202025-05-28%2014-47-21.png)

模拟采集4进程 火焰图
![V0_5_2025-05-30_10-02-07.png](./pics/V0_5_2025-05-30_10-02-07.png)

## 设计思路
- 1. 读取config.json文件
- 2. 读取config.json文件中的节点信息
- 3. 根据节点信息执行request collect命令
- 4. 从json数据转换成火焰图txt数据
- 5. 将生成的火焰图保存到指定目录

## 使用方法
```bash
# 运行probing工具
PROBING=1 PROBING_PORT=9922 python main.py
probing 19963 config "probing.server.address='10.107.204.71:12345'"     

# 运行collect_stack_draw工具
cd src
python main.py
```

## 运行结果
```
❯ python main.py
2025-05-28 13:59:33,759 - collect_stack_info - INFO - 正在从 http://127.0.0.1:9922/apis/pythonext/callstack 获取堆栈数据
2025-05-28 13:59:33,759 - collect_stack_info - INFO - 正在从 http://127.0.0.1:9922/apis/pythonext/callstack 获取堆栈数据
2025-05-28 13:59:33,759 - collect_stack_info - INFO - 正在从 http://127.0.0.1:9922/apis/pythonext/callstack 获取堆栈数据
2025-05-28 13:59:33,759 - collect_stack_info - INFO - 正在从 http://127.0.0.1:9922/apis/pythonext/callstack 获取堆栈数据
2025-05-28 13:59:37,775 - collect_stack_info - INFO - 数据已保存到 debug_4ranks_stack_data.json
2025-05-28 13:59:37,777 - framegraph_generator - INFO - 执行命令: /home/yang/Downloads/FlameGraph-1.0/flamegraph.pl --title=Cluster stack information --colors=java --hash ./debug_4stacks.txt
2025-05-28 13:59:37,801 - framegraph_generator - INFO - 火焰图已生成: ./debug_flamegraph_4ranks.svg
2025-05-28 13:59:37,801 - __main__ - INFO - 任务完成
```

## 注意事项
- 1. 需要安装FlameGraph工具(区分python堆栈增加了额外适配)
- 2. 需要配置config.json文件中的节点信息

