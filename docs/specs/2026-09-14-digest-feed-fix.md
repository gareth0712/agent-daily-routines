// docs/specs/2026-09-14-digest-feed-fix.md
# SPEC — daily-japan-news-digest：feed 修復 + 主線合併（2026-09-14）

## Goal
- 134 個 routine run branches（2026-04-22 ～ 2026-09-14）與 PR #1、#2 全部 merge 進 `main`，`output/` 於 `main` 即為正式 digest。
- 每個 feed 都能穩定抓到：修正 9 個死掉／stale／改址的 URL，新增 3 個 Claude Code 來源。
- RSS 抓取改由 `scripts/fetch_feeds.py` 決定性執行並自寫 zero-trust log；Gmail 由 daily-digest 同一次執行內寄出；run 結果直接 push `main`。

## Verification（已執行）
- `git branch -r --no-merged origin/main` → 0 條。
- `logs/actions.log` 3785 行、`logs/errors.log` 1044 行 = 各 branch 加總；每行 `json.loads` 通過；無 conflict marker。
- `grep -E '[A-Za-z0-9._%+-]+@…' output/ logs/` → 0 筆。
- `python3 scripts/fetch_feeds.py --sources sources.json --out items.json --log-dir <tmp>` → 26/26 HTTP 200，exit 0，log 全為合法 JSON。
- 每個新 URL 皆以 curl 實測 200 且最新 item 為當日。

## Fallback
- Merge 前 `origin/main` = `f73628e`。回滾：`git push --force-with-lease origin f73628e:main`（需 owner 授權）。
- Prompt / sources 變更為單一 commit，可 `git revert` 該 commit。

## Risks
- Routine 環境的網路白名單可能擋住 `news.web.nhk`、`mainichi.jp`、`japantimes.co.jp`、`papers.takara.ai`、`ainow.ai`、`developers.cyberagent.co.jp`、`nadanews.com`、`note.com`；出現 ERROR `network_policy` 時需加入 allowed domains。
- NHK CDN 隨機回 403（約 1/3），腳本已加一次 retry；仍可能偶發失敗。
- 直接 push `main` 需 bot 帳號具備權限；被拒時 prompt 會退回 push 分支並 exit 1。
