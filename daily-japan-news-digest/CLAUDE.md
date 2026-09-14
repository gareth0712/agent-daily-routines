// daily-japan-news-digest/CLAUDE.md
# Daily Japan News Digest

每天自動執行 `daily-digest`，抓取日本 7 類新聞，產出繁體中文摘要 MD，並在同一次執行內以 Gmail 廣播。`broadcast-digest` 為選用補寄工具，不在預設排程內。

## Routine 排程

| Routine | 時間 (JST) | 入口 | 職責 |
|---|---|---|---|
| `daily-digest` | 07:00（每日排程） | `prompts/daily-digest.md` | 抓取 RSS → 摘要 → 寫 MD → commit → Gmail → commit → push `main` |
| `broadcast-digest` | 選用／補寄（不排程） | `prompts/broadcast-digest.md` | 僅在當日 `send_email` 缺失時手動觸發：讀今日 MD → 轉 HTML → 寄 Gmail → commit → push `main` |

## 執行入口

- **daily-digest**：讀取並完整執行 `prompts/daily-digest.md`
- **broadcast-digest**：讀取並完整執行 `prompts/broadcast-digest.md`（僅補寄時使用）

## 抓取機制

RSS 抓取由 `scripts/fetch_feeds.py` 決定性執行（非 LLM WebFetch 迴圈），同時寫入 zero-trust log。Log 語意：

- INFO `items:0`、`status:200` → feed 存活，只是 24h 內無新文章，非錯誤
- WARN `stale_feed` → feed 最新文章超過 `meta.staleFeedDays`（預設 7 天），來源可能已死，需人工檢查
- ERROR `network_policy` → Routine 環境的網路白名單擋下該 host，需把 host 加入 allowed domains
- ERROR `http_4xx` / `http_5xx` → 來源本身問題，跳過即可

## 收件者

寄給自己：session context 的 `userEmail`（Gmail connector 登入帳號）。環境變數 `MY_EMAIL` 為選用覆寫，未設定即略過。地址只能當 Gmail tool 參數，不得寫入任何檔案。

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
- Gmail 已寄出（或已記錄失敗，見 errors.log）
- 兩個 commit 已建立（output + logs）
- 已 push 到 `main`

### broadcast-digest（僅補寄時適用）
- Gmail 已寄出（或已記錄 email 失敗）
- broadcast log commit 已建立
- 已 push 到 `main`
