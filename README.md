# Daily Report Skill

A Claude Code skill that turns ten long prompts into one reusable
"前沿技术情报日报" (frontier-tech intelligence daily report) generator.

Mirror of `~/.claude/skills/daily-report/`.

## Topics

| topic | template | scope |
|---|---|---|
| `ai_compiler` | [prompts/ai_compiler.md](prompts/ai_compiler.md) | XLA / TVM / Triton / MLIR / kernel codegen |
| `ai_infra` | [prompts/ai_infra.md](prompts/ai_infra.md) | HBM / CoWoS / CXL / NVLink / UALink / UEC full stack |
| `ai_software` | [prompts/ai_software.md](prompts/ai_software.md) | vLLM / SGLang / TRT-LLM / FlashAttention / torch.compile / Mooncake |
| `ai_algorithm` | [prompts/ai_algorithm.md](prompts/ai_algorithm.md) | MoE / MLA / SSM / DPO / GRPO / spec-decoding / inference-time scaling |
| `ai_application` | [prompts/ai_application.md](prompts/ai_application.md) | Claude Code / Cursor / Devin / MCP / Computer Use / vertical agents |
| `chip_bus` | [prompts/chip_bus.md](prompts/chip_bus.md) | Five-camp semiconductor map + secondary market + supply chain |
| `interconnect` | [prompts/interconnect.md](prompts/interconnect.md) | Supernode / scale-up & out / switch ASIC / CPO |
| `datacenter_power` | [prompts/datacenter_power.md](prompts/datacenter_power.md) | Gigawatt campuses / PPA / SMR / liquid cooling / capex tracker |
| `stock_signal` | [prompts/stock_signal.md](prompts/stock_signal.md) | US / HK / KR / TW semis + AI compute event-driven signals |
| `oss_signal` | [prompts/oss_signal.md](prompts/oss_signal.md) | GitHub trending / HF / arxiv / X / Reddit / Substack early signals |
| `综合 (composite)` | runs N of the above → [examples/tech_frontier_daily_20260616.md](examples/tech_frontier_daily_20260616.md) | combined frontier daily |

## Source tiers (pick the lane before drafting)

| Tier | sources | usage |
|---|---|---|
| **T0** primary | GitHub commits/PR, arxiv, SEC/FERC filings, official blogs, release notes | mandatory citation per signal |
| **T1** independent depth | SemiAnalysis, Next Platform, The Information, Stratechery, Interconnects | use for "战略判断" sections |
| **T2** high-SNR X / Substack | Dylan Patel, Karpathy, @_lewtun, @nrehiew_, Sebastian Raschka, ThursdAI | feeds `oss_signal` |
| **T3** community | r/LocalLLaMA, r/MachineLearning, HN | sanity-check / second source |
| **T4** Chinese tech press | 36Kr / 量子位 / 机器之心 | supplemental only — never sole source |

A signal that exists only in T3/T4 with **no T0/T1 corroboration** must be flagged as "未交叉验证" or dropped.

## Install as a Claude Code skill

```bash
git clone https://github.com/backyes/daily-report.git ~/.claude/skills/daily-report
```

Then in Claude Code, say things like:
- "跑个 AI Compiler 日报"
- "今天的 AI 软件栈日报"
- "GitHub 早期信号日报"
- "数据中心电力日报"
- "综合日报"
- "/daily-report"

The skill description (see `SKILL.md`) lists all trigger phrases.

### Extension mode: CXL / HBF / NAND deep architecture analysis

This skill also absorbs the former `cxl-agentic-hbf-nand` skill as an **extension mode**.
When the user asks about Agentic AI memory hierarchy, KV-Cache offloading, HBF/NAND media
physics, or 5-metric quantitative matrices (IOPS / BW / latency / $/GB / endurance),
the skill switches to a ~500-line architecture report instead of a daily.

Trigger phrases include: `Agentic AI 内存`, `HBF`, `High-Bandwidth Flash`, `KV Cache 卸载`,
`PagedAttention 内存`, `Decode Offloading`, `Engram`, `5 指标量化`, `WAF`, `P/E Cycle`,
`HBM vs HBF vs CXL-DDR`, `MLSys/ISCA/HPCA 存储论文`, `SK Hynix H³`, `Samsung Memory-Semantic SSD`.

Full methodology: [`docs/CXL_HBF_NAND_GUIDE.md`](docs/CXL_HBF_NAND_GUIDE.md).

## Output

Each report is written **in two formats** to `~/work/claude_workspace/daily_report/output/`:

- `<topic>_<YYYYMMDD>.md` — Markdown source, ideal for GitHub / editors
- `<topic>_<YYYYMMDD>.html` — Self-contained mobile- & email-friendly HTML
  (inline CSS, viewport set, scrollable tables, dark-mode aware), produced via the
  [`mobile-html-render`](https://github.com/backyes/daily_report_skills/tree/main/.github/scripts/md_to_mobile_html.py)
  user-level skill at `~/.claude/skills/mobile-html-render/`.

Composite reports use `tech_frontier_daily_<YYYYMMDD>.{md,html}`.

## GitHub push → Gmail notification

Pushing a new daily report to `main` triggers
[`.github/workflows/daily-report-notify.yml`](.github/workflows/daily-report-notify.yml),
which extracts the "📰 本期速览" section, renders it as mobile-friendly HTML, and emails
it via Gmail SMTP. Setup steps and required secrets are in
[`docs/EMAIL_NOTIFY_SETUP.md`](docs/EMAIL_NOTIFY_SETUP.md).

## Hard rules baked into the skill

- **取证优先**: every signal must carry a clickable URL — drop it otherwise.
- **数字优先**: every signal must carry a quantitative metric (TPS / GW / $B / star / accuracy / TFLOPS) — drop or annotate "无量化数据".
- **三段式判断**: 技术本质 / 影响对象 / 战略价值 — for every item.
- **去新闻化**: no aggregator-style restatement; require new info or new angle.
- **6–24 month horizon**: no daily-noise narrative (except `stock_signal`).
- **Triangulation**: any major call needs ≥2 independent sources, ≥1 of which is T0/T1.
- **Date from `currentDate`**: never guess today's date.

## Recommended composite combos

Don't run all 10 in one go — too much noise. Use:

- **Hardware track**: `ai_infra + chip_bus + interconnect + datacenter_power`
- **Software track**: `ai_software + ai_algorithm + ai_compiler + oss_signal`
- **Application track**: `ai_application + ai_algorithm + oss_signal`
- **Investing track**: `stock_signal + chip_bus + datacenter_power + ai_infra`

## Layout

```
.
├── SKILL.md                              # entry point loaded by Claude Code
├── README.md
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
    └── tech_frontier_daily_20260616.md   # composite reference
```
