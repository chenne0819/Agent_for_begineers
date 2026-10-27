# 第 2 課範例：口語記帳轉帳本

用講話的方式輸入今天的花費，AI 依照**固定格式**整理成一筆一筆的資料，自動存進 `帳本.csv`（可以直接用 Excel 打開），再印出各分類的累計金額。

```
今天花了什麼？> 早餐蛋餅35，午餐雞腿便當100，晚上跟朋友兩個人吃火鍋平分總共800，買衣服一千出頭

品項                金額  分類  備註
--------------------------------------------
蛋餅                  35  餐飲
雞腿便當             100  餐飲
火鍋                 400  餐飲  兩人平分，總額 800

看不懂、沒有記下來的：買衣服一千出頭

帳本累計：
  餐飲  ████████████████████ 535
```
（以上是示意，實際結果以 AI 的回答為準）

## 你需要準備

跟第 1 課一樣：**Python 3.10 以上** + **Anthropic API 金鑰**。做過第 1 課的話，直接把那邊的 `.env` 複製過來就好。

## 執行步驟

在這個資料夾（`code/`）開終端機：

**Windows（PowerShell）**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt      # 這一課多了 pydantic
copy .env.example .env               # 打開 .env 貼上金鑰
python expense_parser.py             # 結構化輸出
python expense_parser.py --raw       # 對照組：不指定格式
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python expense_parser.py
python expense_parser.py --raw
```

## 程式重點（對照影片）

只有一個檔案 `expense_parser.py`：

| 位置 | 做什麼 | 影片裡的概念 |
|---|---|---|
| `SYSTEM` | 角色與任務、5 條規則、1 個範例 | 好 prompt 的要素、範例（few-shot） |
| `class Expense` / `class Ledger` | 用 Pydantic 定義資料的欄位、型別、可選的分類 | Schema（資料的格式說明書） |
| `client.beta.messages.parse(..., output_format=Ledger)` | 要求 AI 照 `Ledger` 的格式回傳 | 結構化輸出 |
| `response.parsed_output` | 已經驗證過的資料，可以直接存檔、加總 | 程式不用再自己解析文字 |
| `ask_raw()` | 同樣的 prompt，但不指定格式 | 對照組：看看 AI 自由發揮會回什麼 |

`Field(description=...)` 裡寫的說明也會一起送給 AI，等於是 prompt 的一部分。

## 動手試試

1. **比較兩種模式**：同一句話分別用一般模式和 `--raw` 跑，想想看哪一種比較容易讓程式接著處理
2. **刪掉範例**：把 `SYSTEM` 最後的「範例」整段刪掉，再輸入「跟朋友三個人吃燒肉平分，總共 1500」，看分攤的金額和 note 有沒有變
3. **加一個分類**：在 `Literal[...]` 和 `CATEGORIES` 都加上「醫療」，輸入「掛號費 150」看看會不會被分到新的分類
4. **加一個欄位**：在 `Expense` 加上 `payment: Literal["現金", "信用卡", "電子支付"]`，記帳時講「刷卡買了…」試試

## 常見問題

- **回覆不符合帳本格式**：模型拒絕回答或回覆不完整時，程式會略過這次回覆，不寫入帳本；請換個說法再試。

- **找不到 ANTHROPIC_API_KEY**：確認 `.env` 跟 `expense_parser.py` 在同一個資料夾，檔名就是 `.env`
- **`AuthenticationError` / 401**：金鑰貼錯，或前後多了空白、引號
- **Excel 打開 `帳本.csv` 是亂碼**：程式已經用 `utf-8-sig` 存檔，一般會正常顯示；如果還是亂碼，用 Excel 的「資料 → 從文字/CSV」匯入，編碼選 UTF-8
- **想清空帳本**：直接刪掉 `帳本.csv`，下次執行會自動重新建立
- **Windows 出現 `ModuleNotFoundError: No module named 'anthropic.types.beta....'`**：資料夾路徑太長，超過 Windows 預設的 260 字元上限。把課程資料夾搬到短一點的位置（例如 `C:\agent-course`），刪掉 `.venv` 重新安裝
