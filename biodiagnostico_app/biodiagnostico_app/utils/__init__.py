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
    load_from_excel,
    EXAM_NAME_MAPPING
)
from .comparison import compare_patients, compute_difference_breakdown, format_divergences_to_json

