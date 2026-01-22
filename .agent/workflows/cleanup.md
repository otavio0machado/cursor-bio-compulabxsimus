---
description: Clean up code technical debt and dirt.
---

# Workflow: /cleanup

1.  **Analyze Context**: Scan the current file for "dirt".
2.  **Load Skill**:
    - Read `c:\Users\otavi\cursor-bio-compulabxsimus\.agent\skills\codigo-limpo-aspirador\SKILL.md` (O Aspirador).
3.  **Clean**:
    - **Remove** unused imports.
    - **Remove** commented-out code (dead code).
    - **Remove** `print` debugging statements (replace with logger if strictly necessary, otherwise delete).
    - **Fix** indentation or formatting inconsistencies.
    - **Shorten** variable names that are unnecessarily long (without losing meaning).
4.  **Output**:
    - Show the diff or the cleaned file.
    - List what was removed.
