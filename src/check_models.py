from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

client = genai.Client(api_key=api_key)

print("Fetching available models...")
for model in client.models.list():
    print(f"Model ID: {model.name}")