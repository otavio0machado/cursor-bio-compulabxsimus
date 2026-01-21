
import os
import asyncio
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

async def list_models():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("API Key not found!")
        return

    client = genai.Client(api_key=api_key)
    
    print("Attempting to list models...")
    try:
        # The new library might have a different way to list models, 
        # but let's try the common 'models.list' if available or just test a generation.
        # Documentation for google-genai 1.0+ suggests client.models.list()
        
        # Note: client.models might be the way, or client.aio.models
        # Let's try to just generate content with 'gemini-1.5-flash' to verify specific model
        # and print expected success.
        
        print("\nTesting 'gemini-1.5-flash'...")
        response = await client.aio.models.generate_content(
            model="gemini-1.5-flash",
            contents="Hello, just testing the connection."
        )
        print(f"Success! Response: {response.text}")
        
    except Exception as e:
        print(f"\nError testing 'gemini-1.5-flash': {e}")
        
    try:
        print("\nTesting 'gemini-1.5-pro'...")
        response = await client.aio.models.generate_content(
            model="gemini-1.5-pro",
            contents="Hello, just testing the connection."
        )
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"\nError testing 'gemini-1.5-pro': {e}")

if __name__ == "__main__":
    asyncio.run(list_models())
