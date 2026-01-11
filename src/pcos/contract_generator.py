from pcos.llm import LLMClient
from pcos.obsidian import ObsidianClient
from pcos.prompts import PROJECT_CONTRACT_PROMPT
from pcos.config import get_env
import re

def extract_frontmatter_content(text: str) -> str:
    """
    Extract the frontmatter and content, removing any text before the first ---
    """

    if text.strip().startswith("---"):
        return text.strip()
    
    pattern = r'^---\s*$'
    match = re.search(pattern, text, re.MULTILINE)
    
    if match:
        return text[match.start():]
    
    if '---' in text:
        idx = text.find('---')
        return text[idx:]
    
    return text

def ensure_frontmatter_closed(text: str) -> str:
    """
    Ensure the frontmatter is properly closed with a second ---
    """
    if not text.strip().startswith("---"):
        return text
    
    parts = text.split("---", 2)
    
    if len(parts) >= 2:
        if len(parts) == 2:
            yaml_content = parts[1]
            lines = yaml_content.split('\n')
            
            last_yaml_line_idx = 0
            for i, line in enumerate(lines):
                if line.strip():
                    last_yaml_line_idx = i
            
            lines.insert(last_yaml_line_idx + 1, "---")
            parts[1] = '\n'.join(lines)
            return "---".join(parts)
        else:
            return text
    
    return text

def generate_contract(cfg: dict, project: str):
    obsidian = ObsidianClient( 
            base_url=cfg["obsidian_api_base"],
            vault_name=cfg["vault_name"],
            api_key=get_env("OBSIDIAN_API_KEY"),)

    brainstorm_path = f"{cfg['projects_root']}/{project}/00_brainstorm.md"
    output_path = f"{cfg['projects_root']}/{project}/01_project_contract.md"

    brainstorm = obsidian.read_note(brainstorm_path)

    prompt = PROJECT_CONTRACT_PROMPT.format(brainstorm=brainstorm)

    llm = LLMClient()
    result = llm.generate(prompt)
    result = extract_frontmatter_content(result)
    if not result.strip().startswith("---"):
        raise RuntimeError("LLM output is not valid contract (no frontmatter)")
    
    result = ensure_frontmatter_closed(result)

    obsidian.write_note(output_path, result)

    return output_path