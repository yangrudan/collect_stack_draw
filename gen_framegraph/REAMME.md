# 生成火焰图过程

- 生成火焰图需要使用`perf`工具，需要先安装`perf`工具 [仓库](https://github.com/brendangregg/FlameGraph）
- 准备数据并绘制火焰图

```bash
sudo sysctl kernel.kptr_restrict=0
sudo sysctl kernel.perf_event_paranoid=-1

cd FrameGraph

sudo perf record -g -- sleep 10  # 生成perf.data
sudo perf script > out.perf  # 将 perf.data 转换为文本格式
sudo ./stackcollapse-perf.pl out.perf > out.stacks  # 生成折叠后的调用栈文件
sudo ./flamegraph.pl out.stacks > perf333.svg  # 生成火焰图
```
