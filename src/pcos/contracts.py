from pcos.obsidian import ObsidianClient
import yaml
from pcos.config import get_env


def load_project_contract(cfg: dict, project: str) -> dict:
    obsidian = ObsidianClient(
        base_url=cfg["obsidian_api_base"],
        vault_name=cfg["vault_name"],
        api_key=get_env("OBSIDIAN_API_KEY"),
    )
    path = f"{cfg['projects_root']}/{project}/01_project_contract.md"

    raw = obsidian.read_note(path)

    if not raw.startswith("---"):
        raise ValueError("Contract has no YAML frontmatter")

    _, frontmatter, _ = raw.split("---", 2)
    data = yaml.safe_load(frontmatter)

    if not isinstance(data, dict):
        raise ValueError("Invalid contract format")

    return data
