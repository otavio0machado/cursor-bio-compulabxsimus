"""
Regras de Westgard para Controle de Qualidade Laboratorial
Implementação das regras estatísticas para detecção de erros sistemáticos e aleatórios.
"""
from typing import List, Dict, Any, Optional

class WestgardRules:
    """
    Avalia uma série de resultados de CQ e identifica violações das regras de Westgard.
    Padrões:
    - 12s: Alerta (1 ponto fora de 2DP)
    - 13s: Rejeição (1 ponto fora de 3DP)
    - 22s: Rejeição (2 pontos consecutivos fora de 2DP do mesmo lado)
    - R4s: Rejeição (Diferença de 4DP entre pontos consecutivos)
    - 41s: Rejeição (4 pontos consecutivos fora de 1DP do mesmo lado)
    - 10x: Rejeição (10 pontos consecutivos do mesmo lado da média)
    """

    @staticmethod
    def evaluate(values: List[float], target: float, sd: float) -> Dict[str, Any]:
        """
        Avalia o último valor em relação ao histórico.
        Retorna dicionário com status e regras violadas.
        """
        if not values or sd <= 0:
            return {"status": "ok", "violations": []}
            
        latest = values[-1]
        violations = []
        
        # Diferença em relação à média (Z-score)
        z_scores = [(v - target) / sd for v in values]
        latest_z = z_scores[-1]
        
        # REGRA 13s (Rejeição Crítica)
        if abs(latest_z) > 3:
            violations.append({
                "rule": "13s",
                "type": "rejection",
                "description": "Um ponto fora de 3 Desvios Padrão."
            })
            
        # REGRA 12s (Apenas Alerta se for a única)
        if abs(latest_z) > 2 and abs(latest_z) <= 3:
            violations.append({
                "rule": "12s",
                "type": "warning",
                "description": "Alerta: Ponto fora de 2 Desvios Padrão."
            })
            
        # Regras que requerem histórico (mínimo 2 pontos)
        if len(z_scores) >= 2:
            # REGRA 22s
            if abs(z_scores[-1]) > 2 and abs(z_scores[-2]) > 2 and (z_scores[-1] * z_scores[-2] > 0):
                violations.append({
                    "rule": "22s",
                    "type": "rejection",
                    "description": "Dois pontos consecutivos fora de 2DP do mesmo lado."
                })
            
            # REGRA R4s (Diferença de 4DP entre consecutivos)
            if abs(z_scores[-1] - z_scores[-2]) > 4:
                violations.append({
                    "rule": "R4s",
                    "type": "rejection",
                    "description": "Diferença maior que 4DP entre pontos consecutivos."
                })
                
        # Regras que requerem histórico (mínimo 4 pontos)
        if len(z_scores) >= 4:
            # REGRA 41s (4 pontos > 1DP do mesmo lado)
            last_4 = z_scores[-4:]
            if all(v > 1 for v in last_4) or all(v < -1 for v in last_4):
                violations.append({
                    "rule": "41s",
                    "type": "rejection",
                    "description": "Quatro pontos consecutivos fora de 1DP do mesmo lado."
                })
                
        # Regras que requerem histórico (mínimo 10 pontos)
        if len(z_scores) >= 10:
            # REGRA 10x (10 pontos do mesmo lado da média)
            last_10 = z_scores[-10:]
            if all(v > 0 for v in last_10) or all(v < 0 for v in last_10):
                violations.append({
                    "rule": "10x",
                    "type": "rejection",
                    "description": "Dez pontos consecutivos do mesmo lado da média."
                })
        
        # Determinar status final
        status = "ok"
        if any(v["type"] == "rejection" for v in violations):
            status = "rejection"
        elif any(v["type"] == "warning" for v in violations):
            status = "warning"
            
        return {
            "status": status,
            "violations": violations,
            "z_score": round(latest_z, 2)
        }
