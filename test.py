import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
API_KEY = os.getenv("HF_TOKEN")
print(API_KEY)

client = InferenceClient(
    model="black-forest-labs/FLUX.1-dev",
    token=API_KEY,  # ✅ ใช้ token แทน api_key
)


image = client.text_to_image(
    """A two good friend young man different races (Elf, orc, human, Dark elf)
    Chilling in tavern""",
    width=1080,   # ความกว้าง
    height=1920,  # ความสูง
)

image.save("output.png")