# Gmail 邮件通知配置指南

每次 push 到 `main` 分支且触动 `examples/**.md` 或 `prompts/**.md` 时，
GitHub Actions 会通过 Gmail SMTP 把"最新日报的速览章节 + commit 元信息"发到指定邮箱。

工作流文件：[`.github/workflows/daily-report-notify.yml`](../.github/workflows/daily-report-notify.yml)
摘要脚本：[`.github/scripts/build-summary.sh`](../.github/scripts/build-summary.sh)

---

## 1. 在 Gmail 生成 App Password（应用专用密码）

> Gmail 从 2022 年起已禁用"低安全性应用"密码，必须用 App Password 走 SMTP。

1. 打开 <https://myaccount.google.com/security>，登录你打算用来**发信**的 Gmail 账户。
2. 在「Google 账户」→「安全」中，先开启 **两步验证 (2-Step Verification)**。未开启则看不到下一步入口。
3. 进入 <https://myaccount.google.com/apppasswords>。
4. App name 随便填，例如 `daily-report-bot`，点击 **Create**。
5. 复制弹出的 **16 位密码**（形如 `abcd efgh ijkl mnop`，复制时去掉空格也行）。
   ⚠️ 这个密码**只显示一次**，关闭弹窗就再也找不到——丢了就重新生成一个。

---

## 2. 在 GitHub 仓库配置 Secrets

仓库页 → **Settings → Secrets and variables → Actions → New repository secret**，
依次添加 **3 个 secret**：

| Secret 名                | 取值                                              | 示例                          |
| ------------------------ | ------------------------------------------------- | ----------------------------- |
| `GMAIL_USERNAME`         | 用来发信的 Gmail 完整地址                         | `your.bot@gmail.com`          |
| `GMAIL_APP_PASSWORD`     | 上一步生成的 16 位 App Password（去不去空格皆可） | `abcdefghijklmnop`            |
| `MAIL_TO`                | 收件人邮箱（多个用逗号分隔，不能有空格）          | `me@gmail.com,team@gmail.com` |

---

## 3. 验证

### 3.1 手动触发一次（推荐先做）

仓库页 → **Actions → Daily Report Email Notify → Run workflow**：

- `target_file` 填 `examples/tech_frontier_daily_20260616.md`（或留空，会自动选最新一份）
- 点 **Run workflow**

预期：

- Job 全部 ✅；
- 收件箱收到一封：
  - 标题：`📰 科技前沿日报 | Tech Frontier Daily — 日期：2026年6月16日（星期二）`
  - 正文：包含"📰 本期速览"那张领域热度表 + commit 链接 + 完整日报链接。

### 3.2 真实 push

修改 `examples/` 下任意 `.md` 后 push 到 `main`，几十秒内就会触发同样的邮件。
非 `.md` 文件、其他分支的 push、PR 都**不会**触发。

---

## 4. 工作流的选片逻辑

`build-summary.sh` 选取目标文件的优先级：

1. **手动触发** 且填了 `target_file` → 直接用；
2. **push 触发** → 在本次 commit 改动的 `examples/*.md` 中取**文件名字典序最大**的那一份
   （日报命名 `tech_frontier_daily_YYYYMMDD.md`，字典序 == 时间序）；
3. 兜底取 `examples/` 现存最新的一份；
4. 仍找不到 → 静默跳过发送，不让 push 失败。

邮件正文优先抽取 `## 📰 本期速览` 整节；如果该日报不带这节，会兜底用文件前 60 行。

---

## 5. 常见排错

| 现象                                 | 大概率原因                                                    |
| ------------------------------------ | ------------------------------------------------------------- |
| Job 红：`535-5.7.8 Username and Password not accepted` | `GMAIL_APP_PASSWORD` 填成了 Gmail 登录密码——必须是 App Password |
| Job 绿但收不到邮件                    | 收件箱垃圾邮件 / 反垃圾过滤；先检查 Gmail 的「全部邮件」标签       |
| Job 红：`Cannot read property 'username'` | 三个 secret 任一未配置或拼错名字                                |
| Job 绿但 `Send email` 步骤被 skip       | `has_summary` 为 false——本次 push 没有动到 `examples/` 里任何 md  |
| 想增加收件人                          | 在 `MAIL_TO` 里用英文逗号继续追加，无须改代码                    |

---

## 6. 关闭/暂停

- 临时关：仓库 Actions 页 → 选中 `Daily Report Email Notify` → `Disable workflow`
- 永久关：删除 `.github/workflows/daily-report-notify.yml`
- 不发邮件但保留改动监听：把 `Send email via Gmail SMTP` 那个 step 注释掉即可
