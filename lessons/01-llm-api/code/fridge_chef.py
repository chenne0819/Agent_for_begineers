"""
第 1 課範例：冰箱清庫存料理顧問

輸入冰箱裡剩下的食材，AI 推薦料理；之後可以一直追問（例如「沒有醬油怎麼辦？」）。
每次回答完，會印出這一輪用了多少 token、大約花多少錢。

執行：python fridge_chef.py
"""
import os
import sys

import anthropic
from dotenv import load_dotenv

load_dotenv()  # 從 .env 檔讀取 ANTHROPIC_API_KEY

MODEL = "claude-opus-5-5"
# 每 100 萬個 token 的價格（美元，2026-10 官方定價，可能會變動）
PRICE_INPUT = 4.00
PRICE_OUTPUT = 20.00

# system prompt：設定 AI 的角色和規則，每一輪都會一起送出
SYSTEM = """你是一位擅長「清冰箱」的家常菜料理顧問。
- 以使用者提到的食材為主，只額外使用鹽、糖、油、醬油這類基本調味料
- 每次推薦 2 道料理，每道附 3～5 個簡單步驟
- 使用繁體中文，語氣輕鬆、內容精簡"""


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("找不到 ANTHROPIC_API_KEY。請照 README 把金鑰填進 .env 檔。")

    client = anthropic.Anthropic()
    messages = []      # 對話紀錄：API 不會幫你記住，每一輪都要整份送過去
    total_cost = 0.0

    print("冰箱清庫存料理顧問（直接按 Enter 或輸入 exit 離開）")
    food = input("\n冰箱裡有什麼？> ").strip()
    if not food or food.lower() in ("exit", "quit"):
        return
    question = f"我冰箱裡有：{food}。可以煮什麼？" if food else ""

    while question and question.lower() not in ("exit", "quit"):
        messages.append({"role": "user", "content": question})
        print()

        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM,
            messages=messages,
            output_config={"effort": "low"},          # 聊天型的任務用 low：回得比較快、也比較省
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",                       # 萬一模型婉拒回答，自動改由備援模型接手
        ) as stream:
            for text in stream.text_stream:           # 串流：字一邊產生、一邊印出來
                print(text, end="", flush=True)
            reply = stream.get_final_message()

        if reply.stop_reason == "refusal":
            print("（這個問題模型無法回答，換個問法試試）")
            messages.pop()                             # 把沒被回答的問題移出紀錄
        else:
            messages.append({"role": "assistant", "content": reply.content})

        usage = reply.usage
        cost = (usage.input_tokens * PRICE_INPUT + usage.output_tokens * PRICE_OUTPUT) / 1_000_000
        total_cost += cost
        print(f"\n\n[這一輪：輸入 {usage.input_tokens} token、輸出 {usage.output_tokens} token，"
              f"約 US${cost:.4f}｜累計約 US${total_cost:.4f}]")

        question = input("\n還想問什麼？> ").strip()


if __name__ == "__main__":
    main()
