"""
Comparison utilities for COMPULAB vs SIMUS analysis
Laboratório Biodiagnóstico
Otimizado para resultados determinísticos e consistentes
"""
import json
import re
from decimal import Decimal
from .pdf_processor import normalize_exam_name_for_comparison, exam_names_match


def compare_patients(compulab_patients, simus_patients):
    """
    Compara pacientes entre COMPULAB e SIMUS usando NOMES e CÓDIGOS de exames.
    Resultados são sempre consistentes e determinísticos.
    """
    results = {
        'missing_patients': [],  # Pacientes no COMPULAB mas não no SIMUS
        'missing_exams': [],  # Exames faltantes por paciente
        'value_divergences': []  # Divergências de valores
    }
    
    compulab_names = set(compulab_patients.keys())
    simus_names = set(simus_patients.keys())
    
    # Pacientes faltantes no SIMUS
    missing_in_simus = sorted(compulab_names - simus_names)
    for patient in missing_in_simus:
        results['missing_patients'].append({
            'patient': patient,
            'exams_count': len(compulab_patients[patient]['exams']),
            'total_value': compulab_patients[patient]['total'],
            'exams': compulab_patients[patient]['exams']
        })
    
    # Comparar pacientes comuns
    common_patients = sorted(compulab_names & simus_names)
    
    for patient in common_patients:
        compulab_exam_list = compulab_patients[patient]['exams']
        simus_exam_list = simus_patients[patient]['exams']
        
        # Criar cópia mutável da lista do SIMUS para marcar quais já foram usados
        simus_used_indices = set()
        
        # Agrupar exames do COMPULAB por CÓDIGO (se disponível) ou NOME NORMALIZADO
        compulab_items = []
        for exam in compulab_exam_list:
            code = exam.get('code', '')
            norm_name = normalize_exam_name_for_comparison(exam['exam_name'])
            # Prioridade para código, senão nome
            compulab_items.append({
                'original': exam,
                'match_key': f"CODE_{code}" if code and len(code) >= 5 else f"NAME_{norm_name}",
                'code': code,
                'norm_name': norm_name
            })
        
        # Agrupar por match_key para tratar exames múltiplos do mesmo tipo
        compulab_grouped = {}
        for item in compulab_items:
            key = item['match_key']
            if key not in compulab_grouped:
                compulab_grouped[key] = []
            compulab_grouped[key].append(item['original'])
            
        # Ordenar chaves para determinismo
        sorted_keys = sorted(compulab_grouped.keys())
        
        for key in sorted_keys:
            comp_exams = compulab_grouped[key]
            # Extrair o que estamos buscando
            is_code_search = key.startswith("CODE_")
            search_val = key.replace("CODE_", "").replace("NAME_", "")
            
            simus_matches = []
            
            # Procurar matches no SIMUS
            for i, sim_exam in enumerate(simus_exam_list):
                if i in simus_used_indices:
                    continue
                
                match_found = False
                if is_code_search:
                    sim_code = sim_exam.get('code', '')
                    if sim_code == search_val:
                        match_found = True
                else:
                    sim_norm = normalize_exam_name_for_comparison(sim_exam['exam_name'])
                    if exam_names_match(search_val, sim_norm):
                        match_found = True
                
                if match_found:
                    simus_matches.append((i, sim_exam))
                    simus_used_indices.add(i)
            
            if not simus_matches:
                # Nenhum match encontrado - exames faltantes
                for exam in comp_exams:
                    results['missing_exams'].append({
                        'patient': patient,
                        'exam_name': exam['exam_name'],
                        'value': exam['value'],
                        'code': exam.get('code', '')
                    })
            else:
                # Comparar valores
                comp_total = sum(Decimal(str(ex['value'])) for ex in comp_exams)
                sim_total = sum(Decimal(str(ex[1]['value'])) for ex in simus_matches)
                
                if abs(comp_total - sim_total) > Decimal('0.01'):
                    # Divergência de valor
                    all_names = [ex['exam_name'] for ex in comp_exams] + [ex[1]['exam_name'] for ex in simus_matches]
                    display_name = max(all_names, key=lambda x: (len(x), x))
                    
                    # Tentar pegar o código de qualquer um deles
                    codes = {ex.get('code', '') for ex in comp_exams} | {ex[1].get('code', '') for ex in simus_matches}
                    display_code = next((c for c in codes if c), "")
                    
                    results['value_divergences'].append({
                        'patient': patient,
                        'exam_name': display_name,
                        'code': display_code,
                        'compulab_value': float(comp_total),
                        'simus_value': float(sim_total),
                        'difference': float(comp_total - sim_total),
                        'compulab_count': len(comp_exams),
                        'simus_count': len(simus_matches)
                    })
        
        # Opcional: Identificar exames no SIMUS que sobraram (não estão no COMPULAB)
        # Por enquanto não estamos salvando isso para não mudar a lógica de negócio principal,
        # mas poderíamos adicionar results['extra_simus_exams']
    
    
    # ORDENAR resultados finais para garantir consistência total
    results['missing_patients'].sort(key=lambda x: (x['patient'], x['total_value']))
    results['missing_exams'].sort(key=lambda x: (x['patient'], x['exam_name'], x['value']))
    results['value_divergences'].sort(key=lambda x: (x['patient'], x['exam_name'], x['difference']))
    
    return results


def compute_difference_breakdown(compulab_total, simus_total, comparison_results):
    """Calcula a explicação da diferença total (COMPULAB - SIMUS)"""
    # Converter para Decimal para garantir consistência
    compulab_total = Decimal(str(compulab_total)) if not isinstance(compulab_total, Decimal) else compulab_total
    simus_total = Decimal(str(simus_total)) if not isinstance(simus_total, Decimal) else simus_total
    
    diff_total = compulab_total - simus_total
    
    # Converter todos os valores para Decimal antes de somar
    missing_patients_total = sum(
        (Decimal(str(item['total_value'])) for item in comparison_results['missing_patients']),
        Decimal('0')
    )
    missing_exams_total = sum(
        (Decimal(str(item['value'])) for item in comparison_results['missing_exams']),
        Decimal('0')
    )
    divergences_total = sum(
        (Decimal(str(item['difference'])) for item in comparison_results['value_divergences']),
        Decimal('0')
    )
    
    explained = missing_patients_total + missing_exams_total + divergences_total
    residual = diff_total - explained
    
    return {
        "diff_total": diff_total,
        "missing_patients_total": missing_patients_total,
        "missing_exams_total": missing_exams_total,
        "divergences_total": divergences_total,
        "explained_total": explained,
        "residual": residual,
    }



def format_divergences_to_json(delimited_data: str) -> str:
    """
    Converte dados delimitados de divergências laboratoriais em JSON estruturado.

    Entrada esperada (delimitado por ; ou ,):
    Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia
    ANA SILVA;HEMOGRAMA;202020380;6,15;6,16;Valor Divergente

    Saída: JSON array com objetos estruturados

    Args:
        delimited_data: String com dados delimitados (CSV ou TSV)

    Returns:
        JSON string formatado
    """
    if not delimited_data or not delimited_data.strip():
        return "[]"

    lines = delimited_data.strip().split('\n')
    if not lines:
        return "[]"

    # Detectar delimitador (ponto-e-vírgula ou vírgula)
    first_line = lines[0]
    delimiter = ';' if ';' in first_line else ','

    result = []
    header_found = False
    expected_fields = ["Paciente", "Nome_Exame", "Codigo_Exame", "Valor_Compulab", "Valor_Simus", "Tipo_Divergencia"]

    for line in lines:
        line = line.strip()
        if not line:
            continue

        parts = [p.strip() for p in line.split(delimiter)]

        # Verificar se é cabeçalho
        if not header_found and any(field in line for field in expected_fields):
            header_found = True
            continue

        # Processar linha de dados
        if len(parts) >= 6:
            obj = {
                "Paciente": parts[0] if len(parts) > 0 else "",
                "Nome_Exame": parts[1] if len(parts) > 1 else "",
                "Codigo_Exame": parts[2] if len(parts) > 2 else "",
                "Valor_Compulab": parts[3] if len(parts) > 3 else "",
                "Valor_Simus": parts[4] if len(parts) > 4 else "",
                "Tipo_Divergencia": parts[5] if len(parts) > 5 else ""
            }
            result.append(obj)

    return json.dumps(result, ensure_ascii=False, indent=2)

