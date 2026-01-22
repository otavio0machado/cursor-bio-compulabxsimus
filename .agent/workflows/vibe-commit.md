---
description: Generate an engaging, emoji-rich commit message.
---

# Workflow: /vibe-commit

1.  **Analyze Context**:
    - Look at the `git diff` or the changes made in the current session.
    - Identify the "Vibe" of the change (Refactor? Feature? Bugfix? Cleanup?).
2.  **Generate Message**:
    - Create a commit message that is informative but fun.
    - **Format**: `[Emoji] [Type]: [Description]`
    - **Emojis**:
        - 🎨 for UI/Design.
        - 🧹 for Cleanup.
        - 🐛 for Bugfix.
        - ✨ for New Feature.
        - 📝 for Docs.
        - 🚀 for Performance/Deploy.
    - Add a "Vibe Note" body if standard requires more detail (optional).
3.  **Output**:
    - The suggested commit command: `git commit -m "..."`.
