import os

from dotenv import load_dotenv
from edit import edit

load_dotenv()

API_KEY   = os.getenv("GOOGLE_API")
SEARCH_ID = os.getenv("GOOGLE_SEARCH_ID")

txt_bot, txt_top = edit()

print(txt_bot)
print(txt_top)