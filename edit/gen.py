import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from transformers import AutoModelForCausalLM, AutoTokenizer
from huggingface_hub import HfApi
# โหลด .env
load_dotenv()

model_name = "EleutherAI/gpt-neo-125M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Prompt สำหรับสร้างข้อความ
prompt = """
You are a writer for TikTok “Would you rather” content.

TASK
- Write EXACTLY 12 original playful questions in English, each using the format “… or … ?”
- Do NOT include the phrase “Would you rather”.
- Keep each question under 14 words.
- No numbering, no prefixes like “Question 1:”.
- Style: playful, surprising, safe for ages 13+.
- Mix topics:superpowers, daily life, food, school, travel, habits, gadgets, social media, religion, sex,.
- Avoid: violence/gore, hate, self-harm, drugs, politics,  medical claims, profanity.
- Do NOT output any explanations.

FEW-SHOT EXAMPLES (do NOT repeat these):
always speak in rhymes or always speak in riddles?
have rewind time for 5 seconds or pause time for 10?
sneeze glitter or hiccup tiny bubbles?
charge your phone by dancing or by telling jokes?
never lose socks again or always find perfect Wi-Fi?
eat breakfast for dinner or dinner for breakfast?

OUTPUT FORMAT
Return ONLY a valid JSON array of strings (no object, no key, no extra text).

NOW PRODUCE:
12 new questions, following all rules above, as a JSON array of strings only.
"""

inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=512)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
