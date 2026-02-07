---
title: "vLLM中的并行技术：张量并行(TP)与流水线并行(PP)解析"
date: 2025-02-10 18:43:28 +0800
---

{% raw %}
今天看到有人用vLLM 0.7.1部署r1，TP size 8，PP size 2，忽然想到平时都是用TP，基本上没有用PP，也看到科学空间群里的有人调研使用的命令。然后在公众号，知乎查到的关于TP和PP的说法很多都是错误的，使用perplexity.ai才在reddit和个人网站搜到一些有用的资料，备份复习重温一下吧。

![image-20250210182840768](/images/20250210-vllm-tp-pp-parallelism-explained/image-20250210182840768.png)

<!--more-->
---
![image-20250210183228905](/images/20250210-vllm-tp-pp-parallelism-explained/image-20250210183228905.png)

------

本文介绍两种tp和pp并行技术——**张量并行（Tensor Parallelism, TP）**和**流水线并行（Pipeline Parallelism, PP）**的实现原理与应用场景。


## 一、理解张量并行（TP）

当单个GPU内存不足以承载整个模型时，**张量并行**通过将模型分片部署在多个GPU上协同工作。这种方法通过对张量运算进行分解，实现了横向扩展能力。

### 关键技术点

1. **分片检查点优化**
   使用官方提供的[分片转换脚本](https://docs.vllm.ai/en/latest/getting_started/examples/save_sharded_state.html)可以将传统模型检查点转换为分片格式。虽然初始转换耗时较长，但后续加载时间可缩短80%以上。

2. **动态资源配置**

   ```properties
   1# 单节点8卡配置示例
   2tensor_parallel_size = 8
   3pipeline_parallel_size = 1
   4
   5# 两节点各8卡的配置
   6tensor_parallel_size = 8  # 每节点GPU数量
   7pipeline_parallel_size = 2  # 总节点数
   ```

3. **性能预估指标**
   vLLM运行时输出的GPU blocks: 790指标反映显存利用率，每个块可处理16个token。实际吞吐量可通过公式换算：

   ```
   最大处理token数 = GPU块数 × 16
   ```

------

## 二、实施流水线并行（PP）

当模型规模突破单节点容量时，**流水线并行**通过纵向分层的方式，将模型的不同stage部署在不同计算节点上。这种架构类似于工厂的装配流水线，各节点接力完成计算任务。



### 实施步骤要点

1. 层级切分策略

   - 按模型层（Layer）进行分段
   - 确保每段可在节点内完成TP部署
   - 考虑层间通信带宽需求

2. 典型配置示例

   ```properties
   1# 跨两节点部署配置
   
   2pipeline_parallel_size = 2  # 节点总数
   
   3tensor_parallel_size = 8   # 每节点GPU数
   ```

3. 性能平衡技巧

   - **微流水线（Micro-batching）**：通过批处理优化利用率
   - **气泡控制**：协调各stage计算时间差
   - **梯度累积**：平衡显存与吞吐量需求

------

## 三、技术选型指南

两种技术的核心区别在于资源调度维度：

| 维度         | 张量并行(TP)      | 流水线并行(PP)        |
| ------------ | ----------------- | --------------------- |
| 资源分配维度 | 单节点内GPU间协同 | 跨节点协同            |
| 通信频率     | 高频（逐层通信）  | 低频（阶段边界通信）  |
| 最佳适用场景 | 百亿级参数模型    | 千亿级参数超大模型    |
| 典型硬件配置 | 8卡A100节点       | 多台8卡A100服务器集群 |

**组合策略建议**：对于超大模型训练，推荐采用混合并行方案——在节点内使用TP进行细粒度并行，节点间使用PP实现粗粒度扩展。例如使用16台配备8卡A100的服务器时，可以配置为：

```properties
1TP_size = 8   # 单节点全卡参与
2PP_size = 16  # 跨16个节点
```

## 参考资料

1. [Vllm Tensor Parallelism Vs Pipeline Parallelism | Restackio](https://www.restack.io/p/vllm-answer-tensor-parallelism-vs-pipeline-parallelism-cat-ai)

2. [vLLM 0.7.1 DeepSeek R1 PP 部署踩坑指南 - 知乎](https://zhuanlan.zhihu.com/p/21064432691)

3. https://www.perplexity.ai/search/what-is-the-difference-between-7_RgadGDQq._p4mjqSDszg
{% endraw %}
