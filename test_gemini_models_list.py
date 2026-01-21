
import os
import asyncio
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

def list_models_sync():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print("Listing Flash models...")
    try:
        for m in client.models.list():
            if "flash" in m.name.lower():
                print(f"{m.name}")
            
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models_sync()
