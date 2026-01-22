"""
Serviço Unificado de IA - Biodiagnóstico App
Suporta OpenAI e Gemini com retry automático e JSON mode.

Segue as diretrizes da skill "O Oráculo":
- Resiliência com tenacity
- JSON Mode para respostas estruturadas
- Logging de uso
"""
import os
import asyncio
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Modelos disponíveis por provedor
AVAILABLE_MODELS = {
    "OpenAI": [
        {"id": "gpt-4o", "name": "GPT-4o (Mais Capaz)", "description": "Melhor qualidade, ideal para análises complexas"},
        {"id": "gpt-4o-mini", "name": "GPT-4o Mini (Econômico)", "description": "Rápido e econômico"},
    ],
    "Gemini": [
        {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "description": "Rápido e eficiente"},
        {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "description": "Melhor raciocínio"},
    ]
}

# Template do prompt de análise - DETALHADO
ANALYSIS_PROMPT_TEMPLATE = """
Você é um auditor financeiro sênior especialista em laboratórios de análises clínicas.
Seu relatório será lido pela diretoria do laboratório para tomada de decisões.

## DADOS DA ANÁLISE

### Faturamento
| Sistema | Valor |
|---------|-------|
| COMPULAB | R$ {compulab_total:,.2f} |
| SIMUS | R$ {simus_total:,.2f} |
| **DIFERENÇA** | **R$ {difference:,.2f}** |

### Divergências Identificadas
| Categoria | Quantidade | Valor Total |
|-----------|------------|-------------|
| Pacientes sem registro no SIMUS | {missing_patients_count} | R$ {missing_patients_total:,.2f} |
| Exames não integrados | {missing_exams_count} | R$ {missing_exams_total:,.2f} |
| Divergências de valor | {divergences_count} | R$ {divergences_total:,.2f} |
| Exames "fantasma" no SIMUS | {extra_simus_count} | N/A |

### Top 5 Exames Problemáticos
{top_exams}

## SUA TAREFA

Produza um **RELATÓRIO EXECUTIVO COMPLETO E DETALHADO** em Markdown, com pelo menos 1000 palavras, incluindo:

### 1. RESUMO EXECUTIVO (3-4 parágrafos)
- Visão geral da situação financeira
- Principal fonte de perda identificada
- Urgência da situação (baixa/média/alta/crítica)

### 2. ANÁLISE DETALHADA DE IMPACTO FINANCEIRO
Crie tabelas mostrando:
- Impacto por categoria de divergência
- Projeção de perda mensal e anual se não corrigido
- Comparação entre valores esperados vs. cobrados

### 3. DIAGNÓSTICO DAS CAUSAS RAIZ
Para cada categoria de problema, identifique:
- **Causa técnica provável** (falha de integração, erro de digitação, etc)
- **Causa processual** (falta de conferência, processo desatualizado)
- **Evidências** baseadas nos dados

### 4. PLANO DE AÇÃO PRIORIZADO
Lista numerada com:
- Ação específica
- Responsável sugerido
- Prazo recomendado
- Impacto esperado (em R$)

### 5. INDICADORES PARA MONITORAMENTO
Sugira KPIs que o laboratório deve acompanhar mensalmente

### 6. CONCLUSÃO E RECOMENDAÇÕES FINAIS
Síntese executiva para apresentação à diretoria

---
**IMPORTANTE**: 
- Use linguagem profissional de auditoria
- Inclua valores monetários específicos sempre que possível
- Baseie todas as conclusões nos dados fornecidos
- O relatório deve ser acionável e orientado a resultados
"""

class ClinicalConsistencySchema(BaseModel):
    """Schema para Structured Output da análise clínica"""
    is_consistent: bool = Field(..., description="Se a alteração do valor faz sentido clínico.")
    reason: str = Field(..., description="Explicação detalhada do raciocínio clínico (Chain of Thought).")
    warning_level: str = Field(..., description="Nível de alerta: 'low', 'medium', 'high', 'critical'.")
    suggested_action: str = Field(..., description="Ação recomendada para o analista.")

CLINICAL_AUDIT_PROMPT = """
Você é um auditor clínico sênior. Sua tarefa é analisar se uma alteração manual em um resultado de exame faz sentido ou parece um erro de digitação/fraude.

## CONTEXTO DO EXAME
Exame: {exam_name}
Lote: {lot_number}
Nível: {level}

## ALTERAÇÃO
Valor Antigo: {old_value}
Valor Novo: {new_value}
Variação: {percentage_change:.2f}%

## INSTRUÇÕES
1. Pense passo a passo sobre a viabilidade biológica dessa variação.
2. Considere se o novo valor está dentro de limites fisiológicos extremos.
3. Identifique possíveis erros de digitação (ex: vírgula no lugar errado).
4. Retorne sua análise obrigatoriamente no formato JSON estruturado.
"""


class AIService:
    """Serviço unificado de IA com suporte a OpenAI e Gemini"""
    
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
    
    def get_available_models(self, provider: str) -> List[Dict[str, str]]:
        """Retorna lista de modelos disponíveis para um provedor"""
        return AVAILABLE_MODELS.get(provider, [])
    
    def build_prompt(self, analysis_data: Dict[str, Any]) -> str:
        """Constrói o prompt com os dados da análise"""
        # Formatar top exames
        top_exams_str = ""
        for i, exam in enumerate(analysis_data.get("top_exams", [])[:5], 1):
            top_exams_str += f"{i}. {exam.get('name', 'N/A')}: {exam.get('count', 0)} ocorrências\n"
        
        if not top_exams_str:
            top_exams_str = "Nenhum exame problemático identificado."
        
        return ANALYSIS_PROMPT_TEMPLATE.format(
            compulab_total=analysis_data.get("compulab_total", 0),
            simus_total=analysis_data.get("simus_total", 0),
            difference=analysis_data.get("compulab_total", 0) - analysis_data.get("simus_total", 0),
            missing_patients_count=analysis_data.get("missing_patients_count", 0),
            missing_patients_total=analysis_data.get("missing_patients_total", 0),
            missing_exams_count=analysis_data.get("missing_exams_count", 0),
            missing_exams_total=analysis_data.get("missing_exams_total", 0),
            divergences_count=analysis_data.get("divergences_count", 0),
            divergences_total=analysis_data.get("divergences_total", 0),
            extra_simus_count=analysis_data.get("extra_simus_exams_count", 0),
            top_exams=top_exams_str
        )
    
    async def analyze_with_openai(self, prompt: str, model: str = "gpt-4o") -> str:
        """Executa análise usando OpenAI com retry automático"""
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY não configurada no .env")
        
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.openai_key)
            
            # Retry manual simples
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = await client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "Você é um auditor financeiro especialista em laboratórios clínicos. Responda sempre em português brasileiro."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=8000
                    )
                    
                    result = response.choices[0].message.content
                    
                    # Log usage
                    usage = response.usage
                    print(f"DEBUG OpenAI: modelo={model}, tokens_in={usage.prompt_tokens}, tokens_out={usage.completion_tokens}")
                    
                    return result
                    
                except Exception as e:
                    if "rate_limit" in str(e).lower() or "429" in str(e):
                        wait_time = 2 ** attempt
                        print(f"DEBUG: Rate limit, aguardando {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise
            
            raise Exception("Excedido número máximo de tentativas")
            
        except ImportError:
            raise ImportError("Pacote 'openai' não instalado. Execute: pip install openai")
        except Exception as e:
            print(f"ERROR OpenAI: {e}")
            raise
    
    async def analyze_with_gemini(self, prompt: str, model: str = "gemini-2.5-flash") -> str:
        """Executa análise usando Gemini com retry automático (google.genai SDK)"""
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY não configurada no .env")
        
        try:
            from google import genai
            
            # Criar cliente com API key
            client = genai.Client(api_key=self.gemini_key)
            
            # Retry manual simples
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Usar o novo SDK
                    response = await asyncio.to_thread(
                        client.models.generate_content,
                        model=model,
                        contents=prompt,
                        config={
                            "temperature": 0.7,
                            "max_output_tokens": 8000,
                        }
                    )
                    
                    result = response.text
                    
                    # Log usage (se disponível)
                    if hasattr(response, 'usage_metadata'):
                        print(f"DEBUG Gemini: modelo={model}, tokens={response.usage_metadata}")
                    
                    return result
                    
                except Exception as e:
                    error_str = str(e).lower()
                    if "resource_exhausted" in error_str or "429" in error_str or "quota" in error_str:
                        wait_time = 2 ** attempt
                        print(f"DEBUG: Rate limit Gemini, aguardando {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise
            
            raise Exception("Excedido número máximo de tentativas")
            
        except ImportError:
            raise ImportError("Pacote 'google-genai' não instalado. Execute: pip install google-genai")
        except Exception as e:
            print(f"ERROR Gemini: {e}")
            raise

    async def analyze_clinical_consistency(self, audit_data: Dict[str, Any]) -> ClinicalConsistencySchema:
        """
        Analisa a consistência de uma alteração clínica usando Structured Outputs.
        """
        if not self.gemini_key:
            return ClinicalConsistencySchema(
                is_consistent=True, 
                reason="AI Analysis skipped: Key missing", 
                warning_level="low",
                suggested_action="Proceder com cautela"
            )

        prompt = CLINICAL_AUDIT_PROMPT.format(
            exam_name=audit_data.get("exam_name"),
            lot_number=audit_data.get("lot_number"),
            level=audit_data.get("level"),
            old_value=audit_data.get("old_value"),
            new_value=audit_data.get("new_value"),
            percentage_change=audit_data.get("percentage_change", 0)
        )

        try:
            from google import genai
            client = genai.Client(api_key=self.gemini_key)
            
            # Usando Structured Output do novo SDK
            response = await asyncio.to_thread(
                client.models.generate_content,
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ClinicalConsistencySchema,
                    "temperature": 0.2, # Baixa temperatura para auditoria
                }
            )
            
            # O SDK retorna um objeto que pode ser convertido/validado
            return response.parsed
            
        except Exception as e:
            print(f"Clinical AI Audit Error: {e}")
            return ClinicalConsistencySchema(
                is_consistent=True,
                reason=f"Erro na análise de IA: {str(e)}",
                warning_level="medium",
                suggested_action="Verificar manualmente"
            )
    
    async def run_analysis(self, provider: str, model: str, analysis_data: Dict[str, Any]) -> str:
        """Executa análise usando o provedor e modelo especificados"""
        prompt = self.build_prompt(analysis_data)
        
        print(f"DEBUG AIService: provider={provider}, model={model}")
        
        if provider == "OpenAI":
            return await self.analyze_with_openai(prompt, model)
        elif provider == "Gemini":
            return await self.analyze_with_gemini(prompt, model)
        else:
            raise ValueError(f"Provedor desconhecido: {provider}")


# Singleton para uso em toda a aplicação
ai_service = AIService()
