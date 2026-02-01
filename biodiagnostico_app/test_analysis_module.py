import json
import importlib.util
from pathlib import Path

import pandas as pd


MODULE_PATH = (
    Path(__file__).resolve().parent / "biodiagnostico_app" / "utils" / "analysis_module.py"
)
spec = importlib.util.spec_from_file_location("analysis_module", MODULE_PATH)
analysis_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analysis_module)

compare_exams = analysis_module.compare_exams
load_synonyms = analysis_module.load_synonyms
map_to_canonical = analysis_module.map_to_canonical
normalize_exam_name = analysis_module.normalize_exam_name
normalize_synonyms = analysis_module.normalize_synonyms


def test_normalize_exam_name_removes_generic_terms():
    name = "Dosagem de Glicemia em Jejum"
    assert normalize_exam_name(name) == "GLICEMIA EM JEJUM"


def test_map_to_canonical_with_synonyms():
    synonyms = normalize_synonyms({"GLICEMIA EM JEJUM": "GLICOSE"})
    assert map_to_canonical("Glicemia em Jejum", synonyms) == "GLICOSE"


def test_load_synonyms_from_json_string():
    payload = json.dumps(
        [
            {"original_name": "AST", "canonical_name": "GOT"},
            {"original_name": "GOT", "canonical_name": "GOT"},
        ]
    )
    synonyms = load_synonyms(payload)
    assert synonyms["AST"] == "GOT"
    assert synonyms["GOT"] == "GOT"


def test_compare_exams_by_code_and_value_divergence():
    comp_df = pd.DataFrame(
        [
            {"Paciente": "Ana", "Nome_Exame": "Glicose", "Codigo_Exame": "123", "Valor": 10.0},
            {"Paciente": "Ana", "Nome_Exame": "Hemograma Completo", "Codigo_Exame": "456", "Valor": 20.0},
        ]
    )
    sim_df = pd.DataFrame(
        [
            {"Paciente": "Ana", "Nome_Exame": "Glicemia em Jejum", "Codigo_Exame": "123", "Valor": 10.0},
            {"Paciente": "Ana", "Nome_Exame": "Hemograma", "Codigo_Exame": "456", "Valor": 25.0},
        ]
    )
    synonyms = normalize_synonyms({"GLICEMIA EM JEJUM": "GLICOSE", "HEMOGRAMA COMPLETO": "HEMOGRAMA"})

    results = compare_exams(comp_df, sim_df, synonyms, tolerance=0.01)

    assert results["summary"]["missing_in_simus_count"] == 0
    assert results["summary"]["missing_in_compulab_count"] == 0
    assert results["summary"]["value_divergences_count"] == 1
    divergence = results["value_divergences"][0]
    assert divergence["Codigo_Exame"] == "456"
    assert divergence["Valor_COMPULAB"] == 20.0
    assert divergence["Valor_SIMUS"] == 25.0


def test_compare_exams_fallback_to_canonical_name():
    comp_df = pd.DataFrame(
        [{"Paciente": "Joao", "Nome_Exame": "AST", "Codigo_Exame": "", "Valor": 12.0}]
    )
    sim_df = pd.DataFrame(
        [{"Paciente": "Joao", "Nome_Exame": "GOT", "Codigo_Exame": "", "Valor": 12.0}]
    )
    synonyms = normalize_synonyms({"AST": "GOT", "GOT": "GOT"})

    results = compare_exams(comp_df, sim_df, synonyms)

    assert results["summary"]["missing_in_simus_count"] == 0
    assert results["summary"]["missing_in_compulab_count"] == 0
    assert results["summary"]["value_divergences_count"] == 0


def test_compare_exams_fuzzy_match_when_enabled():
    comp_df = pd.DataFrame(
        [{"Paciente": "Maria", "Nome_Exame": "GLICEMIA JEJUM", "Codigo_Exame": "", "Valor": 15.0}]
    )
    sim_df = pd.DataFrame(
        [{"Paciente": "Maria", "Nome_Exame": "GLICEMIA EM JEJUM", "Codigo_Exame": "", "Valor": 15.0}]
    )

    results = compare_exams(comp_df, sim_df, enable_fuzzy=True, fuzzy_threshold=0.90)

    assert results["summary"]["missing_in_simus_count"] == 0
    assert results["summary"]["missing_in_compulab_count"] == 0
    assert results["summary"]["value_divergences_count"] == 0
