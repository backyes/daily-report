---
name: daily-report
description: 半导体 / AI Infra / AI Compiler / 互联网络 / 半导体股票 五大领域的"前沿技术情报日报"生成器。
  当用户提到"日报"、"daily report"、"AI Infra 日报"、"AI Compiler 日报"、"芯片日报"、"半导体日报"、
  "互联网络日报"、"超节点日报"、"半导体股票日报"、"AI 算力链 signal"、"科技前沿日报"时使用此技能。
  五个 prompt 模板都强调"取证依据 + 链接出处 + 战略判断"，输出面向 AI Infra 架构师 / 投研团队。
---

# Daily Report Skill (前沿技术情报日报生成器)

把仓库 https://github.com/backyes/daily-report 里五份长 prompt 抽象成一个可复用 skill。
每个模板都强调"不是新闻汇总、是战略判断 + 必须给出取证链接"。

## 五个内置主题

| topic | 模板文件 | 适用 |
|---|---|---|
| `ai_compiler` | prompts/ai_compiler.md | XLA/TVM/Triton/MLIR/编译器栈/Kernel 生成 |
| `ai_infra` | prompts/ai_infra.md | HBM/CoWoS/CXL/NVLink/UALink/UEC 全栈 |
| `chip_bus` | prompts/chip_bus.md | 半导体五大阵营 + 二级市场 + 供应链 |
| `interconnect` | prompts/interconnect.md | 超节点 / Scale-up&out / Switch ASIC / CPO |
| `stock_signal` | prompts/stock_signal.md | 美/港/韩/台股半导体 + AI 算力链事件驱动 |

外加 `综合` 主题：把上面五份并成一份"科技前沿日报"，参考 `examples/科技前沿日报_20260616.md` 的格式。

## 触发与流程

用户说出关键词后：

1. **选模板** — 没指定就让用户在五个 topic 里选；说"综合日报"就走综合流程。
2. **拉取信源** — 用 WebSearch / WebFetch 检索最近 24h（"过去 24 小时" / "过去 7 天"）的：
   - 顶会/arXiv/Hot Chips/MLSys/ISCA/HPCA 等
   - SemiAnalysis、Next Platform、AnandTech、Semiconductor Engineering
   - NVIDIA / Google / AMD / TSMC / Samsung / SK Hynix / Anthropic / OpenAI / DeepSeek 官方动态
   - 二级市场公告（适用于 stock_signal）
   每条信号必须带一个可点击 URL，否则就丢弃。
3. **填充模板** — 严格按 prompt 文件里的章节结构输出，不要省略字段（包括"今日最大技术信号 / Top 5 / 战略判断 / 行动建议"等）。
4. **附录原文链接** — 文末统一一个"信源附录"段，列每条 URL 的标题与摘要。
5. **写文件** — 默认写到 `~/work/claude_workspace/daily_report/output/<topic>_<YYYYMMDD>.md`。
   - 综合日报命名为 `科技前沿日报_<YYYYMMDD>.md`。
   - 已存在同名就追加 `_v2`，不要覆盖。

## 使用示例

```
用户：跑一下今天的 AI Compiler 日报
→ 读 prompts/ai_compiler.md
→ WebSearch 获取过去 24h 信号
→ 输出到 output/ai_compiler_<今天>.md
→ 在对话中给摘要 + 文件路径
```

```
用户：综合日报
→ 5 个模板并行跑（可用 Workflow，需用户先开 ultracode 或显式同意 multi-agent）
  否则就串行选 3 个最重要主题汇总
→ 输出到 output/科技前沿日报_<今天>.md
```

## 关键约束（必须遵守）

- **取证优先**：没链接就不写，宁缺毋滥。
- **去新闻化**：每条信号要带"技术本质 / 影响对象 / 产业价值"三段式判断。
- **6-24 个月视角**：所有 prompt 都强调中长期趋势，不写当天股价波动叙事（除 stock_signal）。
- **保留模板里的 emoji 格式**（速览表、🪐🧬 等）—— 这是用户已习惯的呈现风格。
- **日期处理**：从 `currentDate` system reminder 读今天日期，不要凭空猜。

## 目录结构

```
~/.claude/skills/daily-report/
├── SKILL.md                              # 本文件
├── prompts/
│   ├── ai_compiler.md
│   ├── ai_infra.md
│   ├── chip_bus.md
│   ├── interconnect.md
│   └── stock_signal.md
└── examples/
    └── tech_frontier_daily_20260616.md   # 综合日报参考样式
```

## 可选：升级为 multi-agent 工作流

综合日报有 5 个独立主题，天然适合 fan-out。在用户显式开启 ultracode 或要求 "multi-agent / 用 workflow" 时，
可以一次启 5 个 Explore subagent 各自抓一个主题再合并。否则串行跑，避免高 token 消耗。
