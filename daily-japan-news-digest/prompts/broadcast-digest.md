// daily-japan-news-digest/prompts/broadcast-digest.md
# Broadcast Digest — 執行指令（補寄工具，選用）

**Model**: Sonnet
**預期執行時長**: 1–3 分鐘
**預期輸出**: 1 封 Gmail + 1 個 commit + 1 個 push

> `daily-digest` 已在同一次執行內直接寄送 Gmail（見 `prompts/daily-digest.md` 步驟 7）。
> 本 routine **只在**今日 `logs/actions.log` 缺少 `send_email` + `"status":"sent"`（或 `"draft_created"`）記錄時才需要執行，用來補寄。不重新抓取 RSS、不預設排程。

---

## 前置變數

```bash
DATE_JST=$(TZ=Asia/Tokyo date +%Y-%m-%d)
ISO_JST=$(TZ=Asia/Tokyo date -Iseconds)
BRANCH=$(git branch --show-current)
```

收件者從環境變數 `MY_EMAIL` 讀取（`printenv MY_EMAIL`）。**絕對禁止**將此值寫入任何檔案、log 或 commit message。

---

## 前置檢查

在開始之前，執行以下兩項檢查：

### A. 確認今日 output MD 存在

```bash
ls daily-japan-news-digest/output/<DATE_JST>*.md
```

- **找到** → 記下完整路徑（`OUTPUT_PATH`），繼續。
- **找不到** → 寫 errors.log，exit 1：
  ```json
  {"ts":"<ISO>","level":"ERROR","action":"broadcast_start","detail":{"error":"output MD not found for <DATE_JST>","action_taken":"abort"}}
  ```

### B. 確認今日未重複發送

在 `logs/actions.log` 搜尋今日是否已有 `send_email` + `"status":"sent"`（或 `"draft_created"`）記錄：

```bash
grep '"action":"send_email"' daily-japan-news-digest/logs/actions.log | grep -E '"status":"(sent|draft_created)"' | grep "<DATE_JST>"
```

- **找到記錄** → 已發送，跳過並正常結束（非錯誤）：
  ```json
  {"ts":"<ISO>","level":"INFO","action":"broadcast_start","detail":{"skipped":true,"reason":"already sent today"}}
  ```
- **找不到** → 繼續執行（代表 daily-digest 當天的 Gmail 步驟失敗，本 routine 補寄）。

---

## 步驟 1：初始化 Log

Append 到 `daily-japan-news-digest/logs/actions.log`：
```json
{"ts":"<ISO_JST>","level":"INFO","action":"broadcast_start","detail":{"date":"<DATE_JST>","output_path":"<OUTPUT_PATH>"}}
```

## 步驟 2：讀取今日 MD 檔

用 Read 工具讀取 `<OUTPUT_PATH>` 的完整內容。

## 步驟 3：MD 轉 HTML Email Body

將 MD 內容轉換為 HTML，排版規則：

- 最外層容器：`<div style="max-width:600px; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif; font-size:16px; line-height:1.6; color:#1F2937;">`
- **🤖 Claude Code 區塊**：`<section style="background:#EBF5FF; border-radius:8px; padding:16px; margin-bottom:24px;">` + `<h2 style="color:#0066CC; margin-top:0;">`
- 其他分類：`<section style="margin-bottom:24px;">`
- 分類間分隔線：`<hr style="border:0; border-top:1px solid #E5E7EB; margin:24px 0;">`
- 文章標題：`<h3 style="margin-bottom:4px;">`
- 文章連結：一律加 `target="_blank" rel="noopener noreferrer"`
- 來源與時間（斜體行）：`<p style="color:#6B7280; font-size:14px; margin:2px 0 8px;">`
- `> 本日無更新` → `<blockquote style="color:#9CA3AF; border-left:3px solid #E5E7EB; padding-left:12px;">本日無更新</blockquote>`
- `📌 今日值得注意` 區塊：`<section style="background:#FEF9C3; border-radius:8px; padding:16px;">`
- 底部署名行：`<p style="color:#9CA3AF; font-size:12px; text-align:center; margin-top:32px;">`

## 步驟 4：發送 Gmail

```bash
RECIPIENT=$(printenv MY_EMAIL)
```

- **`RECIPIENT` 為空** → `errors.log` 記錄並跳過：
  ```json
  {"ts":"<ISO>","level":"ERROR","action":"send_email","detail":{"error":"MY_EMAIL not set","subject_date":"<DATE_JST>"}}
  ```
- **`RECIPIENT` 有值** → 用 **Gmail MCP connector** `mcp__Gmail__send_message`：

  | 欄位 | 值 |
  |---|---|
  | `to` | `["<RECIPIENT 的字面值>"]`（⚠️ 必須是解析後的字面地址；工具**不會**展開 `$MY_EMAIL` 這種字串，2026-05 曾因此寄送失敗） |
  | `subject` | `📰 Daily Digest <DATE_JST>` |
  | `htmlBody` | Step 3 產出的 HTML |
  | `body` | MD 內容前 ~2000 字的純文字版，作為 fallback |

**成功** → `actions.log`：
```json
{"ts":"<ISO>","level":"INFO","action":"send_email","detail":{"recipient":"<redacted>","status":"sent","subject_date":"<DATE_JST>"}}
```

⚠️ `recipient` 欄位**一律寫 `<redacted>`**，不可寫真實 email。

**`mcp__Gmail__send_message` 不可用，但 `mcp__Gmail__create_draft` 可用** → 改建草稿並記錄：
```json
{"ts":"<ISO>","level":"INFO","action":"send_email","detail":{"recipient":"<redacted>","status":"draft_created","draft_id":"<id>","subject_date":"<DATE_JST>"}}
```

**失敗**（Gmail server 缺失 / 認證錯誤 / quota）→ `errors.log`：
```json
{"ts":"<ISO>","level":"ERROR","action":"send_email","detail":{"error":"<class>: <message>","subject_date":"<DATE_JST>"}}
```
`<class>` 為 `not_connected` / `auth` / `quota` / `other` 之一。記錄後繼續（MD 已存在 main，下次再補寄）。

## 步驟 5：結束 Log

```json
{"ts":"<ISO>","level":"INFO","action":"broadcast_end","detail":{"status":"success","email_sent":true,"date":"<DATE_JST>"}}
```

若 Step 4 失敗，`email_sent` 改為 `false`，`status` 改為 `"partial_success"`。

## 步驟 6：Git Commit（Logs）

```bash
git add daily-japan-news-digest/logs/
git commit -m "chore(japan-news): broadcast logs for <DATE_JST>"
SHA=$(git rev-parse --short HEAD)
```

## 步驟 7：Git Push（到 `main`）

本 routine 已獲 repo owner 明確授權直接 push `main`（見 root `CLAUDE.md` Git Commit 規範）。

```bash
git fetch origin main
git rebase origin/main
```

`.gitattributes` 已將 `logs/*.log` 標為 `merge=union`，同時間多個 log append 不會衝突；若 rebase 仍卡住：
```bash
git rebase --abort
```
並記錄 ERROR：
```json
{"ts":"<ISO>","level":"ERROR","action":"git_rebase","detail":{"error":"<message>"}}
```

Rebase（或 abort）完成後：
```bash
git push origin HEAD:main
```

**push 成功** → 記錄：
```json
{"ts":"<ISO>","level":"INFO","action":"git_push","detail":{"branch":"main","sha":"<SHA>"}}
```
routine 正常結束。

**push 被拒**（protected branch / 權限問題）→ 寫 WARN 並改 push 到自己的分支，然後 exit 1：
```json
{"ts":"<ISO>","level":"WARN","action":"git_push","detail":{"error":"<message>","fallback":"branch"}}
```
```bash
git push -u origin <BRANCH>
```

---

## 失敗處理總表

| 失敗點 | 處理方式 | 是否中止 |
|---|---|---|
| 今日 output MD 不存在 | 記 errors.log，exit 1 | ✅ 中止 |
| 今日已發送（重複執行保護） | 正常結束，不發送 | ❌ 跳過 |
| Gmail 發送失敗 | 記 errors.log，繼續 commit | ❌ 繼續 |
| Git commit 失敗 | 記 errors.log，exit 1 | ✅ 中止 |
| push `main` 被拒 | push 到分支 + exit 1 | ✅ 中止（並標記失敗） |
| Git push（分支 fallback）也失敗 | 記 errors.log，exit 1 | ✅ 中止 |

---

## 安全檢查清單

- [ ] `logs/actions.log` 的 `recipient` 欄位一律為 `<redacted>`
- [ ] `logs/errors.log` 無真實 email
- [ ] Commit messages 無 email / secrets
