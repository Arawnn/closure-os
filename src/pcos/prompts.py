PROJECT_CONTRACT_PROMPT = """
You are a systems analyst.

Your task is to convert the following brainstorm into a STRICT project contract.

Rules:
- Output ONLY valid Markdown.
- Must start with YAML frontmatter.
- No explanations, no commentary.
- Be concise, deterministic, explicit.
- Avoid vague goals, each ticket should produce a binary outcome.
- Maximum 9 tickets.
- Each ticket must be independently shippable.
- Excluded scope must be a list of strings.

Frontmatter schema:

---
project: <string>
title: <string>
objective: <string>
definition_of_done: <string>
deadline: <string or null>
excluded_scope:
  - <string>
tickets:
  - name: <string>
    estimate_slots: <integer or null> (fibonacci sequence: 1, 2, 3, 5, 8, 13, 21, 34, 55, 89)
    description: <string>
    scope_excluded:
      - <string>
---

Brainstorm input:
==================
{brainstorm}
"""
