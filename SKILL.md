---
name: daily-report
description: 半导体 / AI Infra / AI Compiler / 互联网络 / 半导体股票 / AI 软件栈 / AI 算法 / AI 应用 / 数据中心电力 / OSS 早期信号
  十大领域的"前沿技术情报日报"生成器。当用户提到"日报"、"daily report"、"AI Infra 日报"、"AI Compiler 日报"、
  "AI 软件栈日报"、"AI 算法日报"、"AI 应用日报"、"芯片日报"、"半导体日报"、"互联网络日报"、"超节点日报"、
  "半导体股票日报"、"数据中心电力日报"、"AI 算力链 signal"、"GitHub 早期信号"、"科技前沿日报"时使用此技能。
  所有模板都强调"取证依据 + 链接出处 + 量化数字 + 战略判断"，输出面向 AI Infra 架构师 / 研发负责人 / 投研团队 / Agent 产品 PM。
---

# Daily Report Skill (前沿技术情报日报生成器)

把仓库 https://github.com/backyes/daily-report 里的多份长 prompt 抽象成一个可复用 skill。
每个模板都强调"不是新闻汇总、是战略判断 + 必须给出取证链接 + 必须带量化数字"。

## 十个内置主题

| topic | 模板文件 | 适用领域 | 受众 |
|---|---|---|---|
| `ai_compiler` | prompts/ai_compiler.md | XLA/TVM/Triton/MLIR/编译器栈/Kernel 生成 | 编译器 / Kernel 工程师 |
| `ai_infra` | prompts/ai_infra.md | HBM/CoWoS/CXL/NVLink/UALink/UEC 全栈 | AI Infra 架构师 |
| `ai_software` | prompts/ai_software.md | vLLM / SGLang / TRT-LLM / FlashAttention / torch.compile / Mooncake | 推理引擎 / 训练 SRE |
| `ai_algorithm` | prompts/ai_algorithm.md | MoE / MLA / SSM / DPO / GRPO / 投机解码 / inference-time scaling | 模型团队 / 算法研究员 |
| `ai_application` | prompts/ai_application.md | Claude Code / Cursor / Devin / MCP / Computer Use / 垂类 Agent | Agent PM / 应用层创业者 |
| `chip_bus` | prompts/chip_bus.md | 半导体五大阵营 + 二级市场 + 供应链 | 二级市场研究 / 产业分析 |
| `interconnect` | prompts/interconnect.md | 超节点 / Scale-up&out / Switch ASIC / CPO | 网络芯片 / 互联系统 |
| `datacenter_power` | prompts/datacenter_power.md | Gigawatt 园区 / PPA / SMR / 液冷 / capex 跟踪 | 基建投资 / 数据中心运营 |
| `stock_signal` | prompts/stock_signal.md | 美/港/韩/台股半导体 + AI 算力链事件驱动 | 量化研究 / 事件策略 |
| `oss_signal` | prompts/oss_signal.md | GitHub trending + HF + arxiv + X + Reddit + Substack 早期信号 | 研究/工程 leader |

外加 `综合` 主题：把上面任意 N 个并成一份"科技前沿日报"，参考
`examples/tech_frontier_daily_20260616.md` 的格式。

## 信源分级（写报告前先想清楚走哪条 lane）

| Tier | 信源 | 特征 | 用法 |
|---|---|---|---|
| **T0 一手原文** | GitHub commits/PR、arxiv、SEC/FERC filing、官方 blog、官方 release notes | 时间戳准 / 不可否认 | 必须作为"取证依据" |
| **T1 独立深度** | SemiAnalysis、Next Platform、The Information、Stratechery、Interconnects | 含独立分析 / 数字 | 用于"战略判断"段 |
| **T2 高信噪比 X / Substack** | Dylan Patel、Karpathy、@_lewtun、@nrehiew_、@dr_cintas、Sebastian Raschka、ThursdAI | 早期信号 + 圈内对话 | 用于 oss_signal 的早期信号 |
| **T3 社区** | r/LocalLLaMA、r/MachineLearning、HN、Discord 截图 | 群体反应 / sanity check | 用于"二次验证" |
| **T4 中文媒体** | 36Kr、量子位、机器之心、智东西、芯东西 | 国内动态 + 翻译 | 仅作为补充，不能作为唯一来源 |

**Tier 越低、越需要交叉验证。** 一条只在 T3/T4 出现而 T0/T1 全无的信号，标注为"未交叉验证"或丢弃。

## 触发与流程

用户说出关键词后：

1. **选模板** — 没指定就让用户在十个 topic 里选；说"综合日报"就走综合流程。
2. **拉取信源** — 用 WebSearch / WebFetch 检索最近 24h（"过去 24 小时" / "过去 7 天"）的：
   - **T0**：GitHub Releases、HF model 卡、arxiv、官方 blog、SEC filings
   - **T1**：SemiAnalysis、Next Platform、AnandTech、Semiconductor Engineering、Stratechery、The Information
   - **T2**：上面 T2 列的账号最新动态
   - **T3**：当周 r/LocalLLaMA top、HN AI top
   - 每条信号必须带可点击 URL + 量化数字（吞吐 / GW / $B / star / TPS / accuracy 等），二者缺一就丢弃。
3. **填充模板** — 严格按 prompt 文件里的章节结构输出，不要省略字段。
4. **多源交叉验证（Triangulation）** — 重大趋势必须 ≥ 2 个独立信源印证，且至少有 1 个是 T0/T1。
5. **附录原文链接** — 文末统一一个"信源附录"段，列每条 URL 的标题与摘要。
6. **写文件（双格式）** — 默认写到 `~/work/claude_workspace/daily_report/output/<topic>_<YYYYMMDD>.{md,html}`。
   - 综合日报命名为 `tech_frontier_daily_<YYYYMMDD>.md`。
   - 已存在同名就追加 `_v2`，不要覆盖。
   - **md 写完后必须立刻渲染同名 .html**——给用户的手机阅读 / 邮件客户端用：
     ```bash
     python3 ~/.claude/skills/mobile-html-render/md_to_mobile_html.py \
         <output_path>.md -o <output_path>.html
     ```
     这一步走 [`mobile-html-render`](file:///Users/backyes/.claude/skills/mobile-html-render/SKILL.md) skill：
     单文件、内联 CSS、视口适配、表格在窄屏横向滚、支持暗色模式。
     如果用户**显式说"只要 markdown / 不要 html"**，可跳过；否则一律双发。
   - 写完后在对话里同时给出两个路径，并提示用户 html 适合手机 / 邮件阅读。

## Skill 技巧（写出高质量日报的关键 trick）

### 1. 数字优先
"性能提升 3.3 倍" 比 "性能显著提升" 强 10 倍。没数字的信号丢弃，或注明 "无量化数据"。

### 2. 三段式判断
每条信号写：
- 技术本质（用什么新机制解决什么旧瓶颈）
- 影响对象（谁会立即受益 / 受冲击）
- 战略价值（是补丁、范式、还是噪声）

### 3. 避免双重计数
同一新闻被不同媒体转发 ≠ 多源印证。要追到 **不同立场** 的独立分析。

### 4. 早期信号追"谁在转推"
GitHub repo / HF model 在 trending 之前，往往先被 5-10 个圈内大 V 转推。追溯转推链路是 oss_signal 的核心动作。

### 5. 保留模板里的 emoji 格式
速览表、🪐🧬 等是用户已习惯的呈现风格，不要去掉。

### 6. 日期处理
从 `currentDate` system reminder 读今天日期，不要凭空猜。

### 7. 去新闻化
不要做新闻聚合。一个老技术连续 5 天上头条但没新数字，就跳过。

### 8. 6-24 月视角
所有 prompt 都强调中长期趋势，不写当天股价波动叙事（除 stock_signal）。

### 9. 公开度标注
对模型 / 工具，标注：公开权重 + 公开代码 + 论文（可复现） / 仅论文（待复现） / 闭源（仅作判断信号）。

### 10. 注意"安静的大事"
有时最重要的信号是 "本周 NVIDIA 没发任何新东西" / "Anthropic API 价格悄悄变了"。显式扫描 absent signal。

### 11. 移动 / 邮件友好的 HTML 产出
日报最终消费场景大概率是手机阅读 / Gmail 推送。markdown 在 GitHub 上漂亮，但在邮件客户端会被压缩 + 表格爆栏。
统一用 `mobile-html-render` skill 渲染——单文件 HTML、视口已设、表格窄屏自动横向滚、暗色模式跟随系统：

```bash
python3 ~/.claude/skills/mobile-html-render/md_to_mobile_html.py <md> -o <html>
```

不要自己手写 HTML 模板；不要试图在 markdown 里嵌 `<style>` 来做样式（GitHub 会清掉）。
所有样式都封装在 mobile-html-render 里，统一升级。

## 综合日报推荐组合

不要一次跑全 10 个，会噪声过载。推荐组合：

- **硬件向**：ai_infra + chip_bus + interconnect + datacenter_power
- **软件向**：ai_software + ai_algorithm + ai_compiler + oss_signal
- **应用向**：ai_application + ai_algorithm + oss_signal
- **投研向**：stock_signal + chip_bus + datacenter_power + ai_infra

## 使用示例

```
用户：跑一下今天的 AI Compiler 日报
→ 读 prompts/ai_compiler.md
→ WebSearch 获取过去 24h 信号（T0/T1/T2 每层至少 1 条）
→ 输出到 output/ai_compiler_<今天>.md
→ 调用 mobile-html-render → output/ai_compiler_<今天>.html
→ 在对话中同时给出两个文件路径（md 给 GitHub / 编辑、html 给手机 / 邮件）
```

```
用户：综合软件向日报
→ ai_software + ai_algorithm + ai_compiler + oss_signal 4 个并行（推荐 ultracode 模式）
→ 合成一份 tech_frontier_daily_<今天>.md
```

## 关键约束（必须遵守）

- **取证优先**：没链接就不写，宁缺毋滥。
- **数字优先**：没数字就不写，或显式标注 "无量化数据"。
- **去新闻化**：每条信号要带"技术本质 / 影响对象 / 战略价值"三段式判断。
- **6-24 个月视角**：所有 prompt 都强调中长期趋势，不写当天股价波动叙事（除 stock_signal）。
- **保留模板里的 emoji 格式**（速览表、🪐🧬 等）。
- **日期处理**：从 `currentDate` system reminder 读今天日期，不要凭空猜。
- **多源交叉**：重大判断 ≥ 2 个独立信源，至少 1 个 T0/T1。
- **双格式产出**：除非用户显式拒绝，每份日报都同时产出 `.md` + `.html`（用 `mobile-html-render` skill），html 是给手机阅读 / 邮件推送用的。

## 目录结构

```
~/.claude/skills/daily-report/
├── SKILL.md                              # 本文件
├── prompts/
│   ├── ai_compiler.md
│   ├── ai_infra.md
│   ├── ai_software.md
│   ├── ai_algorithm.md
│   ├── ai_application.md
│   ├── chip_bus.md
│   ├── interconnect.md
│   ├── datacenter_power.md
│   ├── stock_signal.md
│   └── oss_signal.md
└── examples/
    └── tech_frontier_daily_20260616.md   # 综合日报参考样式
```

## 可选：升级为 multi-agent 工作流

综合日报有多个独立主题，天然适合 fan-out。在用户显式开启 ultracode 或要求 "multi-agent / 用 workflow" 时，
可以一次启 N 个 Explore subagent 各自抓一个主题再合并。否则串行跑，避免高 token 消耗。
