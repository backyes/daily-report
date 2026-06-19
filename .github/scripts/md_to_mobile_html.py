#!/usr/bin/env python3
"""md_to_mobile_html.py — 把 markdown 渲染成"邮件 / 手机阅读友好"的自包含 HTML。

特点：
  - 单文件输出，所有 CSS inline 在 <style> 里（邮件客户端不挂外部资源）
  - 视口 <meta viewport>，正文 16px、行高 1.7、最大宽度 760px 居中
  - 表格在窄屏改用横向滚动 + 卡片化（避免被压成豆腐块）
  - 代码块、blockquote、>表格的 emoji 速览都渲染良好
  - 自动识别第一行 `# 标题` 作为 <title>
  - 支持 GFM 表格、围栏代码、删除线、任务列表

用法：
    python3 md_to_mobile_html.py input.md [-o output.html] [--title "..."]
    python3 md_to_mobile_html.py - < input.md > output.html

依赖：python3 + python-markdown (3.x)。已默认装在 Homebrew Python 里。
"""
from __future__ import annotations

import argparse
import html as _html
import re
import sys
from pathlib import Path

try:
    import markdown
except ImportError:
    sys.stderr.write(
        "ERROR: python-markdown 未安装。\n"
        "解决：python3 -m pip install --user markdown\n"
    )
    sys.exit(2)


# 邮件客户端兼容的 inline-CSS。说明：
#  * Gmail / Apple Mail / Outlook Web 都允许 <style>，但要避免 :root 变量（Outlook Desktop 不支持）
#  * 移动端：max-width 760px + 边距，正文 16px 起步，<table> 横向滚动
#  * 暗色模式用 prefers-color-scheme，主流移动客户端 (Apple Mail / Gmail iOS) 支持
EMAIL_CSS = """
* { box-sizing: border-box; }
body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
               "Hiragino Sans GB", "Microsoft YaHei", Roboto, "Helvetica Neue",
               Arial, sans-serif;
  font-size: 16px;
  line-height: 1.7;
  color: #1f2328;
  background: #f6f8fa;
  -webkit-text-size-adjust: 100%;
  -webkit-font-smoothing: antialiased;
}
.wrap {
  max-width: 760px;
  margin: 0 auto;
  padding: 24px 20px 48px;
  background: #ffffff;
}
h1, h2, h3, h4 {
  line-height: 1.3;
  margin: 1.6em 0 0.6em;
  font-weight: 700;
  color: #0d1117;
}
h1 { font-size: 1.55em; border-bottom: 2px solid #e6e8eb; padding-bottom: .35em; margin-top: .2em; }
h2 { font-size: 1.30em; border-bottom: 1px solid #eaecef; padding-bottom: .3em; }
h3 { font-size: 1.12em; }
h4 { font-size: 1.00em; color: #57606a; }
p, ul, ol, blockquote { margin: 0.7em 0; }
ul, ol { padding-left: 1.5em; }
li + li { margin-top: 0.25em; }
a { color: #0969da; text-decoration: underline; word-break: break-all; }
strong { color: #0d1117; }
hr { border: 0; border-top: 1px solid #e6e8eb; margin: 2em 0; }
blockquote {
  margin: 1em 0; padding: 0.6em 1em;
  border-left: 4px solid #d0d7de;
  background: #f6f8fa;
  color: #57606a;
  border-radius: 0 6px 6px 0;
}
code {
  font-family: "SFMono-Regular", "JetBrains Mono", Menlo, Consolas, monospace;
  font-size: 0.92em;
  background: #f1f3f5;
  padding: 0.15em 0.4em;
  border-radius: 4px;
  word-break: break-all;
}
pre {
  background: #0d1117;
  color: #e6edf3;
  padding: 14px 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 0.88em;
  line-height: 1.5;
}
pre code { background: transparent; color: inherit; padding: 0; }
img { max-width: 100%; height: auto; border-radius: 6px; }

/* 表格：桌面正常显示；窄屏靠横向滚动避免溢出 */
.table-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; margin: 1em 0; }
table { border-collapse: collapse; width: 100%; min-width: 480px; font-size: 0.95em; }
th, td { border: 1px solid #d0d7de; padding: 8px 10px; text-align: left; vertical-align: top; }
th { background: #f6f8fa; font-weight: 700; }
tr:nth-child(even) td { background: #fbfcfd; }

/* 顶部小元信息条 */
.meta {
  font-size: 0.88em; color: #57606a;
  background: #f6f8fa;
  border: 1px solid #e6e8eb; border-radius: 8px;
  padding: 10px 14px; margin: 1em 0 1.5em;
}
.footer {
  margin-top: 2em; padding-top: 1em;
  border-top: 1px solid #e6e8eb;
  color: #6e7781; font-size: 0.85em;
}

/* 移动端进一步收缩 */
@media (max-width: 520px) {
  .wrap { padding: 16px 14px 32px; }
  body { font-size: 15.5px; }
  h1 { font-size: 1.35em; }
  h2 { font-size: 1.20em; }
  h3 { font-size: 1.08em; }
  pre { font-size: 0.83em; }
}

/* 暗色模式（Apple Mail / Gmail iOS / 系统级），手动跟随 */
@media (prefers-color-scheme: dark) {
  body { background: #0d1117; color: #c9d1d9; }
  .wrap { background: #161b22; }
  h1, h2, h3, h4, strong { color: #f0f6fc; }
  h1 { border-bottom-color: #30363d; }
  h2 { border-bottom-color: #21262d; }
  h4 { color: #8b949e; }
  a { color: #58a6ff; }
  blockquote { background: #0d1117; border-left-color: #30363d; color: #8b949e; }
  code { background: #21262d; color: #c9d1d9; }
  pre { background: #010409; }
  hr { border-top-color: #30363d; }
  th { background: #161b22; }
  th, td { border-color: #30363d; }
  tr:nth-child(even) td { background: #0d1117; }
  .meta, .footer { background: transparent; border-color: #30363d; color: #8b949e; }
}
"""


HTML_SHELL = """\
<!DOCTYPE html>
<html lang="zh-Hans">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
  <meta name="format-detection" content="telephone=no,date=no,address=no,email=no">
  <meta name="color-scheme" content="light dark">
  <meta name="supported-color-schemes" content="light dark">
  <title>{title}</title>
  <style>{css}</style>
</head>
<body>
  <div class="wrap">
{meta_block}{body}
{footer}
  </div>
</body>
</html>
"""


def extract_title(md_text: str, fallback: str) -> str:
    for line in md_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def wrap_tables(html: str) -> str:
    """把每个 <table>...</table> 包到 <div class="table-scroll"> 里，便于窄屏横向滚。"""
    return re.sub(
        r"(<table[\s\S]*?</table>)",
        r'<div class="table-scroll">\1</div>',
        html,
    )


def build(md_text: str, title: str | None = None, meta: str | None = None,
          footer: str | None = None) -> str:
    md = markdown.Markdown(
        extensions=[
            "extra",          # tables, fenced_code, attr_list, footnotes, ...
            "sane_lists",
            "smarty",
            "toc",
        ],
        output_format="html5",
    )
    body_html = md.convert(md_text)
    body_html = wrap_tables(body_html)
    final_title = title or extract_title(md_text, "Document")
    meta_block = (
        f'<div class="meta">{meta}</div>\n' if meta else ""
    )
    footer_html = (
        f'<div class="footer">{footer}</div>' if footer else ""
    )
    return HTML_SHELL.format(
        title=_html.escape(final_title),
        css=EMAIL_CSS,
        meta_block=meta_block,
        body=body_html,
        footer=footer_html,
    )


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Render Markdown -> mobile/email-friendly HTML")
    p.add_argument("input", help='输入 .md 路径，或 "-" 表示从 stdin 读取')
    p.add_argument("-o", "--output", help="输出路径（默认与输入同名，扩展名换 .html；stdin 输入则写到 stdout）")
    p.add_argument("--title", help="HTML <title>，默认从首行 # 标题提取")
    p.add_argument("--meta", help="顶部元信息块的内联 HTML（可含链接）")
    p.add_argument("--footer", help="底部 footer 块的内联 HTML")
    args = p.parse_args(argv)

    if args.input == "-":
        md_text = sys.stdin.read()
        out_html = build(md_text, args.title, args.meta, args.footer)
        if args.output:
            Path(args.output).write_text(out_html, encoding="utf-8")
        else:
            sys.stdout.write(out_html)
        return 0

    in_path = Path(args.input)
    if not in_path.is_file():
        sys.stderr.write(f"ERROR: input file not found: {in_path}\n")
        return 1
    md_text = in_path.read_text(encoding="utf-8")
    out_html = build(md_text, args.title, args.meta, args.footer)
    out_path = Path(args.output) if args.output else in_path.with_suffix(".html")
    out_path.write_text(out_html, encoding="utf-8")
    sys.stderr.write(f"[mobile-html] wrote {out_path} ({len(out_html):,} bytes)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
