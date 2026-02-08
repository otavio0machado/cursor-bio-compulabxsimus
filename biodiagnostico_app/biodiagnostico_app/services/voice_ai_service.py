"""
Servico de Voz-para-Formulario via Gemini AI
Recebe audio base64, envia ao Gemini com prompt form-specific, retorna JSON estruturado.
"""
import json
import logging
import base64
from typing import Dict, Any
from ..config import Config

logger = logging.getLogger(__name__)

FORM_PROMPTS: Dict[str, str] = {
    "registro": """Voce e um assistente de laboratorio de analises clinicas. O usuario esta ditando dados para registrar um controle de qualidade (CQ).

Extraia os seguintes campos da fala do usuario:
- exam_name: Nome do exame (ex: GLICOSE, COLESTEROL TOTAL, UREIA, CREATININA, GOT, GPT). Sempre em MAIUSCULAS.
- value: Valor da medicao (numero decimal, ex: 95.5). Use ponto como separador decimal.
- target_value: Valor-alvo ou valor de referencia (numero decimal). Use ponto como separador decimal.
- equipment: Nome do equipamento (ex: Cobas c111, Mindray BS-120).
- analyst: Nome do analista responsavel.

REGRAS:
- Se o usuario nao mencionar algum campo, retorne string vazia "" para texto e null para numeros.
- Numeros devem ser float (ex: 95.5, nao "95,5").
- Se o usuario disser "virgula", interprete como separador decimal (ex: "noventa e cinco virgula cinco" = 95.5).
- Retorne APENAS um JSON valido, sem markdown, sem explicacao, sem comentarios.

Formato de resposta (JSON puro):
{"exam_name": "", "value": null, "target_value": null, "equipment": "", "analyst": ""}""",

    "referencia": """Voce e um assistente de laboratorio de analises clinicas. O usuario esta ditando dados para cadastrar uma referencia de controle de qualidade.

Extraia os seguintes campos:
- name: Nome do registro de referencia (ex: "Kit ControlLab Jan/2026").
- exam_name: Nome do exame. Sempre em MAIUSCULAS.
- level: Nivel do controle (opcoes: "Normal", "N1", "N2", "N3"). Default "Normal".
- valid_from: Data de inicio de validade (formato YYYY-MM-DD). Se o usuario disser "hoje", use a data atual.
- valid_until: Data de fim de validade (formato YYYY-MM-DD). Pode ser vazio.
- target_value: Valor-alvo (numero decimal).
- cv_max: CV% maximo aceito (numero decimal, geralmente 5.0 a 15.0).
- lot_number: Numero do lote do material de controle.
- manufacturer: Fabricante (ex: ControlLab, Randox, Bio-Rad).
- notes: Observacoes adicionais.

REGRAS:
- Se o usuario nao mencionar algum campo, retorne string vazia "" para texto e null para numeros.
- Numeros devem ser float. Se o usuario disser "virgula", interprete como separador decimal.
- Datas no formato YYYY-MM-DD.
- Retorne APENAS um JSON valido.

Formato de resposta (JSON puro):
{"name": "", "exam_name": "", "level": "Normal", "valid_from": "", "valid_until": "", "target_value": null, "cv_max": null, "lot_number": "", "manufacturer": "", "notes": ""}""",

    "reagente": """Voce e um assistente de laboratorio de analises clinicas. O usuario esta ditando dados para cadastrar um lote de reagente.

Extraia os seguintes campos:
- name: Nome do reagente (ex: "Glicose Enzimatica", "Colesterol HDL Direto").
- lot_number: Numero do lote (ex: "LOT2024-001", "B25A1234").
- expiry_date: Data de validade (formato YYYY-MM-DD).
- initial_stock: Estoque inicial (numero inteiro ou decimal).
- daily_consumption: Consumo diario estimado (numero decimal).
- manufacturer: Fabricante (ex: Labtest, Wiener, Roche, Abbott).

REGRAS:
- Se o usuario nao mencionar algum campo, retorne string vazia "" para texto e null para numeros.
- Numeros devem ser float.
- Datas no formato YYYY-MM-DD. Se o usuario disser "validade marco 2026", converta para "2026-03-31".
- Retorne APENAS um JSON valido.

Formato de resposta (JSON puro):
{"name": "", "lot_number": "", "expiry_date": "", "initial_stock": null, "daily_consumption": null, "manufacturer": ""}""",

    "manutencao": """Voce e um assistente de laboratorio de analises clinicas. O usuario esta ditando dados para registrar uma manutencao de equipamento.

Extraia os seguintes campos:
- equipment: Nome do equipamento (ex: "Cobas c111", "Mindray BS-120", "Centrifuga Eppendorf").
- type: Tipo de manutencao. DEVE ser um destes: "Preventiva", "Corretiva", "Calibração".
- date: Data da manutencao (formato YYYY-MM-DD). Se o usuario disser "hoje", use a data atual.
- next_date: Data da proxima manutencao prevista (formato YYYY-MM-DD). Pode ser vazio.
- notes: Descricao do que foi feito ou observacoes.

REGRAS:
- Se o usuario nao mencionar algum campo, retorne string vazia "" para texto.
- O campo "type" DEVE ser exatamente "Preventiva", "Corretiva" ou "Calibração". Se o usuario disser algo diferente, escolha o mais proximo.
- Datas no formato YYYY-MM-DD.
- Retorne APENAS um JSON valido.

Formato de resposta (JSON puro):
{"equipment": "", "type": "", "date": "", "next_date": "", "notes": ""}""",
}


class VoiceAIService:
    """Processa audio via Gemini e retorna dados estruturados para formularios"""

    _client = None

    @classmethod
    def _get_client(cls):
        """Retorna instancia do cliente Gemini (lazy init)"""
        if cls._client is None:
            from google import genai
            api_key = Config.GEMINI_API_KEY
            if not api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY nao configurada. Adicione ao arquivo .env"
                )
            cls._client = genai.Client(api_key=api_key)
        return cls._client

    @staticmethod
    async def process_audio(
        audio_base64: str,
        form_type: str,
        mime_type: str = "audio/webm",
    ) -> Dict[str, Any]:
        """
        Envia audio ao Gemini e retorna dados estruturados.

        Args:
            audio_base64: Audio codificado em base64
            form_type: Tipo do formulario ("registro", "referencia", "reagente", "manutencao")
            mime_type: Tipo MIME do audio (padrao: audio/webm do MediaRecorder)

        Returns:
            Dict com os campos extraidos ou {"error": "mensagem"}
        """
        raw_text = ""
        try:
            client = VoiceAIService._get_client()

            prompt = FORM_PROMPTS.get(form_type)
            if not prompt:
                return {"error": f"Tipo de formulario desconhecido: {form_type}"}

            audio_bytes = base64.b64decode(audio_base64)

            if len(audio_bytes) < 100:
                return {"error": "Audio muito curto. Tente novamente."}

            from google.genai import types

            response = await client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(
                        parts=[
                            types.Part.from_bytes(
                                data=audio_bytes,
                                mime_type=mime_type,
                            ),
                            types.Part.from_text(prompt),
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=1024,
                ),
            )

            raw_text = response.text.strip()
            logger.info(f"Gemini voice response ({form_type}): {raw_text[:200]}")

            # Limpar markdown fences se Gemini envolver em ```json
            if raw_text.startswith("```"):
                raw_text = raw_text.split("\n", 1)[-1]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3].strip()

            parsed = json.loads(raw_text)
            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {e}. Raw: {raw_text[:300]}")
            return {"error": "Nao foi possivel interpretar a resposta. Tente falar mais claramente."}
        except RuntimeError as e:
            logger.error(f"Config error: {e}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Voice AI error: {e}", exc_info=True)
            return {"error": f"Erro ao processar audio: {str(e)}"}
