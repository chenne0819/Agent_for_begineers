"""
第 2 課範例：口語記帳轉帳本

用講話的方式輸入今天的花費（例如「早餐蛋餅35，午餐雞腿便當100」），
AI 依照固定格式整理成一筆一筆的資料，存進「帳本.csv」，再印出各分類的累計金額。

執行：
  python expense_parser.py          結構化輸出（照固定格式回傳資料）
  python expense_parser.py --raw    對照組：不指定格式，看 AI 會回什麼
"""
import csv
import os
import sys
import unicodedata
from datetime import date
from typing import List, Literal

import anthropic
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

load_dotenv()  # 從 .env 檔讀取 ANTHROPIC_API_KEY

MODEL = "claude-opus-5-5"
LEDGER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "帳本.csv")
CATEGORIES = ["餐飲", "交通", "購物", "娛樂", "生活", "其他"]

# 好的 prompt：角色與任務、規則、範例，都寫清楚
SYSTEM = """你是記帳助理，負責把使用者口語的記帳內容，整理成一筆一筆的帳本資料。

規則：
1. 每一筆花費拆成一筆資料；同一句話提到好幾樣東西就分開記
2. 金額一律寫成新台幣整數，例如「兩百五」寫成 250
3. 分類只能用：餐飲、交通、購物、娛樂、生活、其他
4. 跟別人分攤的，只記使用者自己付的金額，並在 note 寫下原本的總額
5. 沒有金額、或金額說不清楚（例如「一百出頭」）的不要猜，原文放進 unclear

範例：
輸入：早上蛋餅35，搭公車15，晚餐跟朋友兩個人吃火鍋平分，總共800
輸出：蛋餅 35（餐飲）、公車 15（交通）、火鍋 400（餐飲，note：兩人平分，總額 800）"""


# 結構化輸出：用 Pydantic 定義「資料長什麼樣子」，AI 回傳的內容一定符合這個格式
class Expense(BaseModel):
    item: str = Field(description="品項，例如「雞腿便當」")
    amount: int = Field(description="使用者實際付的金額，新台幣整數")
    category: Literal["餐飲", "交通", "購物", "娛樂", "生活", "其他"]
    note: str = Field(description="補充說明，沒有就填空字串")


class Ledger(BaseModel):
    expenses: List[Expense]
    unclear: List[str] = Field(description="看不懂或沒有金額的原文片段")


def ask_structured(client, text):
    try:
        response = client.beta.messages.parse(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM,
            messages=[{"role": "user", "content": text}],
            output_format=Ledger,                      # 指定輸出格式
            output_config={"effort": "low"},           # 簡單的整理任務用 low：比較快、比較省
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",                       # 萬一模型婉拒回答，自動改由備援模型接手
        )
    except ValidationError:
        # 模型拒絕或回覆被截斷時，SDK 可能在回傳 response 之前就解析失敗。
        print("（回覆不符合帳本格式，沒有寫入帳本，請換個說法再試）")
        return None
    if response.stop_reason == "refusal" or response.parsed_output is None:
        print("（這段內容無法整理，換個說法試試）")
        return None
    return response.parsed_output                 # 已經是 Ledger 物件，可以直接用


def ask_raw(client, text):
    """對照組：一樣的 prompt，但不指定輸出格式。"""
    response = client.beta.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM,
        messages=[{"role": "user", "content": text}],
        output_config={"effort": "low"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    )
    print(next((b.text for b in response.content if b.type == "text"), "（沒有回覆）"))


def save(ledger):
    new_file = not os.path.exists(LEDGER)
    with open(LEDGER, "a", newline="", encoding="utf-8-sig") as f:   # utf-8-sig：Excel 打開中文不會亂碼
        w = csv.writer(f)
        if new_file:
            w.writerow(["日期", "品項", "金額", "分類", "備註"])
        for e in ledger.expenses:
            w.writerow([date.today().isoformat(), e.item, e.amount, e.category, e.note])


def pad(text, width):
    """中文字在終端機佔兩格，補空白時要算進去，表格才會對齊。"""
    used = sum(2 if unicodedata.east_asian_width(ch) in "WF" else 1 for ch in text)
    return text + " " * max(0, width - used)


def show(ledger):
    print(f"\n{pad('品項', 16)}{'金額':>6}  分類  備註")
    print("-" * 44)
    for e in ledger.expenses:
        print(f"{pad(e.item, 16)}{e.amount:>8}  {e.category}  {e.note}")
    if ledger.unclear:
        print("\n看不懂、沒有記下來的：" + "、".join(ledger.unclear))


def show_totals():
    totals = {c: 0 for c in CATEGORIES}
    with open(LEDGER, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            totals[row["分類"]] += int(row["金額"])
    top = max(totals.values()) or 1
    print("\n帳本累計：")
    for c, v in totals.items():
        if v:
            print(f"  {c}  {'█' * max(1, round(v / top * 20))} {v}")


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("找不到 ANTHROPIC_API_KEY。請照 README 把金鑰填進 .env 檔。")
    raw = "--raw" in sys.argv
    client = anthropic.Anthropic()

    print("口語記帳轉帳本" + ("（對照組：不指定格式）" if raw else "") + "　直接按 Enter 離開")
    while True:
        text = input("\n今天花了什麼？> ").strip()
        if not text or text.lower() in ("exit", "quit"):
            break
        if raw:
            ask_raw(client, text)
            continue
        ledger = ask_structured(client, text)
        if ledger:
            show(ledger)
            save(ledger)
            show_totals()


if __name__ == "__main__":
    main()
