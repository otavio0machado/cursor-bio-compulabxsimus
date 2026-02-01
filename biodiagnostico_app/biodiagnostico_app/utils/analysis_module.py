"""
Modulo de comparacao COMPULAB vs SIMUS baseado em DataFrames.

Objetivo:
- Normalizar nomes de exames com unidecode
- Aplicar sinonimos configuraveis
- Priorizar codigo SIGTAP como chave primaria
- Usar nome canonico como fallback
- Opcionalmente aplicar fuzzy matching
"""
from __future__ import annotations

import io
import json
import os
import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import pandas as pd
from unidecode import unidecode


GENERIC_TERMS = [
    "DOSAGEM DE",
    "DOSAGEM",
    "DETERMINACAO DE",
    "DETERMINACAO",
    "ANALISE DE",
    "ANALISE",
    "AVALIACAO DE",
    "AVALIACAO",
    "MEDICAO DE",
    "MEDICAO",
    "MEDIDA DE",
    "MEDIDA",
    "TESTE DE",
    "TESTE",
    "EXAME DE",
    "EXAME",
    "QUANTIFICACAO DE",
    "QUANTIFICACAO",
    "DETECCAO DE",
    "DETECCAO",
    "PESQUISA DE",
    "PESQUISA",
    "TRIAGEM DE",
    "TRIAGEM",
    "SOROLOGIA DE",
    "SOROLOGIA",
    "IMUNOLOGIA DE",
    "IMUNOLOGIA",
    "QUALITATIVO DE",
    "QUALITATIVO",
    "QUANTITATIVO DE",
    "QUANTITATIVO",
]


DEFAULT_SYNONYMS = {
    "HEMOGRAMA COMPLETO": "HEMOGRAMA",
    "HEMOGRAMA": "HEMOGRAMA",
    "GLICEMIA EM JEJUM": "GLICOSE",
    "GAMMA GT": "GAMA GT",
    "AST": "GOT",
    "ALT": "GPT",
    "EAS": "URINA",
}


def load_synonyms(source: Optional[Union[str, Dict[str, str], List[Dict[str, str]]]] = None) -> Dict[str, str]:
    """
    Carrega sinonimos a partir de arquivo JSON, string JSON ou dict/lista.

    Aceita:
    - dict {"VARIACAO": "CANONICO"}
    - lista [{"original_name": "...", "canonical_name": "..."}]
    - caminho para JSON
    - string JSON

    Retorna um dicionario normalizado (chave e valor em uppercase e sem acentos).
    """
    if source is None:
        return {}

    data: Union[Dict[str, str], List[Dict[str, str]]]
    if isinstance(source, dict) or isinstance(source, list):
        data = source
    elif isinstance(source, str):
        if os.path.exists(source):
            with open(source, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        else:
            data = json.loads(source)
    else:
        raise ValueError("Formato invalido para sinonimos.")

    return normalize_synonyms(data)


def normalize_synonyms(raw: Union[Dict[str, str], List[Dict[str, str]]]) -> Dict[str, str]:
    """
    Normaliza sinonimos para um dicionario padrao {normalizado: canonico}.
    """
    normalized: Dict[str, str] = {}

    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            original = str(item.get("original_name", "")).strip()
            canonical = str(item.get("canonical_name", "")).strip()
            if not original or not canonical:
                continue
            key = normalize_exam_name(original)
            value = normalize_exam_name(canonical)
            if key:
                normalized[key] = value or key
        return normalized

    for original, canonical in raw.items():
        if not original:
            continue
        key = normalize_exam_name(str(original))
        value = normalize_exam_name(str(canonical)) if canonical else key
        if key:
            normalized[key] = value or key

    return normalized


def update_synonyms(base: Dict[str, str], updates: Dict[str, str]) -> Dict[str, str]:
    """
    Mescla sinonimos existentes com novos, retornando um novo dicionario.
    """
    merged = dict(base or {})
    merged.update(updates or {})
    return normalize_synonyms(merged)


def normalize_patient_name(name: str) -> str:
    """
    Normaliza nome do paciente para comparacao robusta.
    """
    if not name:
        return ""
    text = unidecode(str(name)).upper()
    text = re.sub(r"[^A-Z0-9\s]", " ", text)
    text = " ".join(text.split())
    return text.strip()


def normalize_exam_name(name: str) -> str:
    """
    Normaliza nome do exame para comparacao.

    - Converte para maiusculas
    - Remove acentos (unidecode)
    - Remove termos genericos
    - Remove pontuacao e parenteses
    """
    if not name:
        return ""
    text = unidecode(str(name)).upper().strip()
    text = text.replace("(", " ").replace(")", " ")
    text = re.sub(r"[^\w\s]", " ", text)
    text = " ".join(text.split())

    for term in GENERIC_TERMS:
        pattern_start = r"^" + re.escape(term) + r"\s+"
        text = re.sub(pattern_start, "", text)

    return text.strip()


def map_to_canonical(name: str, synonyms: Dict[str, str]) -> str:
    """
    Mapeia um nome para o canonico usando dicionario de sinonimos.
    """
    normalized = normalize_exam_name(name)
    if not synonyms:
        return normalized
    return synonyms.get(normalized, normalized)


def load_data(file: Union[bytes, str, pd.DataFrame], source: Optional[str] = None) -> pd.DataFrame:
    """
    Carrega dados de CSV/XLSX/PDF (pre-processado) ou DataFrame e padroniza colunas.

    Args:
        file: bytes, caminho/contendo CSV/XLSX/PDF ou DataFrame
        source: opcional ("compulab" ou "simus") quando a entrada for PDF
    """
    if isinstance(file, pd.DataFrame):
        df = file.copy()
        return standardize_columns(df)

    if isinstance(file, bytes):
        if file[:4] == b"%PDF":
            return _load_from_pdf_bytes(file, source)
        if file[:2] == b"PK":
            return standardize_columns(pd.read_excel(io.BytesIO(file)))
        return standardize_columns(_read_csv_bytes(file))

    if isinstance(file, str):
        if os.path.exists(file):
            lower = file.lower()
            if lower.endswith(".pdf"):
                return _load_from_pdf_path(file, source)
            if lower.endswith(".xlsx") or lower.endswith(".xls"):
                return standardize_columns(pd.read_excel(file))
            if lower.endswith(".tsv"):
                return standardize_columns(pd.read_csv(file, sep="\t"))
            if lower.endswith(".csv"):
                return standardize_columns(pd.read_csv(file, sep=None, engine="python"))
        return standardize_columns(_read_csv_text(file))

    raise ValueError("Tipo de arquivo invalido.")


def compare_exams(
    df_compulab: pd.DataFrame,
    df_simus: pd.DataFrame,
    synonyms: Optional[Dict[str, str]] = None,
    *,
    tolerance: float = 0.01,
    enable_fuzzy: bool = False,
    fuzzy_threshold: float = 0.93,
) -> Dict[str, Any]:
    """
    Compara exames entre COMPULAB e SIMUS.

    Regras:
    - Usa Codigo_Exame quando presente nas duas fontes
    - Usa Nome_Canonico como fallback
    - Fuzzy matching opcional para variacoes nao cobertas por sinonimos
    - Tolerancia de valor padrao: R$ 0,01
    """
    normalized_synonyms = normalize_synonyms(synonyms or {})

    comp_df = prepare_dataframe(df_compulab, normalized_synonyms)
    sim_df = prepare_dataframe(df_simus, normalized_synonyms)

    comp_patients = build_patient_records(comp_df)
    sim_patients = build_patient_records(sim_df)

    all_patient_keys = sorted(set(comp_patients.keys()) | set(sim_patients.keys()))

    missing_in_simus: List[Dict[str, Any]] = []
    missing_in_compulab: List[Dict[str, Any]] = []
    value_divergences: List[Dict[str, Any]] = []

    tolerance_dec = Decimal(str(tolerance))

    for patient_key in all_patient_keys:
        comp_data = comp_patients.get(patient_key)
        sim_data = sim_patients.get(patient_key)

        if not comp_data:
            for record in sim_data["records"]:
                missing_in_compulab.append(
                    build_result_row(
                        patient=record["patient"],
                        code=record["code"],
                        canonical_name=record["canonical_name"],
                        comp_value=None,
                        sim_value=record["value"],
                        comp_exam_name="",
                        sim_exam_name=record["exam_name"],
                    )
                )
            continue

        if not sim_data:
            for record in comp_data["records"]:
                missing_in_simus.append(
                    build_result_row(
                        patient=record["patient"],
                        code=record["code"],
                        canonical_name=record["canonical_name"],
                        comp_value=record["value"],
                        sim_value=None,
                        comp_exam_name=record["exam_name"],
                        sim_exam_name="",
                    )
                )
            continue

        comp_records = comp_data["records"]
        sim_records = sim_data["records"]

        pairs, comp_unmatched, sim_unmatched = match_records(
            comp_records,
            sim_records,
            enable_fuzzy=enable_fuzzy,
            fuzzy_threshold=fuzzy_threshold,
        )

        for comp_idx, sim_idx in pairs:
            comp_record = comp_records[comp_idx]
            sim_record = sim_records[sim_idx]
            diff = comp_record["value"] - sim_record["value"]
            if abs(diff) > tolerance_dec:
                value_divergences.append(
                    build_result_row(
                        patient=comp_record["patient"] or sim_record["patient"],
                        code=comp_record["code"] or sim_record["code"],
                        canonical_name=comp_record["canonical_name"] or sim_record["canonical_name"],
                        comp_value=comp_record["value"],
                        sim_value=sim_record["value"],
                        comp_exam_name=comp_record["exam_name"],
                        sim_exam_name=sim_record["exam_name"],
                    )
                )

        for comp_idx in sorted(comp_unmatched):
            record = comp_records[comp_idx]
            missing_in_simus.append(
                build_result_row(
                    patient=record["patient"],
                    code=record["code"],
                    canonical_name=record["canonical_name"],
                    comp_value=record["value"],
                    sim_value=None,
                    comp_exam_name=record["exam_name"],
                    sim_exam_name="",
                )
            )

        for sim_idx in sorted(sim_unmatched):
            record = sim_records[sim_idx]
            missing_in_compulab.append(
                build_result_row(
                    patient=record["patient"],
                    code=record["code"],
                    canonical_name=record["canonical_name"],
                    comp_value=None,
                    sim_value=record["value"],
                    comp_exam_name="",
                    sim_exam_name=record["exam_name"],
                )
            )

    missing_in_simus.sort(key=lambda r: (r["Paciente"], r["Nome_Canonico"], r["Codigo_Exame"]))
    missing_in_compulab.sort(key=lambda r: (r["Paciente"], r["Nome_Canonico"], r["Codigo_Exame"]))
    value_divergences.sort(key=lambda r: (r["Paciente"], r["Nome_Canonico"], r["Codigo_Exame"]))

    summary = {
        "missing_in_simus_count": len(missing_in_simus),
        "missing_in_compulab_count": len(missing_in_compulab),
        "value_divergences_count": len(value_divergences),
        "missing_in_simus_total": float(sum_decimal(r["Valor_COMPULAB"] for r in missing_in_simus)),
        "missing_in_compulab_total": float(sum_decimal(r["Valor_SIMUS"] for r in missing_in_compulab)),
        "divergences_total": float(sum_decimal(abs_decimal(r["Diferenca"]) for r in value_divergences)),
    }

    return {
        "missing_in_simus": missing_in_simus,
        "missing_in_compulab": missing_in_compulab,
        "value_divergences": value_divergences,
        "summary": summary,
    }


def results_to_dataframes(results: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
    """
    Converte o resultado da comparacao em DataFrames.
    """
    return {
        "missing_in_simus": pd.DataFrame(results.get("missing_in_simus", [])),
        "missing_in_compulab": pd.DataFrame(results.get("missing_in_compulab", [])),
        "value_divergences": pd.DataFrame(results.get("value_divergences", [])),
    }


def export_results_to_excel(results: Dict[str, Any], file_path: Optional[str] = None) -> Optional[bytes]:
    """
    Exporta os resultados para Excel (xlsx). Se file_path for fornecido, salva no disco.
    """
    output = io.BytesIO()
    dataframes = results_to_dataframes(results)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        dataframes["missing_in_simus"].to_excel(writer, index=False, sheet_name="Faltantes_Simus")
        dataframes["missing_in_compulab"].to_excel(writer, index=False, sheet_name="Faltantes_Compulab")
        dataframes["value_divergences"].to_excel(writer, index=False, sheet_name="Divergencias")

    data = output.getvalue()
    if file_path:
        with open(file_path, "wb") as handle:
            handle.write(data)
        return None

    return data


def export_results_to_csv(results: Dict[str, Any], directory: Optional[str] = None) -> Dict[str, str]:
    """
    Exporta resultados para CSV. Se directory for fornecido, salva arquivos no disco.
    """
    dataframes = results_to_dataframes(results)
    outputs: Dict[str, str] = {}

    for name, df in dataframes.items():
        csv_text = df.to_csv(index=False, sep=";", encoding="utf-8-sig")
        if directory:
            os.makedirs(directory, exist_ok=True)
            file_path = os.path.join(directory, f"{name}.csv")
            with open(file_path, "w", encoding="utf-8-sig") as handle:
                handle.write(csv_text)
            outputs[name] = file_path
        else:
            outputs[name] = csv_text

    return outputs


def prepare_dataframe(df: pd.DataFrame, synonyms: Dict[str, str]) -> pd.DataFrame:
    """
    Padroniza colunas e cria campos auxiliares para comparacao.
    """
    standardized = standardize_columns(df)
    standardized["Paciente"] = standardized["Paciente"].astype(str).fillna("")
    standardized["Nome_Exame"] = standardized["Nome_Exame"].astype(str).fillna("")
    standardized["Codigo_Exame"] = standardized["Codigo_Exame"].astype(str).fillna("")

    standardized["Paciente_Normalizado"] = standardized["Paciente"].apply(normalize_patient_name)
    standardized["Codigo_Exame"] = standardized["Codigo_Exame"].apply(clean_code)
    standardized["Nome_Canonico"] = standardized["Nome_Exame"].apply(lambda x: map_to_canonical(x, synonyms))
    standardized["Valor"] = standardized["Valor"].apply(safe_decimal)

    return standardized


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Garante colunas: Paciente, Nome_Exame, Codigo_Exame, Valor.
    """
    if df is None or df.empty:
        return pd.DataFrame(columns=["Paciente", "Nome_Exame", "Codigo_Exame", "Valor"])

    col_map = resolve_column_map(df.columns)
    renamed = df.rename(columns=col_map).copy()

    if "Paciente" not in renamed.columns or "Nome_Exame" not in renamed.columns or "Valor" not in renamed.columns:
        raise ValueError("Colunas obrigatorias ausentes: Paciente, Nome_Exame, Valor.")

    if "Codigo_Exame" not in renamed.columns:
        renamed["Codigo_Exame"] = ""

    return renamed[["Paciente", "Nome_Exame", "Codigo_Exame", "Valor"]]


def resolve_column_map(columns: Iterable[str]) -> Dict[str, str]:
    """
    Mapeia colunas de entrada para os nomes padrao.
    """
    normalized = {col: normalize_column_name(col) for col in columns}
    col_map: Dict[str, str] = {}

    def find_column(possible: List[str]) -> Optional[str]:
        normalized_targets = [normalize_column_name(c) for c in possible]
        for col, norm in normalized.items():
            if norm in normalized_targets:
                return col
        return None

    patient_col = find_column(
        [
            "PACIENTE",
            "PACIENTES",
            "NOME_PACIENTE",
            "NOME DO PACIENTE",
            "BENEFICIARIO",
            "NOME",
        ]
    )
    exam_col = find_column(
        [
            "NOME_EXAME",
            "NOME DO EXAME",
            "EXAME",
            "PROCEDIMENTO",
            "DESCRICAO",
        ]
    )
    code_col = find_column(
        [
            "CODIGO_EXAME",
            "CODIGO",
            "COD",
            "SIGTAP",
            "COD_PROC",
        ]
    )
    value_col = find_column(
        [
            "VALOR",
            "VALOR_PAGO",
            "VALOR PAGO",
            "PRECO",
            "TOTAL",
            "VALOR_TOTAL",
        ]
    )

    if patient_col:
        col_map[patient_col] = "Paciente"
    if exam_col:
        col_map[exam_col] = "Nome_Exame"
    if code_col:
        col_map[code_col] = "Codigo_Exame"
    if value_col:
        col_map[value_col] = "Valor"

    return col_map


def normalize_column_name(name: str) -> str:
    """
    Normaliza nome de coluna para facilitar o mapeamento.
    """
    text = unidecode(str(name)).upper()
    text = re.sub(r"[^A-Z0-9]+", "_", text).strip("_")
    return text


def clean_code(code: Any) -> str:
    """
    Limpa codigo do exame (SIGTAP) removendo caracteres nao numericos.
    """
    if code is None:
        return ""
    text = str(code).strip()
    if text.lower() in {"nan", "none", "null"}:
        return ""
    digits = re.sub(r"\D", "", text)
    return digits or text


def safe_decimal(value: Any, default: Decimal = Decimal("0")) -> Decimal:
    """
    Converte valores para Decimal de forma segura.
    """
    if value is None:
        return default
    if isinstance(value, Decimal):
        return value
    text = str(value).strip()
    if not text:
        return default
    text = text.replace("R$", "").strip()
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text and "." not in text:
        text = text.replace(",", ".")
    text = re.sub(r"[^0-9.\-]", "", text)
    if text in {"", "-", ".", "-.", ".-"}:
        return default
    try:
        return Decimal(text)
    except Exception:
        return default


def build_patient_records(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Agrupa exames por paciente normalizado.
    """
    patients: Dict[str, Dict[str, Any]] = {}
    for row in df.itertuples(index=False):
        patient = getattr(row, "Paciente", "")
        patient_norm = getattr(row, "Paciente_Normalizado", "")
        if not patient_norm:
            continue
        entry = patients.setdefault(patient_norm, {"records": []})
        entry["records"].append(
            {
                "patient": patient,
                "exam_name": getattr(row, "Nome_Exame", ""),
                "canonical_name": getattr(row, "Nome_Canonico", ""),
                "code": getattr(row, "Codigo_Exame", ""),
                "value": getattr(row, "Valor", Decimal("0")),
            }
        )
    return patients


def match_records(
    comp_records: List[Dict[str, Any]],
    sim_records: List[Dict[str, Any]],
    *,
    enable_fuzzy: bool = False,
    fuzzy_threshold: float = 0.93,
) -> Tuple[List[Tuple[int, int]], List[int], List[int]]:
    """
    Executa o matching por codigo, nome canonico e fuzzy opcional.
    """
    comp_unmatched = set(range(len(comp_records)))
    sim_unmatched = set(range(len(sim_records)))
    pairs: List[Tuple[int, int]] = []

    # Match por codigo
    comp_by_code = group_by(comp_records, comp_unmatched, key="code")
    sim_by_code = group_by(sim_records, sim_unmatched, key="code")
    for code in sorted(set(comp_by_code.keys()) & set(sim_by_code.keys())):
        comp_indices = sort_indices(comp_by_code[code], comp_records)
        sim_indices = sort_indices(sim_by_code[code], sim_records)
        for comp_idx, sim_idx in zip(comp_indices, sim_indices):
            if comp_idx in comp_unmatched and sim_idx in sim_unmatched:
                pairs.append((comp_idx, sim_idx))
                comp_unmatched.remove(comp_idx)
                sim_unmatched.remove(sim_idx)

    # Match por nome canonico
    comp_by_name = group_by(comp_records, comp_unmatched, key="canonical_name")
    sim_by_name = group_by(sim_records, sim_unmatched, key="canonical_name")
    for name in sorted(set(comp_by_name.keys()) & set(sim_by_name.keys())):
        comp_indices = sort_indices(comp_by_name[name], comp_records)
        sim_indices = sort_indices(sim_by_name[name], sim_records)
        for comp_idx, sim_idx in zip(comp_indices, sim_indices):
            if comp_idx in comp_unmatched and sim_idx in sim_unmatched:
                pairs.append((comp_idx, sim_idx))
                comp_unmatched.remove(comp_idx)
                sim_unmatched.remove(sim_idx)

    if enable_fuzzy and comp_unmatched and sim_unmatched:
        fuzzy_pairs = fuzzy_match_pairs(
            comp_records,
            sim_records,
            comp_unmatched,
            sim_unmatched,
            threshold=fuzzy_threshold,
        )
        for comp_idx, sim_idx in fuzzy_pairs:
            if comp_idx in comp_unmatched and sim_idx in sim_unmatched:
                pairs.append((comp_idx, sim_idx))
                comp_unmatched.remove(comp_idx)
                sim_unmatched.remove(sim_idx)

    return pairs, sorted(comp_unmatched), sorted(sim_unmatched)


def group_by(records: List[Dict[str, Any]], indices: Iterable[int], key: str) -> Dict[str, List[int]]:
    """
    Agrupa indices por chave de record.
    """
    grouped: Dict[str, List[int]] = {}
    for idx in indices:
        value = str(records[idx].get(key, "")).strip()
        if not value:
            continue
        grouped.setdefault(value, []).append(idx)
    return grouped


def sort_indices(indices: List[int], records: List[Dict[str, Any]]) -> List[int]:
    """
    Ordena indices para matching deterministico.
    """
    return sorted(
        indices,
        key=lambda idx: (
            records[idx].get("canonical_name", ""),
            str(records[idx].get("value", "")),
        ),
    )


def fuzzy_match_pairs(
    comp_records: List[Dict[str, Any]],
    sim_records: List[Dict[str, Any]],
    comp_unmatched: Iterable[int],
    sim_unmatched: Iterable[int],
    *,
    threshold: float,
) -> List[Tuple[int, int]]:
    """
    Gera pares usando Jaro-Winkler quando codigos nao estao disponiveis.
    """
    candidates: List[Tuple[float, int, int]] = []
    for comp_idx in comp_unmatched:
        comp_record = comp_records[comp_idx]
        comp_name = comp_record.get("canonical_name", "")
        if not comp_name:
            continue
        for sim_idx in sim_unmatched:
            sim_record = sim_records[sim_idx]
            sim_name = sim_record.get("canonical_name", "")
            if not sim_name:
                continue
            if comp_record.get("code") and sim_record.get("code"):
                continue
            score = jaro_winkler_similarity(comp_name, sim_name)
            if score >= threshold:
                candidates.append((score, comp_idx, sim_idx))

    candidates.sort(key=lambda item: (-item[0], comp_records[item[1]].get("canonical_name", "")))

    pairs: List[Tuple[int, int]] = []
    used_comp = set()
    used_sim = set()
    for _, comp_idx, sim_idx in candidates:
        if comp_idx in used_comp or sim_idx in used_sim:
            continue
        pairs.append((comp_idx, sim_idx))
        used_comp.add(comp_idx)
        used_sim.add(sim_idx)
    return pairs


def jaro_winkler_similarity(s1: str, s2: str, prefix_scale: float = 0.1, max_prefix: int = 4) -> float:
    """
    Similaridade Jaro-Winkler entre duas strings.
    """
    s1 = str(s1)
    s2 = str(s2)
    if s1 == s2:
        return 1.0
    jaro = jaro_similarity(s1, s2)
    prefix = 0
    for i in range(min(len(s1), len(s2), max_prefix)):
        if s1[i] == s2[i]:
            prefix += 1
        else:
            break
    return jaro + prefix * prefix_scale * (1.0 - jaro)


def jaro_similarity(s1: str, s2: str) -> float:
    """
    Similaridade Jaro entre duas strings.
    """
    if not s1 or not s2:
        return 0.0
    len1 = len(s1)
    len2 = len(s2)
    match_distance = max(len1, len2) // 2 - 1

    s1_matches = [False] * len1
    s2_matches = [False] * len2
    matches = 0

    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len2)
        for j in range(start, end):
            if s2_matches[j]:
                continue
            if s1[i] != s2[j]:
                continue
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    transpositions = 0
    s2_index = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[s2_index]:
            s2_index += 1
        if s1[i] != s2[s2_index]:
            transpositions += 1
        s2_index += 1

    transpositions /= 2
    return (
        matches / len1
        + matches / len2
        + (matches - transpositions) / matches
    ) / 3.0


def build_result_row(
    *,
    patient: str,
    code: str,
    canonical_name: str,
    comp_value: Optional[Decimal],
    sim_value: Optional[Decimal],
    comp_exam_name: str,
    sim_exam_name: str,
) -> Dict[str, Any]:
    """
    Monta um registro padrao para resultados.
    """
    comp_val = decimal_to_float(quantize_decimal(comp_value)) if comp_value is not None else None
    sim_val = decimal_to_float(quantize_decimal(sim_value)) if sim_value is not None else None
    diff_val = None
    if comp_val is not None and sim_val is not None:
        diff_val = decimal_to_float(quantize_decimal(Decimal(str(comp_val)) - Decimal(str(sim_val))))
    elif comp_val is not None:
        diff_val = comp_val
    elif sim_val is not None:
        diff_val = decimal_to_float(quantize_decimal(Decimal("0") - Decimal(str(sim_val))))

    return {
        "Paciente": patient,
        "Codigo_Exame": code,
        "Nome_Canonico": canonical_name,
        "Nome_Exame_Compulab": comp_exam_name,
        "Nome_Exame_Simus": sim_exam_name,
        "Valor_COMPULAB": comp_val,
        "Valor_SIMUS": sim_val,
        "Diferenca": diff_val,
    }


def quantize_decimal(value: Decimal) -> Decimal:
    """
    Arredonda valor para 2 casas decimais.
    """
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def decimal_to_float(value: Decimal) -> float:
    """
    Converte Decimal para float com duas casas.
    """
    return float(value)


def sum_decimal(values: Iterable[Any]) -> Decimal:
    """
    Soma valores convertendo para Decimal.
    """
    total = Decimal("0")
    for value in values:
        if value is None:
            continue
        total += safe_decimal(value, Decimal("0"))
    return quantize_decimal(total)


def abs_decimal(value: Any) -> Decimal:
    """
    Valor absoluto como Decimal.
    """
    return abs(safe_decimal(value, Decimal("0")))


def _read_csv_bytes(data: bytes) -> pd.DataFrame:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            text = data.decode(encoding)
            return _read_csv_text(text)
        except Exception:
            continue
    return _read_csv_text(data.decode("utf-8", errors="ignore"))


def _read_csv_text(text: str) -> pd.DataFrame:
    delimiter = _guess_delimiter(text)
    return pd.read_csv(io.StringIO(text), sep=delimiter)


def _guess_delimiter(text: str) -> str:
    if isinstance(text, str):
        sample = text.splitlines()[:5]
        sample = "\n".join(sample)
    else:
        sample = text
    return ";" if ";" in sample else ","


def _load_from_pdf_bytes(data: bytes, source: Optional[str]) -> pd.DataFrame:
    if not source:
        raise ValueError("Informe source='compulab' ou 'simus' para PDF.")
    import tempfile

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(data)
        tmp_path = tmp.name
    try:
        return _load_from_pdf_path(tmp_path, source)
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def _load_from_pdf_path(path: str, source: Optional[str]) -> pd.DataFrame:
    if not source:
        raise ValueError("Informe source='compulab' ou 'simus' para PDF.")

    from . import pdf_processor

    if source.lower() == "compulab":
        patients, _ = pdf_processor.extract_compulab_patients(path)
    elif source.lower() == "simus":
        patients, _, _, _ = pdf_processor.extract_simus_patients(path)
    else:
        raise ValueError("Source invalido para PDF. Use 'compulab' ou 'simus'.")

    rows: List[Dict[str, Any]] = []
    for patient_name, data in (patients or {}).items():
        exams = data.get("exams", []) if isinstance(data, dict) else data
        for exam in exams:
            rows.append(
                {
                    "Paciente": patient_name,
                    "Nome_Exame": exam.get("exam_name", ""),
                    "Codigo_Exame": exam.get("code", ""),
                    "Valor": exam.get("value", 0),
                }
            )

    return standardize_columns(pd.DataFrame(rows))
