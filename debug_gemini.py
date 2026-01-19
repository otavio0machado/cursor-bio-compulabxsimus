
import os
import sys
from dotenv import load_dotenv

# Try to find .env manually to be sure
current_dir = os.getcwd()
print(f"Current working directory: {current_dir}")

# Attempt to load .env
load_dotenv()

key = os.getenv("GEMINI_API_KEY")
print(f"GEMINI_API_KEY from env: {'FOUND (Starts with ' + key[:4] + ')' if key else 'NOT FOUND'}")

try:
    import google.generativeai as genai
    print("google-generativeai package: INSTALLED")
except ImportError:
    print("google-generativeai package: NOT INSTALLED")

# Test Config class directly
try:
    sys.path.append(os.path.join(current_dir, 'biodiagnostico_app'))
    from biodiagnostico_app.config import Config
    config_key = Config.GEMINI_API_KEY
    print(f"Config.GEMINI_API_KEY: {'FOUND (Starts with ' + config_key[:4] + ')' if config_key else 'NOT FOUND'}")
except Exception as e:
    print(f"Error importing Config: {e}")
