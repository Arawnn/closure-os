from pathlib import Path

from pcos.llm import LLMClient
from pcos.obsidian import ObsidianClient
from pcos.prompts import PROJECT_CONTRACT_PROMPT
from pcos.config import get_env

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

    if not result.strip().startswith("---"):
        raise RuntimeError("LLM output is not valid contract (no frontmatter)")

    obsidian.write_note(output_path, result)

    return output_path
