# Função de Formatação de Divergências Laboratoriais

## Descrição

A função `format_divergences_to_json()` converte dados delimitados (CSV/TSV) de divergências de exames laboratoriais em formato JSON estruturado, facilitando integração com frontend, banco de dados e outros sistemas.

## Localização

```
biodiagnostico_app/biodiagnostico_app/utils/comparison.py
```

## Como Usar

### Importação

```python
from biodiagnostico_app.utils import format_divergences_to_json
```

ou

```python
from biodiagnostico_app.utils.comparison import format_divergences_to_json
```

### Exemplo Básico

```python
# Dados de entrada (delimitados por ponto-e-vírgula)
dados_csv = """Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia
ANA SILVA;HEMOGRAMA;202020380;6,15;6,16;Valor Divergente
ANA SILVA;UREIA;202010694;2,77;0,00;Exame Ausente no SIMUS"""

# Conversão para JSON
json_result = format_divergences_to_json(dados_csv)

# Resultado
print(json_result)
```

### Saída Esperada

```json
[
  {
    "Paciente": "ANA SILVA",
    "Nome_Exame": "HEMOGRAMA",
    "Codigo_Exame": "202020380",
    "Valor_Compulab": "6,15",
    "Valor_Simus": "6,16",
    "Tipo_Divergencia": "Valor Divergente"
  },
  {
    "Paciente": "ANA SILVA",
    "Nome_Exame": "UREIA",
    "Codigo_Exame": "202010694",
    "Valor_Compulab": "2,77",
    "Valor_Simus": "0,00",
    "Tipo_Divergencia": "Exame Ausente no SIMUS"
  }
]
```

## Recursos

### Detecção Automática de Delimitador

A função detecta automaticamente se os dados usam:
- **Ponto-e-vírgula (;)** - Padrão brasileiro
- **Vírgula (,)** - Padrão internacional

```python
# Funciona com ponto-e-vírgula
dados1 = "Paciente;Nome_Exame;Codigo_Exame;..."

# Funciona com vírgula
dados2 = "Paciente,Nome_Exame,Codigo_Exame,..."
```

### Cabeçalho Opcional

A função detecta e pula automaticamente o cabeçalho se presente:

```python
# Com cabeçalho (recomendado)
dados = """Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia
JOAO SILVA;GLICOSE;202030456;12,50;12,50;Valor Correto"""

# Sem cabeçalho (também funciona)
dados = """JOAO SILVA;GLICOSE;202030456;12,50;12,50;Valor Correto"""
```

### Campos Vazios

Campos vazios são preservados como strings vazias:

```python
dados = """Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia
GABRIEL PIRES;;202135456;5,0;5,0;Valor Correto"""

# Resultado:
# {
#   "Paciente": "GABRIEL PIRES",
#   "Nome_Exame": "",
#   "Codigo_Exame": "202135456",
#   ...
# }
```

### Múltiplos Blocos

A função processa múltiplos blocos de dados em uma única chamada:

```python
dados = """Paciente;Nome_Exame;Codigo_Exame;Valor_Compulab;Valor_Simus;Tipo_Divergencia
PACIENTE A;EXAME 1;123;10,00;10,00;Valor Correto

PACIENTE B;EXAME 2;456;20,00;0,00;Exame Ausente no SIMUS"""

# Retorna array com ambos os registros
```

## Campos do JSON

Cada objeto no array JSON contém exatamente 6 campos:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `Paciente` | string | Nome do paciente |
| `Nome_Exame` | string | Nome do exame laboratorial |
| `Codigo_Exame` | string | Código do exame |
| `Valor_Compulab` | string | Valor no sistema COMPULAB (preserva formato decimal) |
| `Valor_Simus` | string | Valor no sistema SIMUS (preserva formato decimal) |
| `Tipo_Divergencia` | string | Tipo de divergência encontrada |

**Nota:** Todos os campos são strings, incluindo códigos e valores, para preservar formatação decimal original (vírgulas/pontos).

## Tipos de Divergência Comuns

- `Valor Divergente` - Valores diferentes entre sistemas
- `Exame Ausente no SIMUS` - Exame registrado apenas no COMPULAB
- `Valor Correto` - Valores idênticos (sem divergência)

## Integração com State.py

### Exemplo de Uso no Estado Reflex

```python
import reflex as rx
from biodiagnostico_app.utils import format_divergences_to_json
import json


class State(rx.State):
    divergencias_json: str = "[]"

    def processar_divergencias(self, dados_csv: str):
        """Processa dados CSV e armazena como JSON"""
        self.divergencias_json = format_divergences_to_json(dados_csv)

    @rx.var
    def divergencias_list(self) -> list:
        """Retorna divergências como lista de dicionários"""
        return json.loads(self.divergencias_json)

    @rx.var
    def total_divergencias(self) -> int:
        """Conta total de divergências"""
        return len(self.divergencias_list)

    def exportar_para_supabase(self):
        """Exemplo: exportar dados para Supabase"""
        divergencias = self.divergencias_list
        # Inserir no banco de dados
        # supabase.table('divergencias').insert(divergencias).execute()
```

### Uso em Componentes

```python
def display_divergencias():
    """Componente para exibir divergências"""
    return rx.foreach(
        State.divergencias_list,
        lambda item: rx.card(
            rx.text(f"Paciente: {item['Paciente']}"),
            rx.text(f"Exame: {item['Nome_Exame']}"),
            rx.text(f"COMPULAB: {item['Valor_Compulab']}"),
            rx.text(f"SIMUS: {item['Valor_Simus']}"),
            rx.badge(item['Tipo_Divergencia'])
        )
    )
```

## Integração com API/Backend

### Endpoint FastAPI

```python
from fastapi import APIRouter
from biodiagnostico_app.utils import format_divergences_to_json

router = APIRouter()


@router.post("/api/converter-divergencias")
async def converter_divergencias(dados: str):
    """Endpoint para converter dados CSV em JSON"""
    json_result = format_divergences_to_json(dados)
    return {
        "success": True,
        "data": json_result
    }
```

### Upload de Arquivo

```python
from fastapi import UploadFile

@router.post("/api/upload-divergencias")
async def upload_divergencias(file: UploadFile):
    """Upload de arquivo CSV e conversão"""
    contents = await file.read()
    dados_csv = contents.decode('utf-8')
    json_result = format_divergences_to_json(dados_csv)

    return {
        "filename": file.filename,
        "registros": len(json.loads(json_result)),
        "data": json_result
    }
```

## Integração com Banco de Dados

### Inserção em Supabase

```python
from biodiagnostico_app.services.supabase_client import get_supabase_client
import json


def salvar_divergencias_no_banco(dados_csv: str):
    """Salva divergências no Supabase"""
    supabase = get_supabase_client()

    # Converter para JSON
    json_str = format_divergences_to_json(dados_csv)
    divergencias = json.loads(json_str)

    # Inserir no banco
    result = supabase.table('divergencias_laboratoriais').insert(divergencias).execute()

    return len(result.data) if result.data else 0
```

### Schema Supabase (SQL)

```sql
CREATE TABLE divergencias_laboratoriais (
    id SERIAL PRIMARY KEY,
    paciente VARCHAR(255),
    nome_exame VARCHAR(255),
    codigo_exame VARCHAR(50),
    valor_compulab VARCHAR(50),
    valor_simus VARCHAR(50),
    tipo_divergencia VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Casos de Uso

### 1. Análise Comparativa COMPULAB vs SIMUS

```python
# Após comparação, gerar CSV de divergências
divergencias_csv = gerar_csv_divergencias(compulab_data, simus_data)

# Converter para JSON
json_data = format_divergences_to_json(divergencias_csv)

# Armazenar ou exibir
state.divergencias = json.loads(json_data)
```

### 2. Exportação de Relatórios

```python
import json

# Converter dados
json_str = format_divergences_to_json(dados_csv)
divergencias = json.loads(json_str)

# Gerar relatório
for div in divergencias:
    if div['Tipo_Divergencia'] == 'Valor Divergente':
        print(f"ALERTA: {div['Paciente']} - {div['Nome_Exame']}")
```

### 3. Dashboard de Métricas

```python
divergencias = json.loads(format_divergences_to_json(dados))

# Calcular métricas
total_divergencias = len(divergencias)
total_ausentes = sum(1 for d in divergencias if 'Ausente' in d['Tipo_Divergencia'])
total_valores_divergentes = sum(1 for d in divergencias if d['Tipo_Divergencia'] == 'Valor Divergente')
```

## Performance

- **Processamento:** Linear O(n) - processa cada linha uma vez
- **Memória:** Eficiente - não carrega dados duplicados
- **Formato:** JSON compacto com indent=2 para legibilidade

## Limitações

- Requer pelo menos 6 campos por linha
- Detecta apenas delimitadores `;` e `,`
- Não valida tipos de dados (preserva strings originais)
- Não realiza conversões de moeda ou formatação de números

## Troubleshooting

### Problema: JSON vazio retornado

**Causa:** Dados sem 6 campos completos ou delimitador não reconhecido

**Solução:** Verificar formato de entrada:
```python
# Correto (6 campos)
"PACIENTE;EXAME;CODIGO;VAL1;VAL2;TIPO"

# Incorreto (menos de 6 campos)
"PACIENTE;EXAME;CODIGO"
```

### Problema: Cabeçalho aparece nos dados

**Causa:** Cabeçalho não contém palavras-chave esperadas

**Solução:** Usar exatamente estes nomes no cabeçalho:
- Paciente
- Nome_Exame
- Codigo_Exame
- Valor_Compulab
- Valor_Simus
- Tipo_Divergencia

## Testes

Execute os testes incluídos:

```bash
# Teste standalone (sem dependências)
python test_divergences_standalone.py
```

## Changelog

- **v1.0** - Implementação inicial
  - Detecção automática de delimitador
  - Suporte a cabeçalho opcional
  - Tratamento de campos vazios
  - Processamento de múltiplos blocos

## Contribuindo

Para melhorias na função, edite:
```
biodiagnostico_app/biodiagnostico_app/utils/comparison.py
```

E atualize os testes em:
```
test_divergences_standalone.py
```
