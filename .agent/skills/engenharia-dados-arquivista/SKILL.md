---
name: Engenharia de Dados e Supabase (O Arquivista)
description: Otimização e padronização da interação com o banco de dados Supabase e engenharia de dados.
---

# Skill: Engenharia de Dados e Supabase ("O Arquivista")

Esta skill organiza a camada de dados do Biodiagnóstico, promovendo o padrão Repository para desacoplar a lógica de negócios das chamadas diretas ao Supabase. Isso facilita manutenção, testes e futuras migrações.

## 🎯 Objetivos
- Centralizar queries SQL/Supabase em classes de Repositório.
- Eliminar duplicidade de código de acesso a dados nas páginas.
- Garantir validação de dados com Pydantic antes da persistência.
- Fornecer snippets para operações complexas (Upsert, Joins).

## 📂 Estrutura Recomendada
- `biodiagnostico_app/repositories/`: Classes de acesso a dados.
    - `user_repository.py`
    - `exam_repository.py`
    - `base_repository.py`: Classe base com métodos comuns (CRUD).
- `biodiagnostico_app/schemas/`: Modelos Pydantic para validação (se não usar apenas SQLModel do Reflex).

## 🛠️ O Padrão Repository
Ao invés de chamar `supabase.table("users").insert(...)` diretamente no State, use:

```python
# No State
from ..repositories.user_repository import UserRepository

def save_user(self):
    UserRepository.create(self.user_data)
```

## 📝 Receitas e Templates

### Base Repository (Template)
Use este template para criar repositórios tipados:

```python
# repositories/base_repository.py
from typing import Generic, TypeVar, List, Optional
import reflex as rx

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, table_name: str):
        self.table = table_name

    def get_client(self):
        # Assumindo que o client está acessível via state ou config global
        # Ajuste conforme sua implementação de client singleton
        return rx.get_app().state_manager.get_state(rx.State).supabase_client

    def get_all(self) -> List[T]:
        response = self.get_client().table(self.table).select("*").execute()
        return response.data

    def create(self, data: dict) -> T:
        response = self.get_client().table(self.table).insert(data).execute()
        return response.data[0]
```

### Validação com Pydantic
Antes de salvar, valide:

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: str = "user"

# No uso:
try:
    valid_data = UserCreate(**raw_data)
    repo.create(valid_data.dict())
except ValueError as e:
    print(f"Dados inválidos: {e}")
```

## 🚨 Guardrails do Arquivista
1. **Nunca** chame `supabase.table` diretamente dentro de um `render` ou componente UI. Use sempre via `State`.
2. Evite `SELECT *` em tabelas gigantes. Selecione apenas as colunas necessárias (`select("id, name")`).
3. Trate erros de conexão/timeout. O Repositório deve lançar exceções de domínio, não exceções brutas da lib client.

## 🔍 Scripts Úteis
- `scripts/migrate_to_repo.py`: (Futuro) Script para identificar chamadas diretas ao supabase e sugerir refatoração.
