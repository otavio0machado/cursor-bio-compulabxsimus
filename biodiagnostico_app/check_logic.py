
# Mocking the data structures
class QCRecord:
    def __init__(self, exam_name):
        self.exam_name = exam_name

qc_records = [
    QCRecord("GLICOSE"),
    QCRecord("TEST_NEW_EXAM")
]

def get_unique_exam_names():
    # Lista de exames comuns em laboratório (padronizada)
    common_exams = [
        "GLICOSE",
        "HEMOGRAMA",
        "CREATININA",
        "UREIA",
        "ACIDO URICO",
        "COLESTEROL TOTAL",
        "COLESTEROL HDL",
        "COLESTEROL LDL",
        "TRIGLICERIDEOS",
        "HEMOGLOBINA GLICOSILADA A1C",
        "TIREOTROFINA (TSH)",
        "TIROXINA LIVRE (T4 LIVRE)",
        "VITAMINA D25",
        "VITAMINA B12",
        "FERRITINA",
        "FERRO SERICO",
        "SODIO",
        "POTASSIO",
        "CALCIO",
        "MAGNESIO",
        "GOT",
        "GPT",
        "GAMA GT",
        "FOSFATASE ALCALINA",
        "BILIRRUBINAS",
        "PROTEINA C REATIVA",
        "V. S. G.",
        "TEMPO DE PROTROMBINA",
        "EXAME QUALITATIVO DE URINA",
        "UROCULTURA",
        "INSULINA",
        "CORTISOL",
        "PROLACTINA",
        "ESTRADIOL",
        "PROGESTERONA",
        "TESTOSTERONA TOTAL",
        "HORMONIO FOLICULO ESTIMULANTE FSH",
        "HORMONIO LUTEINIZANTE LH",
        "ANTIGENO PROSTATICO ESPECIFICO",
    ]
    
    # Adicionar exames dos registros existentes
    recorded_exams = set()
    for record in qc_records:
        if record.exam_name:
            recorded_exams.add(record.exam_name)
    
    # Combinar e ordenar
    all_exams = set(common_exams) | recorded_exams
    return sorted(list(all_exams))

exams = get_unique_exam_names()
print(f"Total Exams: {len(exams)}")
print(f"Contains 'GLICOSE': {'GLICOSE' in exams}")
print(f"Contains 'TEST_NEW_EXAM': {'TEST_NEW_EXAM' in exams}")
