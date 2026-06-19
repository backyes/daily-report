# archive/cxl_deep_analysis/

这里保留了原 `cxl-agentic-hbf-nand` skill 的资源——5 个分析向 prompts、4 个深度架构样例、
11 节报告模板、5 指标量化辅助脚本，以及完整方法论文档 `CXL_HBF_NAND_GUIDE.md`。

## 为什么归档而不是删除

2026-06-19 的重构把 cxl 内容**全部统一为日报模式**：
- `prompts/cxl_hbf_memory.md` 是新的、按日报体例写的、聚焦 **CXL DDR Memory + HBF** 主线的 prompt
- 走标准日报流程：每天 push → md+html 双产出 → GitHub Actions 触发 Gmail 邮件
- 用户只需说"CXL 日报 / HBF 日报 / CXL DDR 日报 / 内存层级日报"即可触发

但原有的"工作负载驱动 + 5 指标矩阵 + MLSys 论文映射"这套方法论仍然有价值，
特别是当某天需要从日报切换到一份"~500 行的深度架构白皮书"时，
可以参考这里的 prompts / 模板手工拼装一份，不再走 skill 自动化。

## 内容索引

```
archive/cxl_deep_analysis/
├── CXL_HBF_NAND_GUIDE.md          # 完整方法论（四大支柱 / 工作流 / 强制规则 / 已知陷阱）
├── prompts/
│   ├── cxl_workload_driven_analysis.md   # 工作负载驱动分析
│   ├── cxl_memory_hierarchy.md           # CXL 内存层级
│   ├── cxl_hbf_nand_deep_dive.md         # HBF/NAND 介质物理层
│   ├── cxl_academic_paper_mapping.md     # MLSys/ISCA/HPCA 论文映射
│   └── cxl_cross_workload_synthesis.md   # 跨工作负载横向主线
├── examples/                       # 4 份历史深度报告样例
├── templates/
│   └── analysis_report_template.md       # 11 节报告模板
└── scripts/
    └── quantify_5metrics.py              # 5 指标量化辅助脚本
```

## 不要把这些当 skill 入口

`SKILL.md` 不再引用这里的任何文件；Claude Code 也不会把它加载为 prompt。
日常使用走 `prompts/cxl_hbf_memory.md`（外层目录）即可。
