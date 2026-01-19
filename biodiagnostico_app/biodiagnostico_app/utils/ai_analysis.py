"""
AI Analysis utilities using OpenAI
Laboratório Biodiagnóstico
"""
from datetime import datetime
import openai

def generate_ai_analysis(
    compulab_total,
    simus_total,
    compulab_count,
    simus_count,
    comparison_results,
    breakdown,
    api_key: str
):
    """Gera análise inteligente usando OpenAI"""
    try:
        if not api_key:
            return None, "API Key não fornecida."
            
        print(f"DEBUG: Configurando OpenAI com API Key: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else ''}")
        
        client = openai.OpenAI(api_key=api_key)
        
    except ImportError:
        return None, "Biblioteca openai não está instalada e configurada."
    except Exception as e:
        return None, f"Erro ao configurar OpenAI API: {str(e)}"
    
    # Criar resumo dos dados
    summary_data = f"""
RESUMO DA ANÁLISE COMPULAB vs SIMUS:

Totais:
- COMPULAB: R$ {compulab_total:,.2f}
- SIMUS: R$ {simus_total:,.2f}
- Diferença: R$ {compulab_total - simus_total:,.2f}

Pacientes:
- COMPULAB: {compulab_count} pacientes
- SIMUS: {simus_count} pacientes
- Pacientes faltantes no SIMUS: {len(comparison_results.get('missing_patients', []))}

Exames Faltantes: {len(comparison_results.get('missing_exams', []))} exame(s)
Divergências de Valores: {len(comparison_results.get('value_divergences', []))} divergência(s)

Breakdown da Diferença:
- Pacientes faltantes: R$ {breakdown.get('missing_patients_total', 0):,.2f}
- Exames faltantes: R$ {breakdown.get('missing_exams_total', 0):,.2f}
- Divergências: R$ {breakdown.get('divergences_total', 0):,.2f}
- Total explicado: R$ {breakdown.get('explained_total', 0):,.2f}
- Diferença residual: R$ {breakdown.get('residual', 0):,.2f}
"""
    
    # Adicionar exemplos de exames faltantes
    missing_exams = comparison_results.get('missing_exams', [])
    if missing_exams:
        summary_data += "\n\nExemplos de Exames Faltantes (primeiros 10):\n"
        for i, exam in enumerate(missing_exams[:10], 1):
            summary_data += f"{i}. Paciente: {exam['patient']} | Exame: {exam['exam_name']} | Valor: R$ {exam['value']:,.2f}\n"
    
    # Adicionar exemplos de divergências
    divergences = comparison_results.get('value_divergences', [])
    if divergences:
        summary_data += "\n\nExemplos de Divergências de Valores (primeiros 10):\n"
        for i, div in enumerate(divergences[:10], 1):
            summary_data += f"{i}. Paciente: {div['patient']} | Exame: {div['exam_name']} | COMPULAB: R$ {div['compulab_value']:,.2f} | SIMUS: R$ {div['simus_value']:,.2f} | Diferença: R$ {div['difference']:,.2f}\n"
    
    # Prompt para a IA
    prompt = f"""Você é um especialista em análise de faturamento médico/laboratorial. 

Analise os seguintes dados de comparação entre COMPULAB (sistema de faturamento) e SIMUS (sistema de pagamento):

{summary_data}

Forneça uma análise detalhada e acionável com:
1. **Resumo Executivo**: Principais pontos que explicam a diferença entre os valores
2. **Principais Causas**: Identifique os 3-5 principais motivos para as divergências
3. **Recomendações**: Sugestões práticas para resolver os problemas identificados
4. **Pontos de Atenção**: Itens que precisam de verificação manual imediata
5. **Impacto Financeiro**: Avaliação do impacto de cada tipo de divergência

Seja específico, prático e use linguagem profissional mas acessível. Responda em português brasileiro."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente especializado em análise de dados financeiros de laboratórios."},
                {"role": "user", "content": prompt}
            ]
        )
        
        ai_analysis = response.choices[0].message.content
        return ai_analysis, None
        
    except Exception as e:
        return None, f"Erro ao gerar análise por IA (OpenAI): {str(e)}"


def format_ai_report(ai_analysis: str) -> str:
    """Formata o relatório da IA para download"""
    return f"""ANÁLISE POR IA - COMPULAB vs SIMUS
{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

{'='*80}

{ai_analysis}
"""
