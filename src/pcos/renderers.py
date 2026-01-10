def render_readme(contract: dict) -> str:
    excluded = "\n".join(
        f"- {x}" for x in contract.get("excluded_scope", [])
    )

    return f"""# {contract.get("title", contract["project"])}

## 🎯 Objective
{contract.get("objective", "")}

## ✅ Definition of Done
{contract.get("definition_of_done", "")}

## 🚫 Excluded Scope
{excluded}

## ⏳ Deadline
{contract.get("deadline", "N/A")}
"""
