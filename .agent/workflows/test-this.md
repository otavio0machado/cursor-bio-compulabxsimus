---
description: Create unit tests for the current code.
---

# Workflow: /test-this

1.  **Analyze Context**: Identify functions or classes in the current file that need testing.
2.  **Load Skill**:
    - Read `c:\Users\otavi\cursor-bio-compulabxsimus\.agent\skills\testes-qa-guardiao\SKILL.md` (O Guardião).
3.  **Generate Tests**:
    - Create a new test file (e.g., `tests/test_filename.py`) or append to existing.
    - Use `pytest` style.
    - Mock external dependencies (Supabase, API calls) as per the Guardião skill.
    - Cover happy paths and edge cases.
4.  **Output**:
    - The code for the test file.
    - Instructions on how to run it (e.g., `pytest tests/test_filename.py`).
