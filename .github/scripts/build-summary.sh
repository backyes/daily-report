#!/usr/bin/env bash
# build-summary.sh
# ─────────────────────────────────────────────────────────────────────────────
# 选出"本次 push 想要通知的那份日报"，把它的标题 + 速览表 + 前若干段提取出来，
# 同时产出 markdown 摘要 (email_body.md) 和 mobile/邮件友好的 HTML (email_body.html)，
# 把邮件主题通过 GITHUB_OUTPUT 暴露给上游 step。
#
# 选取规则（优先级递减）：
#   1. workflow_dispatch 手动触发且填了 target_file → 直接用
#   2. push 事件：在本次 commit 改动的文件中找 examples/*.md，取文件名按字典序最大的
#      （日报文件命名形如 tech_frontier_daily_YYYYMMDD.md，字典序==时间序）
#   3. 上面都没命中：fallback 取 examples/ 下字典序最大的 .md
#   4. 仍找不到：把 has_summary 设为 false，工作流会跳过发送
#
# 输出（写到 $GITHUB_OUTPUT）：
#   has_summary  true / false
#   subject      邮件标题
#   target_file  实际选中的文件路径（用于日志）
#   body_md      生成的 markdown 摘要路径
#   body_html    生成的 HTML 摘要路径（手机/邮件友好）
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

OUT="${GITHUB_OUTPUT:-/dev/stderr}"
BODY_MD="email_body.md"
BODY_HTML="email_body.html"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RENDERER="${SCRIPT_DIR}/md_to_mobile_html.py"

emit() { echo "$1=$2" >> "$OUT"; }

# 1. 决定 TARGET ----------------------------------------------------------------
TARGET=""

if [[ "${GH_EVENT_NAME:-}" == "workflow_dispatch" && -n "${GH_TARGET_FILE:-}" ]]; then
  TARGET="${GH_TARGET_FILE}"
  echo "[build-summary] using manual target: $TARGET"
fi

if [[ -z "$TARGET" ]]; then
  CHANGED=$(git diff --name-only HEAD~1 HEAD -- 'examples/*.md' 2>/dev/null | sort | tail -n 1 || true)
  if [[ -n "$CHANGED" ]]; then
    TARGET="$CHANGED"
    echo "[build-summary] picked from diff: $TARGET"
  fi
fi

if [[ -z "$TARGET" ]]; then
  TARGET=$(ls examples/*.md 2>/dev/null | sort | tail -n 1 || true)
  if [[ -n "$TARGET" ]]; then
    echo "[build-summary] fallback to newest file in examples/: $TARGET"
  fi
fi

if [[ -z "$TARGET" || ! -f "$TARGET" ]]; then
  echo "[build-summary] no target daily-report file found; skipping mail." >&2
  emit has_summary false
  emit subject ""
  emit target_file ""
  emit body_md ""
  emit body_html ""
  exit 0
fi

emit target_file "$TARGET"

# 2. 解析标题 + 日期 ------------------------------------------------------------
TITLE=$(grep -m1 '^# ' "$TARGET" | sed 's/^#\s*//' || true)
[[ -z "$TITLE" ]] && TITLE="Daily Report"

DATE_LINE=$(grep -m1 -E '^\*\*日期[:：]' "$TARGET" | sed 's/\*\*//g' || true)
if [[ -z "$DATE_LINE" ]]; then
  STAMP=$(echo "$TARGET" | grep -oE '[0-9]{8}' | head -n1 || true)
  if [[ -n "$STAMP" ]]; then
    DATE_LINE="日期：${STAMP:0:4}-${STAMP:4:2}-${STAMP:6:2}"
  fi
fi

SUBJECT="📰 ${TITLE} — ${DATE_LINE:-update}"
emit subject "$SUBJECT"

# 3. 构造 markdown 摘要正文 ----------------------------------------------------
# 优先抽取 "## 📰 本期速览" 整节，否则取前 60 行
SUMMARY=$(awk '
  /^## .*本期速览/ {flag=1; print; next}
  flag && /^## / {flag=0}
  flag && /^---[[:space:]]*$/ {flag=0}
  flag {print}
' "$TARGET")

if [[ -z "${SUMMARY// /}" ]]; then
  SUMMARY=$(head -n 60 "$TARGET")
fi

REPO_URL="https://github.com/${GH_REPO}"
COMMIT_URL="${REPO_URL}/commit/${GH_SHA}"
FILE_URL="${REPO_URL}/blob/${GH_SHA}/${TARGET}"
SHORT_SHA="${GH_SHA:0:7}"
COMMIT_MSG_FIRST=$(printf '%s' "${GH_COMMIT_MSG:-}" | head -n1)

{
  echo "# ${TITLE}"
  echo
  if [[ -n "${DATE_LINE:-}" ]]; then echo "**${DATE_LINE}**"; echo; fi
  echo "> 📂 来源文件：[\`${TARGET}\`](${FILE_URL})  "
  echo "> 🔁 触发提交：[\`${SHORT_SHA}\`](${COMMIT_URL}) by **${GH_ACTOR:-unknown}**  "
  if [[ -n "$COMMIT_MSG_FIRST" ]]; then
    echo "> 💬 ${COMMIT_MSG_FIRST}"
  fi
  echo
  echo "---"
  echo
  echo "$SUMMARY"
  echo
  echo "---"
  echo
  echo "🔗 完整日报：${FILE_URL}"
  echo "🏠 仓库：${REPO_URL}"
} > "$BODY_MD"

echo "[build-summary] wrote $BODY_MD ($(wc -l < "$BODY_MD") lines)"

# 4. 渲染 HTML 版本（手机 / 邮件客户端友好） ----------------------------------
# 调用 vendored 的 mobile-html renderer。CI 上需要 python-markdown，
# 工作流里已经安装。失败时降级为只发 markdown，不让 push 报错。
if [[ -x "$RENDERER" || -f "$RENDERER" ]]; then
  META_HTML="📂 来源：<a href=\"${FILE_URL}\"><code>${TARGET}</code></a> · 🔁 提交：<a href=\"${COMMIT_URL}\"><code>${SHORT_SHA}</code></a> by <strong>${GH_ACTOR:-unknown}</strong>"
  FOOTER_HTML="🔗 <a href=\"${FILE_URL}\">完整日报</a> · 🏠 <a href=\"${REPO_URL}\">${GH_REPO}</a>"
  if python3 "$RENDERER" "$BODY_MD" -o "$BODY_HTML" \
       --title "$SUBJECT" \
       --meta "$META_HTML" \
       --footer "$FOOTER_HTML"; then
    echo "[build-summary] wrote $BODY_HTML ($(wc -c < "$BODY_HTML") bytes)"
    emit body_html "$BODY_HTML"
  else
    echo "[build-summary] HTML render failed, falling back to markdown-only" >&2
    emit body_html ""
  fi
else
  echo "[build-summary] renderer not found at $RENDERER, skipping HTML" >&2
  emit body_html ""
fi

emit body_md "$BODY_MD"
emit has_summary true
