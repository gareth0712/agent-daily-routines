// daily-japan-news-digest/CLAUDE.md
# Daily Japan News Digest

每天 07:00 JST 自動執行，抓取日本 4 類新聞，產出繁體中文摘要 MD + Gmail。

## 執行入口
讀取並完整執行 `prompts/daily-digest.md`。

## 環境變數（Routine secrets 注入）
- `MY_EMAIL` — 收件信箱

## 分類
1. 🖥️ 日本科技業（`japan_tech`）
2. 📰 日本綜合新聞（`japan_general`）
3. 🤖 日本 AI 發展（`japan_ai`）
4. ₿ 日本 Crypto（`japan_crypto`）

## 成功條件
- `output/YYYYMMDD-HHMMSS.md` 已產生
- Gmail 已寄出（或已記錄 email 失敗）
- 兩個 commit 已建立
- `git push` 成功