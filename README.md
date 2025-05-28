# collect_stack_draw
收集集群中的堆栈信息,绘制火焰图🔥

![原始单rank stack](./pics/stack%202025-05-26%2010-37-55.png)

![单rank stack](./pics/V0_2%202025-05-26%2010-40-15.png)

## 设计思路
- 1. 读取config.json文件
- 2. 读取config.json文件中的节点信息
- 3. 根据节点信息执行request collect命令
- 4. 从json数据转换成火焰图txt数据
- 5. 将生成的火焰图保存到指定目录

## 使用方法
```bash
cd src
python main.py
```