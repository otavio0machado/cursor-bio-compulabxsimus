
import os
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

def list_gemini_models():
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print("Checking for Gemini 3 models...")
    try:
        found = False
        for m in client.models.list():
            if "gemini-3" in m.name.lower():
                print(f"FOUND: {m.name}")
                found = True
        
        if not found:
            print("No 'gemini-3' models found in your account/region.")
            
    except Exception as e:
        print(f"Error checking models: {e}")

if __name__ == "__main__":
    list_gemini_models()
