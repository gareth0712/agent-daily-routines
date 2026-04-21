// agent-daily-routines/CLAUDE.md
# Agent Daily Routines

此 repo 託管多個獨立 Cloud Routines，每個子目錄是一個自動化任務。
所有 routines 共用以下規範。

## 架構約定

每個 routine 子目錄必須包含：
- `CLAUDE.md` — 該 routine 的任務描述
- `prompts/` — 執行指令模板
- `output/` — 每日產出
- `logs/` — 執行日誌

## Zero-Trust Observability（強制）

**原則：不相信 agent 的自我報告，所有動作必須落檔驗證。**

### `logs/actions.log` — 所有動作
JSON Lines 格式，append-only，每行一筆：
```json
{"ts":"2026-04-22T07:00:15+09:00","level":"INFO","action":"fetch_rss","detail":{"url":"https://...","items":5,"status":200}}
```

必記錄的動作：`routine_start`、`fetch_rss`、`parse_feed`、`summarize_category`、`write_output`、`send_email`、`git_commit`、`git_push`、`routine_end`

### `logs/errors.log` — 錯誤與警告
只記錄 WARN / ERROR 級別，格式同上。
**失敗不中止整體流程**（Result pattern 心智模型）：某個 RSS fail 就記下繼續，不要 silent fail。

### 安全要求（public repo）
**禁止**在任何 log / output / commit message 中出現：
- Email 地址（包括 `{{MY_EMAIL}}` 解析後的值）
- 任何 secrets / tokens
- 個人姓名

## 時區
所有時間戳一律 **JST（Asia/Tokyo）** + ISO 8601 帶時區偏移。

## Git Commit 規範

每次執行結束必須**兩步 commit**：

```bash
# Step 1: 產出檔案
git add {routine}/output/
git commit -m "docs({routine-short}): daily digest YYYY-MM-DD"

# Step 2: 日誌
git add {routine}/logs/
git commit -m "chore({routine-short}): logs for YYYY-MM-DD"

# Push
git push origin main
```

Commit author 由 Routine 環境預設處理（`claude-code-bot`），勿覆寫。

## 語言規範
所有 output 用**繁體中文**，人名/地名/公司名保留原文（日文/英文）。
Log / commit message 用英文。

## 失敗處理
- 單一 RSS 失敗：記 `errors.log`，繼續其他來源
- 全部 RSS 失敗：仍產出 MD 檔（內容為「本日全部來源抓取失敗」）+ 寄錯誤通知
- Gmail 失敗：MD 檔仍 commit，errors.log 記錄，下次執行時檢查是否需要補寄
- Git push 失敗：記錄後 exit 非零碼讓 Routine 標記失敗