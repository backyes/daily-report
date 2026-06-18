# Daily Report Skill

A Claude Code skill that turns five long prompts into one reusable
"前沿技术情报日报" (frontier-tech intelligence daily report) generator.

Mirror of `~/.claude/skills/daily-report/`.

## Topics

| topic | template | scope |
|---|---|---|
| `ai_compiler` | [prompts/ai_compiler.md](prompts/ai_compiler.md) | XLA / TVM / Triton / MLIR / kernel codegen |
| `ai_infra` | [prompts/ai_infra.md](prompts/ai_infra.md) | HBM / CoWoS / CXL / NVLink / UALink / UEC full stack |
| `chip_bus` | [prompts/chip_bus.md](prompts/chip_bus.md) | Five-camp semiconductor map + secondary market + supply chain |
| `interconnect` | [prompts/interconnect.md](prompts/interconnect.md) | Supernode / scale-up & out / switch ASIC / CPO |
| `stock_signal` | [prompts/stock_signal.md](prompts/stock_signal.md) | US / HK / KR / TW semis + AI compute event-driven signals |
| `综合 (composite)` | runs all five → [examples/tech_frontier_daily_20260616.md](examples/tech_frontier_daily_20260616.md) | combined frontier daily |

## Install as a Claude Code skill

```bash
git clone https://github.com/backyes/daily-report.git ~/.claude/skills/daily-report
```

Then in Claude Code, say things like:
- "跑个 AI Compiler 日报"
- "今天的芯片日报"
- "综合日报"
- "/daily-report"

The skill description (see `SKILL.md`) lists all trigger phrases.

## Output

Written to `~/work/claude_workspace/daily_report/output/<topic>_<YYYYMMDD>.md`
(or `科技前沿日报_<YYYYMMDD>.md` for the composite report).

## Hard rules baked into the skill

- **取证优先**: every signal must carry a clickable URL — drop it otherwise.
- **去新闻化**: each item gets a three-part judgement (技术本质 / 影响对象 / 产业价值).
- **6–24 month horizon**: no daily-noise narrative (except `stock_signal`).
- **Date from `currentDate`**: never guess today's date.

## Layout

```
.
├── SKILL.md                              # entry point loaded by Claude Code
├── README.md
├── prompts/
│   ├── ai_compiler.md
│   ├── ai_infra.md
│   ├── chip_bus.md
│   ├── interconnect.md
│   └── stock_signal.md
└── examples/
    └── tech_frontier_daily_20260616.md   # composite reference
```
