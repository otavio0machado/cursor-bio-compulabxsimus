from typing import List, Dict, Any, Optional
from ..models import QCRecord

class WestgardService:
    """
    Serviço especializado na verificação das Regras de Westgard para Controle de Qualidade.
    Implementa lógica para detectar violações baseadas em desvios padrão (SD).
    """

    @staticmethod
    def check_rules(current_record: QCRecord, history: List[QCRecord]) -> List[Dict[str, Any]]:
        """
        Avalia as regras de Westgard para o registro atual considerando o histórico.
        Retorna uma lista de violações encontradas.
        
        Args:
            current_record: O registro sendo avaliado (deve ter value, target_value e target_sd).
            history: Lista de registros anteriores (ordenados do mais recente para o mais antigo),
                     do mesmo exame e nível.
        
        Returns:
            List[Dict]: Lista de violações, ex: [{"rule": "1-3s", "description": "...", "severity": "rejection"}]
        """
        violations = []
        
        # Dados básicos
        val = current_record.value
        mean = current_record.target_value
        sd = current_record.target_sd
        
        if sd == 0:
            return [] # Impossível calcular sem SD

        # Cálculo do Z-Score (Desvio em unidades de SD)
        z_score = (val - mean) / sd
        current_record.z_score = z_score # Atualiza no objeto se possível
        
        # 1. Regra 1-2s (Alerta)
        # Um ponto além de ±2SD. GERALMENTE é apenas aviso, mas inicia checagem de outras regras.
        if abs(z_score) > 2:
            violations.append({
                "rule": "1-2s",
                "description": "Alerta: Valor excede 2 Desvios Padrão.",
                "severity": "warning"
            })
            
            # --- Regras de Rejeição (só checamos se 1-2s for ativado, tipicamente, mas aqui checaremos todas para robustez) ---

            # 2. Regra 1-3s (Rejeição)
            # Um ponto além de ±3SD.
            if abs(z_score) > 3:
                violations.append({
                    "rule": "1-3s",
                    "description": "Erro Aleatório: Valor excede 3 Desvios Padrão.",
                    "severity": "rejection"
                })

            # 3. Regra 2-2s (Rejeição)
            # Dois pontos consecutivos excedem ±2SD no MESMO lado da média.
            if history:
                prev_record = history[0] # O mais recente do histórico
                if prev_record.target_sd > 0:
                    prev_z = (prev_record.value - prev_record.target_value) / prev_record.target_sd
                    
                    # Verifica se ambos estão acima de +2SD ou ambos abaixo de -2SD
                    if (z_score > 2 and prev_z > 2) or (z_score < -2 and prev_z < -2):
                         violations.append({
                            "rule": "2-2s",
                            "description": "Erro Sistemático: Dois valores consecutivos excedem 2 SD do mesmo lado.",
                            "severity": "rejection"
                        })

            # 4. Regra R-4s (Rejeição)
            # Diferença entre dois pontos consecutivos excede 4SD (um > +2SD e outro < -2SD ou vice-versa).
            if history:
                prev_record = history[0]
                if prev_record.target_sd > 0:
                    prev_z = (prev_record.value - prev_record.target_value) / prev_record.target_sd
                    
                    if abs(z_score - prev_z) > 4:
                        violations.append({
                            "rule": "R-4s",
                            "description": "Erro Aleatório: Diferença entre pontos consecutivos excede 4 SD.",
                            "severity": "rejection"
                        })

        # 5. Regra 4-1s (Rejeição)
        # Quatro pontos consecutivos excedem ±1SD do MESMO lado.
        # Necessita histórico de pelo menos 3 itens + atual
        if len(history) >= 3:
            consecutive_1sd = True
            check_side_positive = z_score > 1
            check_side_negative = z_score < -1
            
            if check_side_positive or check_side_negative:
                count = 1
                for rec in history[:3]:
                    if rec.target_sd <= 0:
                        consecutive_1sd = False
                        break
                    r_z = (rec.value - rec.target_value) / rec.target_sd
                    
                    if check_side_positive and r_z > 1:
                        count += 1
                    elif check_side_negative and r_z < -1:
                        count += 1
                    else:
                        consecutive_1sd = False
                        break
                
                if consecutive_1sd and count == 4:
                     violations.append({
                        "rule": "4-1s",
                        "description": "Erro Sistemático: Quatro valores consecutivos excedem 1 SD do mesmo lado.",
                        "severity": "rejection"
                    })

        # 6. Regra 10x (ou 8x, 12x) (Rejeição/Alerta)
        # Dez pontos consecutivos do mesmo lado da média.
        if len(history) >= 9:
            consecutive_side = True
            is_positive = z_score > 0
            
            count = 1
            for rec in history[:9]:
                r_z = rec.value - rec.target_value # usando dif bruta pois só importa o sinal
                if (is_positive and r_z > 0) or (not is_positive and r_z < 0):
                    count += 1
                else:
                    consecutive_side = False
                    break
            
            if consecutive_side and count == 10:
                violations.append({
                    "rule": "10x",
                    "description": "Erro Sistemático: Dez valores consecutivos do mesmo lado da média.",
                    "severity": "warning" # Pode ser rejection dependendo do rigor
                })

        return violations
