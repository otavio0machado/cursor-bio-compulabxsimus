---
name: Integração AI e Prompts (O Oráculo)
description: Padronização, robustez e controle nas chamadas de IA (Gemini), separando prompts do código.
---

# Skill: Integração AI e Prompts ("O Oráculo")

Esta skill governa a inteligência do Biodiagnóstico. Seu objetivo é transformar chamadas de API frágeis ("strings soltas") em uma arquitetura robusta, testável e econômica.

## 🎯 Objetivos
- **Desacoplar Prompts**: Prompts não devem viver no meio de funções Python.
- **Resiliência**: Tratamento automático de `ResourceExhausted` (429) e timeouts.
- **Consistência**: Garantir que o JSON retornado pela IA siga sempre o mesmo schema.

## 📂 Estrutura Recomendada
- `biodiagnostico_app/ai/`: Módulo dedicado.
    - `prompts/`: Arquivos de texto ou YAML com os prompts.
        - `analise_pdf.txt`
        - `correcao_ocr.yaml`
    - `services/`: Classes que encapsulam a chamada ao Gemini.
    - `schemas/`: Definições Pydantic do formato de resposta esperado.

## 🛠️ O Gerenciador de Prompts
Evite concatenar strings gigantes no código. Use um template engine simples ou arquivos formatados.

### Exemplo de Template (Classe)

```python
# biodiagnostico_app/ai/services/prompt_manager.py
from string import Template

class PromptManager:
    @staticmethod
    def get_prompt(prompt_name: str, **kwargs) -> str:
        # Carregar de arquivo ou constante
        template_str = PROMPTS.get(prompt_name, "")
        return Template(template_str).safe_substitute(**kwargs)

# Uso
prompt = PromptManager.get_prompt("analise_pdf", texto_extraido=pdf_text)
```

## 🛡️ Tratamento de Erros e Retries
Sempre envolva chamadas de LLM com retentativas exponenciais.

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def chamar_gemini(prompt: str):
    # Lógica de chamada
    pass
```

## 🚨 Regras do Oráculo
1. **JSON Mode Always**: Sempre instrua a IA a retornar JSON e use `generation_config={"response_mime_type": "application/json"}` no Gemini 1.5.
2. **Never Trust AI**: Valide o JSON retornado com Pydantic antes de usar. Se falhar, lance `AIParsingError`.
3. **Log Everything**: Logue o token usage (se disponível) e latência para monitoramento futuro.

## 📝 Scripts
- `scripts/test_prompts.py`: Script para rodar um prompt contra um set de arquivos de teste e avaliar a qualidade da resposta (human evaluation).
