---
description: Verify consistency between Python Models and Supabase.
---

# Workflow: /db-audit

1.  **Analyze Context**: Identify the `rx.Model` or data class in the current file.
2.  **Load Skill**:
    - Read `c:\Users\otavi\cursor-bio-compulabxsimus\.agent\skills\engenharia-dados-arquivista\SKILL.md` (O Arquivista).
3.  **Audit**:
    - Check if the field types match standard Supabase/Postgres types (e.g., `str` -> `text`, `int` -> `int8`).
    - Check for missing `table_name` or primary keys.
    - Verify if the `utils/supabase_client.py` usage follows best practices (singleton).
4.  **Output**:
    - A specific report on the Data Model's health.
    - Suggestions to fix distinct types or missing indexes.
