"""
Serviço de Tools para integração com n8n AI Agent.

Este módulo fornece funções que podem ser chamadas pelo n8n
através de HTTP requests, permitindo que o AI Agent execute
operações complexas no backend.

Seguindo SKILL "O Oráculo" - Integração AI e Prompts
"""

from typing import Optional
from dataclasses import dataclass
import math


@dataclass
class WestgardResult:
    """Resultado da análise Westgard."""
    sucesso: bool
    z_score: Optional[float] = None
    z_score_absoluto: Optional[float] = None
    status: str = ""
    severity: str = "none"
    cor_indicador: str = "green"
    violations: list = None
    interpretacao: str = ""
    recomendacao: str = ""
    metafora: str = ""
    erro: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Converte para dicionário."""
        return {
            "sucesso": self.sucesso,
            "dados_entrada": None,  # Será preenchido pelo caller
            "resultado": {
                "z_score": f"{self.z_score:.3f}" if self.z_score else None,
                "z_score_absoluto": f"{self.z_score_absoluto:.3f}" if self.z_score_absoluto else None,
                "status": self.status,
                "severity": self.severity,
                "cor_indicador": self.cor_indicador
            } if self.sucesso else None,
            "violations": self.violations or [],
            "interpretacao": self.interpretacao,
            "recomendacao": self.recomendacao,
            "metafora": self.metafora,
            "erro": self.erro
        }


class N8NToolsService:
    """
    Serviço que implementa as ferramentas (tools) utilizadas pelo AI Agent do n8n.
    
    Cada método corresponde a uma ferramenta que o agente pode invocar.
    """
    
    @staticmethod
    def interpretador_westgard(
        value: float,
        target_value: float,
        target_sd: float
    ) -> dict:
        """
        Valida resultados de Controle de Qualidade usando as regras de Westgard.
        
        Regras implementadas:
        - 1-2s (Warning): |z-score| > 2
        - 1-3s (Rejection): |z-score| > 3
        
        Args:
            value: Valor medido do resultado
            target_value: Valor alvo (média esperada)
            target_sd: Desvio padrão do controle
            
        Returns:
            Dicionário com resultado da análise
        """
        # Validação de entrada
        if target_sd == 0:
            return {
                "sucesso": False,
                "erro": "❌ Desvio padrão não pode ser zero.",
                "exemplo": '{ "value": 150, "target_value": 145, "target_sd": 3 }'
            }
        
        # Cálculo do z-score
        z = (value - target_value) / target_sd
        z_abs = abs(z)
        
        violations = []
        status = "OK ✅"
        severity = "none"
        cor_fundo = "green"
        
        # Regra 1-3s (Rejeição - Erro Aleatório ou Sistemático Grave)
        if z_abs > 3:
            violations.append({
                "regra": "1-3s",
                "tipo": "REJEIÇÃO",
                "descricao": "Valor excede 3 Desvios Padrão"
            })
            status = "REJEITADO ❌"
            severity = "critical"
            cor_fundo = "red"
        # Regra 1-2s (Alerta - Possível problema)
        elif z_abs > 2:
            violations.append({
                "regra": "1-2s",
                "tipo": "ALERTA",
                "descricao": "Valor excede 2 Desvios Padrão"
            })
            status = "ALERTA ⚠️"
            severity = "warning"
            cor_fundo = "yellow"
        
        # Interpretação baseada na zona
        if z_abs <= 1:
            interpretacao = "Excelente: Dentro de 1 SD (zona verde)"
        elif z_abs <= 2:
            interpretacao = "Aceitável: Entre 1-2 SD (zona amarela)"
        else:
            interpretacao = "Fora de controle: Acima de 2 SD"
        
        # Recomendação
        if violations:
            recomendacao = (
                "🔧 Ações: 1) Verificar calibração do equipamento "
                "2) Conferir lote de reagentes 3) Repetir o teste"
            )
        else:
            recomendacao = "✅ Resultado dentro dos limites. Liberar análise normalmente."
        
        return {
            "sucesso": True,
            "dados_entrada": {
                "valor_medido": value,
                "media_esperada": target_value,
                "desvio_padrao": target_sd
            },
            "resultado": {
                "z_score": f"{z:.3f}",
                "z_score_absoluto": f"{z_abs:.3f}",
                "status": status,
                "severity": severity,
                "cor_indicador": cor_fundo
            },
            "violations": violations,
            "interpretacao": interpretacao,
            "recomendacao": recomendacao,
            "metafora": (
                "🎯 Pense no z-score como uma flecha: quanto mais perto do centro "
                "do alvo (zero), melhor. Flechas que saem muito do centro (>2 SD) "
                "indicam problema na pontaria (equipamento)."
            )
        }
    
    @staticmethod
    def gerar_contestacao(
        convenio: str = "[Nome do Convênio]",
        exame: str = "[Nome do Exame]",
        valor_cobrado: float = 0,
        valor_pago: float = 0,
        motivo: str = "divergência de valores",
        paciente: str = "[Nome do Paciente]"
    ) -> dict:
        """
        Gera uma carta profissional para contestar uma glosa de convênio.
        
        Args:
            convenio: Nome do convênio
            exame: Nome do exame
            valor_cobrado: Valor que foi cobrado
            valor_pago: Valor que foi pago pelo convênio
            motivo: Motivo alegado pela glosa
            paciente: Nome do paciente
            
        Returns:
            Dicionário com a carta formatada e próximos passos
        """
        from datetime import datetime
        
        diferenca = valor_cobrado - valor_pago
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        
        def format_brl(v: float) -> str:
            return f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        
        carta = f"""
╔══════════════════════════════════════════════════════════════╗
║           CARTA DE CONTESTAÇÃO DE GLOSA                       ║
╚══════════════════════════════════════════════════════════════╝

À {convenio}
Setor de Auditoria e Faturamento

Ref.: Contestação de Glosa - Procedimento {exame}
Data: {data_hoje}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Prezados Senhores,

Vimos, por meio desta, CONTESTAR FORMALMENTE a glosa aplicada ao procedimento abaixo:

┌─────────────────────────────────────────────────────────────┐
│ 📋 DADOS DO PROCEDIMENTO                                     │
├─────────────────────────────────────────────────────────────┤
│ Paciente:        {paciente[:40]:<40}│
│ Procedimento:    {exame[:40]:<40}│
│ Valor Cobrado:   R$ {format_brl(valor_cobrado):<37}│
│ Valor Pago:      R$ {format_brl(valor_pago):<37}│
│ Diferença:       R$ {format_brl(diferenca):<37}│
│ Motivo Alegado:  {motivo[:40]:<40}│
└─────────────────────────────────────────────────────────────┘

📌 FUNDAMENTAÇÃO:

1. O procedimento foi realizado em conformidade com as normas técnicas
   vigentes e o contrato estabelecido entre as partes.

2. A cobrança está de acordo com a tabela de preços pactuada,
   conforme anexo contratual de [inserir data do contrato].

3. Toda documentação comprobatória encontra-se disponível para
   verificação (requisição médica, resultado do exame, nota fiscal).

4. Não houve duplicidade de cobrança ou erro de digitação.

📎 DOCUMENTOS ANEXOS:
   ☐ Cópia da requisição médica
   ☐ Laudo do exame
   ☐ Tabela de preços contratada
   ☐ Nota fiscal correspondente

🎯 SOLICITAÇÃO:
Solicitamos a REVISÃO da glosa e o PAGAMENTO da diferença de
R$ {format_brl(diferenca)} no prazo legal de 30 dias.

Aguardamos manifestação.

Atenciosamente,

_________________________________
Laboratório Biodiagnóstico
Setor de Faturamento
Telefone: (XX) XXXX-XXXX
Email: faturamento@biodiagnostico.com.br

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        return {
            "sucesso": True,
            "carta_contestacao": carta,
            "resumo": {
                "convenio": convenio,
                "exame": exame,
                "diferenca": f"R$ {format_brl(diferenca)}"
            },
            "proximos_passos": [
                "1. Revise e personalize os campos entre colchetes [ ]",
                "2. Anexe os documentos listados",
                "3. Protocole junto ao convênio (guarde o número de protocolo!)",
                "4. Acompanhe a resposta em até 30 dias",
                "5. Se necessário, escale para recurso de 2ª instância"
            ]
        }
    
    @staticmethod
    def comparar_tabelas(exame: str = "HEMOGRAMA") -> dict:
        """
        Compara valores entre a tabela do laboratório e as tabelas dos convênios.
        
        Args:
            exame: Nome do exame a comparar
            
        Returns:
            Dicionário com comparativo de preços
        """
        exame_consultado = exame.upper()
        
        # Tabelas simuladas (em produção viriam do Supabase)
        tabela_lab = {
            "HEMOGRAMA": 35.00,
            "GLICOSE": 12.50,
            "COLESTEROL TOTAL": 18.00,
            "TSH": 45.00,
            "T4 LIVRE": 42.00,
            "CREATININA": 15.00,
            "UREIA": 12.00,
            "ACIDO URICO": 14.00
        }
        
        tabelas_convenios = {
            "UNIMED": {
                "HEMOGRAMA": 32.00, "GLICOSE": 10.00, "COLESTEROL TOTAL": 15.00,
                "TSH": 40.00, "T4 LIVRE": 38.00, "CREATININA": 13.00
            },
            "BRADESCO": {
                "HEMOGRAMA": 30.00, "GLICOSE": 11.00, "COLESTEROL TOTAL": 16.50,
                "TSH": 42.00, "T4 LIVRE": 40.00, "CREATININA": 14.00
            },
            "AMIL": {
                "HEMOGRAMA": 28.00, "GLICOSE": 9.50, "COLESTEROL TOTAL": 14.00,
                "TSH": 38.00, "T4 LIVRE": 36.00, "CREATININA": 12.00
            },
            "SULAMERICA": {
                "HEMOGRAMA": 33.00, "GLICOSE": 11.50, "COLESTEROL TOTAL": 17.00,
                "TSH": 43.00, "T4 LIVRE": 41.00, "CREATININA": 14.50
            }
        }
        
        valor_lab = tabela_lab.get(exame_consultado, 0)
        comparativo = []
        
        for convenio, tabela in tabelas_convenios.items():
            valor_conv = tabela.get(exame_consultado, 0)
            if valor_conv > 0:
                diferenca = valor_lab - valor_conv
                percentual = ((diferenca / valor_lab) * 100) if valor_lab > 0 else 0
                
                if diferenca > 5:
                    status = "⚠️ DEFASADO"
                elif diferenca > 2:
                    status = "🟡 ATENÇÃO"
                else:
                    status = "✅ OK"
                
                comparativo.append({
                    "convenio": convenio,
                    "valor_lab": f"R$ {valor_lab:.2f}",
                    "valor_convenio": f"R$ {valor_conv:.2f}",
                    "diferenca": f"R$ {diferenca:.2f}",
                    "percentual": f"{percentual:.1f}%",
                    "status": status
                })
        
        # Ordenar do mais defasado para o menos
        comparativo.sort(key=lambda x: float(x["diferenca"].replace("R$ ", "")), reverse=True)
        
        convenio_mais_defasado = comparativo[0] if comparativo else None
        diferenca_maior = float(convenio_mais_defasado["diferenca"].replace("R$ ", "")) if convenio_mais_defasado else 0
        
        if convenio_mais_defasado and diferenca_maior > 5:
            recomendacao = f"📞 Priorizar renegociação de tabela com {convenio_mais_defasado['convenio']}"
        else:
            recomendacao = "✅ Tabelas dentro do esperado"
        
        return {
            "sucesso": True,
            "exame_consultado": exame_consultado,
            "valor_tabela_laboratorio": f"R$ {valor_lab:.2f}",
            "comparativo_convenios": comparativo,
            "convenio_mais_defasado": convenio_mais_defasado,
            "recomendacao": recomendacao,
            "metafora": (
                "💰 Tabelas defasadas são como cupons de desconto que você dá sem querer: "
                "o cliente (convênio) paga menos do que deveria."
            )
        }


# Instância global do serviço
n8n_tools_service = N8NToolsService()
