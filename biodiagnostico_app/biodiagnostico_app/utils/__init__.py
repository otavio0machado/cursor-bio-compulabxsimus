# Utils package for Biodiagnóstico App
from .pdf_processor import (
    parse_currency_value,
    normalize_name,
    normalize_exam_name,
    normalize_exam_name_for_comparison,
    extract_key_terms,
    exam_names_match,
    map_simus_to_compulab_exam_name,
    extract_compulab_patients,
    extract_simus_patients,
    generate_excel_from_pdfs,
    load_from_csv,
    load_from_excel
)
from .comparison import compare_patients, compute_difference_breakdown, format_divergences_to_json
from .analysis_module import (
    load_data,
    normalize_exam_name as normalize_exam_name_v2,
    map_to_canonical,
    compare_exams,
    load_synonyms,
    normalize_synonyms,
    update_synonyms,
    results_to_dataframes,
    export_results_to_excel,
    export_results_to_csv,
)

