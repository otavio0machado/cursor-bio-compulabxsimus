import os
import logging
import asyncio
import google.genai as genai
from google.genai import types
from string import Template
from typing import Optional, List
from dotenv import load_dotenv, find_dotenv

# Load env vars from .env file (search in current and parent dirs)
load_dotenv(find_dotenv())

# Path to the prompt file
PROMPT_FILE = os.path.join(os.path.dirname(__file__), "../prompts/detective_persona.txt")

class DetectiveService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logging.error("GEMINI_API_KEY not found in environment variables.")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)
        
        # Use gemini-2.5-flash (confirmed available via models.list())
        self.model = "gemini-2.5-flash"
        # Fallback to gemini-2.0-flash if 2.5 fails
        self.fallback_model = "gemini-2.0-flash"

    def _load_prompt(self, data_json: str) -> str:
        """Loads and populates the prompt template."""
        try:
            with open(PROMPT_FILE, "r", encoding="utf-8") as f:
                template_str = f.read()
                template = Template(template_str)
                return template.safe_substitute(data_json=data_json)
        except Exception as e:
            logging.error(f"Error loading prompt file: {e}")
            # Fallback inline prompt
            return f"Voce e um analista financeiro. Analise estes dados: {data_json}"

    async def ask_detective(self, question: str, data_context: str, images: Optional[List[dict]] = None) -> str:
        """
        Sends the user's question, the data context, and optional images to Gemini.
        Includes retry logic with exponential backoff.
        
        images: List of dicts with {"data": bytes, "mime_type": str}
        """
        if not self.client:
            return "Erro: Chave de API do Gemini nao configurada."

        system_instruction = self._load_prompt(data_context)
        
        # Prepare contents
        contents = [question]
        if images:
            for img in images:
                contents.append(
                    types.Part.from_bytes(
                        data=img["data"],
                        mime_type=img["mime_type"]
                    )
                )
        
        # List of models to try
        models_to_try = [self.model, self.fallback_model]
        
        for model_name in models_to_try:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = await self.client.aio.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.2,
                        )
                    )
                    return response.text
                except Exception as e:
                    error_msg = str(e)
                    
                    # Check for rate limit (429)
                    if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                        wait_time = 2 ** (attempt + 1)  # 2, 4, 8 seconds
                        logging.warning(f"Rate limited on {model_name}. Waiting {wait_time}s (attempt {attempt+1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                    else:
                        logging.error(f"Error with {model_name}: {error_msg}")
                        break  # Non-retryable error, try next model
            
            logging.warning(f"All retries exhausted for {model_name}. Trying next model...")
        
        return "Desculpe, o Detetive de Dados esta temporariamente indisponivel. Por favor, tente novamente em alguns minutos."

