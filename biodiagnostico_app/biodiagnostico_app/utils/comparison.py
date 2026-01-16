"""
Comparison utilities for COMPULAB vs SIMUS analysis
Laboratório Biodiagnóstico
Otimizado para resultados determinísticos e consistentes
"""
from decimal import Decimal
from .pdf_processor import normalize_exam_name_for_comparison, exam_names_match


def compare_patients(compulab_patients, simus_patients):
    """
    Compara pacientes entre COMPULAB e SIMUS usando APENAS NOMES
    Resultados são sempre consistentes e determinísticos (mesma ordem)
    """
    results = {
        'missing_patients': [],  # Pacientes no COMPULAB mas não no SIMUS
        'missing_exams': [],  # Exames faltantes por paciente
        'value_divergences': []  # Divergências de valores
    }
    
    compulab_names = set(compulab_patients.keys())
    simus_names = set(simus_patients.keys())
    
    # Pacientes faltantes no SIMUS - ORDENAR para garantir consistência
    missing_in_simus = sorted(compulab_names - simus_names)
    for patient in missing_in_simus:
        results['missing_patients'].append({
            'patient': patient,
            'exams_count': len(compulab_patients[patient]['exams']),
            'total_value': compulab_patients[patient]['total'],
            'exams': compulab_patients[patient]['exams']
        })
    
    # Comparar pacientes comuns - ORDENAR para garantir consistência
    common_patients = sorted(compulab_names & simus_names)
    
    for patient in common_patients:
        compulab_exam_list = compulab_patients[patient]['exams']
        simus_exam_list = simus_patients[patient]['exams']
        
        # Criar cópia mutável da lista do SIMUS para marcar quais já foram usados
        simus_used_indices = set()
        
        # Agrupar exames por nome normalizado para comparação
        compulab_grouped = {}
        for exam in compulab_exam_list:
            norm_key = normalize_exam_name_for_comparison(exam['exam_name'])
            if norm_key not in compulab_grouped:
                compulab_grouped[norm_key] = []
            compulab_grouped[norm_key].append(exam)
        
        # ORDENAR grupos por chave normalizada para garantir ordem determinística
        sorted_comp_groups = sorted(compulab_grouped.items(), key=lambda x: x[0])
        
        # Para cada grupo de exames do COMPULAB, encontrar correspondentes no SIMUS
        for comp_norm_key, comp_exams in sorted_comp_groups:
            # ORDENAR exames dentro do grupo por nome e valor para consistência
            comp_exams = sorted(comp_exams, key=lambda x: (x['exam_name'], x['value']))
            
            simus_matches = []
            
            # Procurar matches no SIMUS - ORDENAR antes de iterar para matching determinístico
            # Ordenar por índice primeiro (ordem original), depois por nome normalizado
            sorted_simus_with_index = sorted(
                enumerate(simus_exam_list),
                key=lambda x: (normalize_exam_name_for_comparison(x[1]['exam_name']), x[1]['exam_name'], x[1]['value'])
            )
            
            for i, sim_exam in sorted_simus_with_index:
                if i in simus_used_indices:
                    continue
                sim_norm_key = normalize_exam_name_for_comparison(sim_exam['exam_name'])
                if exam_names_match(comp_norm_key, sim_norm_key):
                    simus_matches.append((i, sim_exam))
                    simus_used_indices.add(i)
            
            # ORDENAR matches por índice para manter ordem determinística
            simus_matches = sorted(simus_matches, key=lambda x: x[0])
            
            if not simus_matches:
                # Nenhum match encontrado - exames faltantes
                # ORDENAR exames antes de adicionar
                for exam in comp_exams:
                    results['missing_exams'].append({
                        'patient': patient,
                        'exam_name': exam['exam_name'],
                        'value': exam['value']
                    })
            else:
                # Comparar valores
                compulab_total = sum(ex['value'] for ex in comp_exams)
                simus_total = sum(ex['value'] for i, ex in simus_matches)
                
                if abs(compulab_total - simus_total) > Decimal('0.01'):
                    # Usa o nome mais completo para exibição
                    # Se houver empate no tamanho, usar o primeiro alfabeticamente
                    all_names = [ex['exam_name'] for ex in comp_exams] + [ex['exam_name'] for i, ex in simus_matches]
                    display_name = max(all_names, key=lambda x: (len(x), x))
                    results['value_divergences'].append({
                        'patient': patient,
                        'exam_name': display_name,
                        'compulab_value': compulab_total,
                        'simus_value': simus_total,
                        'difference': compulab_total - simus_total,
                        'compulab_count': len(comp_exams),
                        'simus_count': len(simus_matches)
                    })
    
    # ORDENAR resultados finais para garantir consistência total
    results['missing_patients'].sort(key=lambda x: (x['patient'], x['total_value']))
    results['missing_exams'].sort(key=lambda x: (x['patient'], x['exam_name'], x['value']))
    results['value_divergences'].sort(key=lambda x: (x['patient'], x['exam_name'], x['difference']))
    
    return results


def compute_difference_breakdown(compulab_total, simus_total, comparison_results):
    """Calcula a explicação da diferença total (COMPULAB - SIMUS)"""
    diff_total = compulab_total - simus_total
    missing_patients_total = sum(item['total_value'] for item in comparison_results['missing_patients'])
    missing_exams_total = sum(item['value'] for item in comparison_results['missing_exams'])
    divergences_total = sum(item['difference'] for item in comparison_results['value_divergences'])
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

