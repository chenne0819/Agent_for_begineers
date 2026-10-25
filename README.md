# AI 研究僧｜AI Agent 入門課程

一位研究生的 AI 實作筆記。用動畫講清楚原理，用 Python 把想法做出來。

這個 repository 放置課程的範例程式與操作說明；每課的程式會隨課程逐步加入。

## 課程與範例

| 課程 | 主題 | 範例程式 |
| --- | --- | --- |
| 第 1 課 | LLM API 入門：讓程式跟 AI 對話 | [冰箱清庫存料理顧問](lessons/01-llm-api/code/) |

## 開始使用

1. 在上方選擇 **Code → Download ZIP** 並解壓縮，或使用 `git clone` 下載此 repository。
2. 進入 `lessons/01-llm-api/code/`。
3. 按照該課的 [README](lessons/01-llm-api/code/README.md) 建立 Python 環境、安裝套件，再執行範例。

目前第 1 課使用 Python 3.10 以上及 Anthropic API。API 需自行申請金鑰並支付用量費；費用以服務商實際帳單為準。

## 金鑰與個人資料

- repository 只提供空白的 `.env.example`；請複製成 `.env`，再填入自己的金鑰。
- 不要將 `.env`、API 金鑰、OAuth 權杖、私人資料或真實對話紀錄提交到 GitHub。
- 範例的食材與對話會傳送到 Anthropic API，請使用適合提供給該服務的內容。
- 範例會顯示 token 用量與估計費用；模型、價格和 API 功能可能更新，請以 [Anthropic 官方文件](https://platform.claude.com/docs/en/about-claude/pricing) 為準。

## 關於頻道

[前往 YouTube 頻道](https://www.youtube.com/channel/UCJz7HPD5WsLc-MmcbCQc_cw)

修的是 AI，練的是實作。
