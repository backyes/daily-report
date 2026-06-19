# Agentic AI 内存层级全景分析（示例）

> 本文是 cxl-agentic-hbf-nand skill 的输出示例。
> 展示如何将四种 Agentic AI 工作负载映射到多级异构内存层级。
> 
> **注意**：本文为模板示例，部分数字为占位符，实际使用时需填充真实数据。

---

## 0. 元数据

| 属性 | 内容 |
|------|------|
| **报告标题** | Agentic AI 推理的异构内存层级全景分析 |
| **分析日期** | 2026-06-19 |
| **分析范围** | Prefill + Decode Offloading + Engram + Embedding 四种工作负载 |
| **关键信源** | [待补充 T0/T1 信源] |
| **报告版本** | v1.0 (示例) |

---

## 1. TL;DR

**问题**：Agentic AI 推理引入的多轮 Tool Calling、长上下文、记忆模块（Engram）使内存访问模式从"可预测的 Prefill-Decode 两阶段"变为"混沌化的多工作负载混合"，传统 HBM 独占方案在容量/成本维度崩溃。

**方案**：构建 HBM → CXL-DDR → HBF → NAND 四级存储层级，按工作负载特征（IOPS/带宽/延迟/成本/耐久度 5 指标）将数据静态/动态地映射到最优介质。

**结论**：CXL-DDR + HBF 的组合可将单 GPU 可服务的上下文长度从 ~128K 扩展到 1M+ tokens，同时将单位 token 的存储成本降低 3-5×。Marvell Structera 三件套（S/X/A）是 2026 年唯一提供 CXL 全栈方案的供应商。

---

## 2. 工作负载特征量化

### 2.1 四种工作负载的 5 指标矩阵

| 工作负载 | 访问粒度 | 峰值随机 IOPS | 有效带宽需求 | 延迟敏感度 | 容量需求 | 单位成本目标 | 耐久度/WAF |
|---------|---------|-------------|-------------|-----------|---------|------------|-----------|
| **Prefill** | 64KB-MB 顺序 | ~0 (顺序流) | >1 TB/s | 低 (流水线隐藏) | 与模型参数正比 (~100GB) | ~$10/GB (HBM) | 无写入 |
| **Decode 热 KV** | 4KB 随机 | 10-50M | 100-500 GB/s | 极高 (<200ns 关键路径) | 100-500GB | ~$10/GB (HBM) | 零限制 |
| **Decode 冷 KV** | 4KB 随机 | 1-10M | 50-200 GB/s | 中 (可预取, <1μs) | 500GB-2TB | ~$3/GB (CXL-DDR) | 零限制 |
| **Engram** | 1-4KB 稀疏 | 100K-1M | 10-50 GB/s | 低 (前瞻预取) | 100GB-1TB | ~$1/GB (HBF) | 无限 (只读) |
| **Embedding 热** | 64-256B | 100M+ | 10-30% 有效 | 极高 (P99 <100μs) | 100-500GB | ~$10/GB (HBM Buffer) | SRAM 吸收 |
| **Embedding 冷** | 64-256B | 1-10M | 5-15% 有效 | 中 (P99 <1ms) | 1-10TB+ | ~$0.1/GB (NAND) | ~3K PE × WAF |

### 2.2 关键洞察

1. **Prefill 不需要变**：HBM 是唯一选择，未来也是
2. **Decode 需要分层**：热 KV 留 HBM，冷 KV 迁移到 CXL-DDR/HBF
3. **Engram 是全新需求**：只读 + 成本优先 → HBF 是最佳匹配
4. **Embedding 的 P99 是硬骨头**：需要 SRAM Hit-Buffer + NAND 冷存储

---

## 3. CXL 协议栈与异构拓扑

### 3.1 推荐拓扑：单级 CXL Switch + 混合介质后端

```
┌─────────────────────────────────────────────────────┐
│                    GPU (HBM)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │ Hot KV   │  │ Prefill  │  │ Embedding│          │
│  │ Cache    │  │ Weights  │  │ Hot Buf  │          │
│  └──────────┘  └──────────┘  └──────────┘          │
│       │                                        │
│  NVLink/CXL Bridge                             │
└───────┼────────────────────────────────────────┘
        │
   ┌────▼────────────────────────────────┐
   │     CXL 3.0 Switch                  │
   │  (Marvell Structera S / Astera Leo)  │
   │  260-lane / 4 TB/s / <460ns         │
   └────┬──────────┬──────────┬──────────┘
        │          │          │
   ┌────▼───┐ ┌───▼────┐ ┌──▼────────┐
   │ CXL-DDR│ │ HBF    │ │ Near-Mem  │
   │ Cold KV│ │ Engram │ │ Compute   │
   │ 4-6TB  │ │ 2-4TB  │ │ (ARM V2)  │
   │Struct X│ │ SK H³  │ │ Struct A  │
   └────────┘ └────────┘ └───────────┘
```

---

## 4. HBF/NAND 存储层级

### 4.1 HBF 的核心价值

HBF 不是"更快的 SSD"，而是"更便宜的伪 DRAM"：
- 读延迟 ~10μs vs NAND ~100μs（10× 改善）
- 顺序读带宽 ~10-20GB/s vs NAND ~1-2GB/s（10× 改善）
- 单位成本 ~$1-3/GB vs HBM ~$10-15/GB（5-10× 便宜）

对于 Engram（只读、可预取、低 IOPS）和 Decode 冷 KV（非延迟关键路径），HBF 是性价比最优解。

---

## 5. 学术论文映射

| 论文 | 会议 | 核心贡献 | 对应 5 指标 |
|------|------|---------|------------|
| [待补充：KV 量化论文] | MLSys'26 | 2-bit KV 量化，容量减少 8× | Cost, BW |
| [待补充：分层迁移论文] | ISCA'25 | 贝叶斯预测复用，命中率 92% | Latency, IOPS |
| [待补充：PIM 卸载论文] | HPCA'26 | CXL 控制器侧 KV 解压 | BW, IOPS |

---

## 6. 2026 硬件方案

| 产品 | 角色 | 关键规格 | 量产 |
|------|------|---------|------|
| Marvell Structera S | CXL Switch | 260-lane / 4TB/s / <460ns | 2026 |
| Marvell Structera X | 内存扩展 | 4-6TB DDR4/DDR5 | 2026 |
| Marvell Structera A | 近存计算 | ARM V2 / KV 压缩卸载 | 2026 |
| SK Hynix H³ | Hybrid Stack | HBM + HBF | 2026 样品 |
| NVIDIA Rubin ICMS | 集成 Switch | NVLink + CXL | 2026-2027 |

---

## 7. 横向主线

1. **从"HBM 独占"到"多级存储协同"** — Decode 冷数据 + Engram 驱动 HBF/CXL 需求
2. **CXL 从带宽扩展到智能内存网络** — Switch + 近存计算使 CXL 成为独立内存平面
3. **Flash 在 AI 推理中的角色升维** — HBF 填补 DRAM-NAND 之间的"黄金中层"

---

## 8. 局限与开放问题

- HBF 的写延迟（~100μs）仍是读延迟的 10×，不适合写密集型场景
- CXL 3.0 Switch 的生态成熟度待验证（目前仅 Marvell/Astera 有量产产品）
- 预测预取算法的精度直接影响 HBF/NAND 的可行性（命中率 <80% 时延迟惩罚不可接受）

---

## 9. 一句话点评

> Agentic AI 的内存层级变革不是"要不要分层"的问题，而是"分几层、每层用什么介质、谁来提供控制器"的问题——Marvell Structera 在 2026 年用 S+X+A 三件套给出了目前最完整的答案，但 SK Hynix H³ 的 HBM+HBF Hybrid Stack 才是真正的"介质层范式变化"。
