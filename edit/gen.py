import os
from openai import OpenAI
from dotenv import load_dotenv
import json

# โหลด .env
load_dotenv()

# ดึง HF token
API_KEY = os.getenv("HF_API")
if not API_KEY:
    raise ValueError("HF_API token not found. Set it in .env or environment variable.")

# สร้าง client ของ OpenAI แต่ชี้ไปที่ HF Inference API
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=API_KEY
)

# Prompt สำหรับสร้างข้อความ
prompt = """
You are a writer for TikTok “Would you rather” content.

TASK
- Write EXACTLY 12 original “Would you rather … or … ?” questions in English.
- Keep each question under 14 words.
- No numbering, no prefixes like “Question 1:”.
- Style: playful, surprising, safe for ages 13+.
- Mix topics: daily life, food, school, travel, habits, gadgets, social media, superpowers.
- Avoid: violence/gore, hate, sex, self-harm, drugs, politics, religion, medical claims, profanity.
- Do NOT output any explanations.

FEW-SHOT EXAMPLES (do NOT repeat these):
always speak in rhymes or always speak in riddles?
have rewind time for 5 seconds or pause time for 10?
sneeze glitter or hiccup tiny bubbles?
charge your phone by dancing or by telling jokes?
never lose socks again or always find perfect Wi-Fi?
eat breakfast for dinner or dinner for breakfast?

OUTPUT FORMAT
Return ONLY a valid JSON array of strings. No code fences, no extra text.

NOW PRODUCE:
12 new questions, following all rules above, as a JSON array of strings only.
"""

def main():
    try:
        # เรียกโมเดลผ่าน client ของ OpenAI (HF-compatible)
        completion = client.chat.completions.create(
            model="HuggingFaceTB/SmolLM3-3B:hf-inference",  # เปลี่ยนโมเดลได้ตามที่คุณเลือก
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # ดึงข้อความจาก response
        generated_text = completion.choices[0].message.content
        print("==== RESULT ====")
        print(generated_text)

        # บันทึกลงไฟล์
        with open("would_you_rather.json", "w", encoding="utf-8") as f:
            f.write(generated_text)

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()
