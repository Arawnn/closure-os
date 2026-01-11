PROJECT_CONTRACT_PROMPT = """
You are a systems analyst.

Your task is to convert the following brainstorm into a STRICT project contract.

Rules:
- Your output MUST start IMMEDIATELY with "---" (three dashes)
- NO text, NO explanations, NO commentary before the frontmatter
- Output valid Markdown with YAML frontmatter followed by formatted ticket sections
- Be concise, deterministic, explicit.
- Avoid vague goals, each ticket should produce a binary outcome.
- Maximum 9 tickets.
- Each ticket must be independently shippable.
- Excluded scope must be a list of strings.

Output format:
1. Start with YAML frontmatter (closed with ---)
2. After frontmatter, add a Markdown section "## 📋 Tickets" with a table
3. Then add detailed sections for each ticket

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

After the frontmatter, add:

## 📋 Tickets

| # | Ticket | Estimation | Description |
|---|--------|------------|-------------|
| 1 | <ticket name> | <estimate> | <short description> |
| 2 | <ticket name> | <estimate> | <short description> |

### Détails des tickets

#### 1. <ticket name>

**Estimation:** <estimate> slots

**Description:** <full description>

**Scope exclu:**
- <excluded item>

#### 2. <ticket name>

...

Brainstorm input:
==================
{brainstorm}
"""