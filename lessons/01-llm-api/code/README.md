# 第 1 課範例：冰箱清庫存料理顧問

輸入冰箱裡剩下的食材，AI 推薦兩道料理；接著可以一直追問。每一輪回答完，程式會印出用了多少 token、大約花多少錢。

```
冰箱裡有什麼？> 雞蛋、番茄、半顆洋蔥

推薦你做「番茄炒蛋」和「洋蔥烘蛋」！……（AI 的回答會一個字一個字跑出來）

[這一輪：輸入 120 token、輸出 380 token，約 US$0.0081｜累計約 US$0.0081]

還想問什麼？> 沒有醬油怎麼辦？
```
（以上是示意，實際回答每次都不一樣）

## 你需要準備

1. **Python 3.10 以上**：到 [python.org](https://www.python.org/downloads/) 下載。Windows 安裝時記得勾選「Add Python to PATH」
2. **Anthropic API 金鑰**：到 [console.anthropic.com](https://console.anthropic.com) 註冊 → 儲值 → 在「API Keys」建立一把金鑰（`sk-ant-` 開頭）。跑完這支範例大約只要幾美分

## 執行步驟

在這個資料夾（`code/`）開終端機：

**Windows（PowerShell）**
```powershell
python -m venv .venv                 # 建立虛擬環境（只要做一次）
.venv\Scripts\activate               # 啟用虛擬環境
pip install -r requirements.txt      # 安裝套件（只要做一次）
copy .env.example .env               # 複製設定檔，再用記事本打開 .env 貼上金鑰
python fridge_chef.py                # 執行
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                 # 再用文字編輯器打開 .env 貼上金鑰
python fridge_chef.py
```

`.env` 打開後長這樣，把金鑰貼在等號後面：
```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx
```

## 程式重點（對照影片）

只有一個檔案 `fridge_chef.py`，重點在這幾個地方：

| 位置 | 做什麼 | 影片裡的概念 |
|---|---|---|
| `SYSTEM` | 設定 AI 的角色和規則 | system prompt |
| `messages` | 每一輪都把整份對話紀錄送出去 | API 是「無狀態」的 |
| `client.beta.messages.stream(...)` | 送出請求，回答一邊產生一邊印出來 | API 呼叫、串流 |
| `reply.usage` | 這一輪的輸入、輸出 token 數 | token 與費用 |
| `fallbacks="default"` | 萬一模型婉拒回答，自動改由備援模型接手 | （進階，第 13 課會再說明） |

## 動手試試

1. **換角色**：把 `SYSTEM` 改成「減脂料理顧問」或「十分鐘快手料理」，看回答怎麼變
2. **觀察 token**：連續追問 3、4 次，看「輸入 token」是不是越來越多？想想為什麼（提示：對話紀錄）
3. **調思考深度**：把 `effort` 從 `"low"` 改成 `"high"`，比較回答品質、速度和費用
4. **省錢**：把 `MODEL` 換成比較便宜的模型（例如 `claude-haiku-5-5`），記得一起改 `PRICE_INPUT`、`PRICE_OUTPUT`

## 常見問題

- **找不到 ANTHROPIC_API_KEY**：確認 `.env` 跟 `fridge_chef.py` 放在同一個資料夾，而且檔名就是 `.env`（不是 `.env.txt`）
- **`AuthenticationError` / 401**：金鑰貼錯，或前後多了空白、引號
- **`PermissionDeniedError`、餘額相關錯誤**：帳戶還沒儲值
- **Windows 出現 `ModuleNotFoundError: No module named 'anthropic.types.beta....'`**：資料夾路徑太長，超過 Windows 預設的 260 字元上限。把整個課程資料夾搬到短一點的位置（例如 `C:\agent-course`），刪掉 `.venv` 重新安裝就好
- **`.env` 不要上傳到 GitHub**：已經寫在 `.gitignore` 裡了。金鑰外流的話，到 console 把那把金鑰刪掉、再建一把新的
