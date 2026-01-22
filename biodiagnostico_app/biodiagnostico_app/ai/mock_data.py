import json

def get_mock_divergency_data():
    """Returns a mock JSON string representing billing/glosa report data."""
    data = [
        {"id": 101, "data": "2024-01-15", "convenio": "Unimed", "paciente": "Maria Silva", "exame": "Hemograma Completo", "valor": 28.50, "status": "GLOSADO", "motivo_glosa": "Carteirinha vencida/inválida"},
        {"id": 102, "data": "2024-01-15", "convenio": "Bradesco Saúde", "paciente": "João Souza", "exame": "Glicose", "valor": 12.00, "status": "PAGO", "motivo_glosa": None},
        {"id": 103, "data": "2024-01-16", "convenio": "Unimed", "paciente": "Pedro Santos", "exame": "Colesterol Total", "valor": 18.00, "status": "GLOSADO", "motivo_glosa": "Pedido médico sem assinatura"},
        {"id": 104, "data": "2024-01-16", "convenio": "SulAmérica", "paciente": "Ana Costa", "exame": "TSH", "valor": 45.00, "status": "GLOSADO", "motivo_glosa": "Valor acima da tabela acordada"},
        {"id": 105, "data": "2024-01-17", "convenio": "Unimed", "paciente": "Lucas Lima", "exame": "Hemograma Completo", "valor": 28.50, "status": "PAGO", "motivo_glosa": None},
        {"id": 106, "data": "2024-01-17", "convenio": "Amil", "paciente": "Carla Diaz", "exame": "Vitamina D", "valor": 80.00, "status": "GLOSADO", "motivo_glosa": "Falta justificativa clínica"},
        {"id": 107, "data": "2024-01-18", "convenio": "Unimed", "paciente": "Roberto Carlos", "exame": "Ressonância Magnética", "valor": 450.00, "status": "GLOSADO", "motivo_glosa": "Autorização prévia inexistente"},
        {"id": 108, "data": "2024-01-18", "convenio": "Bradesco Saúde", "paciente": "Fernanda Torres", "exame": "Urina Tipo 1", "valor": 15.00, "status": "PAGO", "motivo_glosa": None},
        {"id": 109, "data": "2024-01-19", "convenio": "Unimed", "paciente": "Juliana Paes", "exame": "Hemograma Completo", "valor": 28.50, "status": "GLOSADO", "motivo_glosa": "Carteirinha vencida/inválida"},
        {"id": 110, "data": "2024-01-19", "convenio": "Cassi", "paciente": "Wagner Moura", "exame": "Lipidograma", "valor": 55.00, "status": "PAGO", "motivo_glosa": None}
    ]
    return json.dumps(data, indent=2, ensure_ascii=False)
