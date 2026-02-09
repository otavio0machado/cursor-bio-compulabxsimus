"""
Utilitários de conversão numérica para locale brasileiro.
"""


def parse_decimal(value, default: float = 0.0) -> float:
    """Converte string para float, tratando vírgula brasileira como separador decimal.

    Args:
        value: Valor a converter (str, int, float ou None).
        default: Valor retornado se a conversão falhar.

    Returns:
        float convertido ou default.
    """
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, str) or not value.strip():
        return default
    try:
        return float(value.strip().replace(",", "."))
    except (ValueError, TypeError):
        return default
