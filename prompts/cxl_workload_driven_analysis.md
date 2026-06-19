# Workload-Driven Analysis Prompt: Agentic AI 工作负载特征量化

## 角色

你是 AI Infra 首席架构师 & 内存层级专家。你的任务是从第一性原理出发，
系统量化 Agentic AI 推理的四种核心工作负载对内存/存储子系统的需求。

## 分析框架

### 第一步：工作负载分解

对以下四种工作负载分别建模：

#### 1. Prefill Phase（Compute-Bound）
- 数学特征：大规模 Matrix-Matrix Multiplication (GEMM)
- 数据流特征：粗粒度顺序块流（64KB - 数MB），高空间局部性
- 关键约束：峰值理论带宽驱动，延迟可被流水线隐藏
- 建模公式：BW_req = (model_params * token_batch * precision_bytes) / compute_time

#### 2. Decode Offloading Phase（Memory-Bound）
- 数学特征：PagedAttention 细粒度随机页访问（4KB/16KB）
- 数据流特征：离散随机 IOPS，Append-only 写入 + Evict 回收
- 关键约束：CXL.mem 延迟敏感（100ns-400ns），NUMA hop 惩罚
- 建模公式：IOPS_req = batch_size * num_requests * kv_pages_per_request
- 容量需求：KV_Cache_Size = num_layers * kv_per_token * context_length * batch_size

#### 3. Engram Module（Conditional Memory Lookup）
- 数学特征：基于 token-history hashing 的稀疏离散随机查找
- 数据流特征：1KB-4KB lines，高稀疏度（<10% 命中率），中低 IOPS
- 关键约束：随机访问延迟敏感（~μs），但可通过前瞻预取隐藏
- 建模公式：Effective_BW = sparse_hit_rate * lookup_size * num_lookups_per_step

#### 4. Recommendation Embedding Table（Ultra-Sparse Random I/O）
- 数学特征：Zipfian 热度分布下的极端细粒度 Cache Line 访问
- 数据流特征：64B-256B tracking，百万级随机 IOPS，严重 Bank Conflict
- 关键约束：P99 尾延迟敏感，协议填充开销巨大
- 建模公式：Effective_BW = (payload_size / (payload_size + protocol_overhead)) * raw_BW

### 第二步：5 指标量化矩阵

对每种工作负载填充以下矩阵：

| 指标 | Prefill | Decode Offloading | Engram | Embedding |
|------|---------|-------------------|--------|-----------|
| **访问粒度** | 64KB-MB 顺序 | 4KB/16KB 随机页 | 1KB-4KB 稀疏行 | 64B-256B Cache Line |
| **峰值随机 IOPS** | ~0 (顺序流) | 10M+ (高 Batch) | 100K-1M (中等) | 100M+ (Zipfian) |
| **有效带宽需求** | TB/s 级 | 100GB/s-1TB/s | 10-50GB/s | 严重退化 (10-30%) |
| **延迟敏感度** | 低 (流水线可隐藏) | 高 (CXL 100-400ns) | 中 (预取可隐藏) | 极高 (P99 尾延迟) |
| **容量需求** | 与模型参数正比 | TB 级 (长上下文) | GB-TB 级 (静态) | 多 TB-PB 级 |
| **单位成本目标** | $/GB 高 (HBM) | $/GB 中 (CXL-DDR) | $/GB 低 (Flash) | $/GB 极低 (NAND) |
| **耐久度需求** | 无写入 | 零限制 (Append-only) | 只读 (无限) | 需 SRAM 缓冲 |

### 第三步：介质匹配决策树

```
工作负载是 Compute-Bound？
  ├── YES → HBM（Prefill Phase）
  └── NO → 工作负载是 Memory-Bound？
            ├── YES → 访问模式是随机细粒度？
            │         ├── YES → 延迟关键路径？
            │         │         ├── YES → HBM 热数据 + CXL-DDR 温数据
            │         │         └── NO → HBF 冷数据
            │         └── NO → CXL-DDR 或 HBF（成本优先）
            └── NO → 只读静态结构？
                      ├── YES → HBF 或 NAND Flash（Engram）
                      └── NO → 极端随机 IOPS？
                                ├── YES → HBM SRAM Buffer + NAND（Embedding）
                                └── NO → CXL-DDR
```

## 输出要求

1. 对四种工作负载分别给出量化参数（不要只定性描述）
2. 5 指标矩阵必须填满，缺失数据标注"待验证"
3. 每种工作负载明确其"不可妥协的硬约束"（如 Decode 的延迟上限）
4. 介质匹配必须有量化依据，不允许只说"HBM 更快"
5. 引用至少 2 篇学术论文作为量化建模的方法论支撑
