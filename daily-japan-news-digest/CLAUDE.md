// daily-japan-news-digest/CLAUDE.md
# Daily Japan News Digest

每天自動執行兩個連續 Routine，抓取日本 7 類新聞，產出繁體中文摘要 MD，並以 Gmail 廣播。

## Routine 排程

| Routine | 時間 (JST) | 入口 | 職責 |
|---|---|---|---|
| `daily-digest` | 07:00 | `prompts/daily-digest.md` | 抓取 RSS → 摘要 → 寫 MD → commit → PR → merge |
| `broadcast-digest` | 07:10 | `prompts/broadcast-digest.md` | 讀今日 MD → 轉 HTML → 寄 Gmail → commit → PR → merge |

兩個 Routine 分開執行，避免單一 session 因工作量過大而 timeout。

## 執行入口

- **daily-digest**：讀取並完整執行 `prompts/daily-digest.md`
- **broadcast-digest**：讀取並完整執行 `prompts/broadcast-digest.md`

## 環境變數（Routine secrets 注入）

- `MY_EMAIL` — 收件信箱（僅 broadcast-digest 使用）

## 分類（7 類）

1. 🤖 Claude Code 新聞（`claude_code`）
2. 🇺🇸 美國 AI 大廠（`us_ai_labs`）
3. 🧠 日本 AI / ML 研究（`japan_ai`）
4. 👨‍💻 日本工程社群（`japan_dev_community`）
5. 🖥️ 日本科技業（`japan_tech`）
6. ₿ 日本 Crypto（`japan_crypto`）
7. 📰 日本綜合（`japan_general`）

## 成功條件

### daily-digest
- `output/YYYYMMDD-HHMMSS.md` 已產生
- 兩個 commit 已建立（output + logs）
- `git push` 成功（PR 由 Routine 平台自動建立）

### broadcast-digest
- Gmail 已寄出（或已記錄 email 失敗）
- broadcast log commit 已建立
- `git push` 成功（PR 由 Routine 平台自動建立）
