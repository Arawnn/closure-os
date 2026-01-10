from pathlib import Path
import typer
from rich import print

from pcos.config import load_config, ConfigError
from pcos.parser import load_contract, ContractError

from pcos.obsidian import ObsidianClient, ObsidianError
from pcos.parser import read_input_text
from pcos.config import get_env

from typing import Optional, Set

from pcos.clipboard_watcher import (
    watch_clipboard,
    DEFAULT_ALLOWED_TAGS,
    DEFAULT_DEBOUNCE_SECONDS,
    DEFAULT_CHECK_INTERVAL,
)

from pcos.contract_generator import generate_contract

from pcos.contracts import load_project_contract
from pcos.github import GitHubClient
from pcos.renderers import render_readme
from pcos.issues import sync_issues



app = typer.Typer()


@app.command()
def validate(
    contract: Path = typer.Argument(..., exists=True),
    config: Path = typer.Option("config.yaml"),
):
    """
    Validate configuration and contract file.
    """
    try:
        cfg = load_config(config)
        print("[green]✓ Config loaded[/green]")
    except ConfigError as e:
        print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(1)

    try:
        contract_data = load_contract(contract)
        print("[green]✓ Contract loaded[/green]")
    except ContractError as e:
        print(f"[red]Contract error:[/red] {e}")
        raise typer.Exit(1)

    print("\n[bold]Contract summary[/bold]")
    print(f"Project: {contract_data['project']}")
    print(f"Deadline: {contract_data['deadline']}")
    print(f"Tickets: {len(contract_data['tickets'])}")

@app.command()
def capture(
    project: str = typer.Option(..., help="Project name"),
    input: Path = typer.Option(None, exists=True, help="Markdown file to import"),
    config: Path = typer.Option("config.yaml"),
):
    """
    Capture markdown into Obsidian as 00_brainstorm.md
    """
    try:
        cfg = load_config(Path(config))
        print("[green]✓ Config loaded[/green]")
    except ConfigError as e:
        print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(1)

    try:
        text = read_input_text(input)
        if not text.strip():
            raise ValueError("Empty input")
    except Exception as e:
        print(f"[red]Input error:[/red] {e}")
        raise typer.Exit(1)

    try:
        client = ObsidianClient(
            base_url=cfg["obsidian_api_base"],
            vault_name=cfg["vault_name"],
            api_key=get_env("OBSIDIAN_API_KEY"),
        )

        note_path = f"{cfg['projects_root']}/{project}/00_brainstorm.md"
        client.write_note(note_path, text)

        print(f"[green]✓ Brainstorm captured[/green]")
        print(f"[dim]{note_path}[/dim]")

    except ObsidianError as e:
        print(f"[red]Obsidian error:[/red] {e}")
        raise typer.Exit(1)
    
@app.command()
def watch(
    project: Optional[str] = typer.Option(
        None,
        help="Force project name (otherwise read from frontmatter)",
    ),
    allowed_tags: str = typer.Option(
        ",".join(sorted(DEFAULT_ALLOWED_TAGS)),
        help="Comma-separated allowed tags",
    ),
    debounce: float = typer.Option(
        DEFAULT_DEBOUNCE_SECONDS,
        help="Debounce delay in seconds",
    ),
    interval: float = typer.Option(
        DEFAULT_CHECK_INTERVAL,
        help="Clipboard polling interval in seconds",
    ),
):
    """
    Watch clipboard and automatically capture brainstorm markdown into Obsidian.
    """

    tag_set: Set[str] = {
        tag.strip().lower()
        for tag in allowed_tags.split(",")
        if tag.strip()
    }

    if not tag_set:
        print("[red]No allowed tags provided[/red]")
        raise typer.Exit(1)

    watch_clipboard(
        project=project,
        allowed_tags=tag_set,
        debounce_seconds=debounce,
        check_interval=interval,
    )

@app.command()
def contract(project: str):
    """
    Generate project contract from brainstorm using LLM.
    """

    from pathlib import Path

    try:
        cfg = load_config(Path("config.yaml"))
        print("[green]✓ Config loaded[/green]")
    except ConfigError as e:
        print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(1)

    try:
        path = generate_contract(cfg, project)
        print(f"[green]✓ Contract generated[/green]")
        print(f"[dim]{path}[/dim]")
    except Exception as e:
        print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    print(f"📄 Contract generated: {path}")

@app.command()
def publish(project: str):
    """
    Publish project to GitHub (repo, README, issues).
    """
    try:
        cfg = load_config(Path("config.yaml"))
        print("[green]✓ Config loaded[/green]")
    except ConfigError as e:
        print(f"[red]Config error:[/red] {e}")
        raise typer.Exit(1)

    print("✓ Loading contract")
    contract = load_project_contract(cfg, project)

    repo_name = project.lower().replace(" ", "-")

    gh = GitHubClient()
    print("✓ Getting authenticated user")
    user = gh.get_user()
    owner = user["login"]
    print("✓ Resolving repo")
    repo = gh.get_repo(owner, repo_name)
    if not repo:
        print(f"📦 Creating repo {owner}/{repo_name}")
        gh.create_repo(repo_name, private=False)
    else:
        print(f"📦 Repo exists {owner}/{repo_name}")

    print("✓ Sync README")
    readme = render_readme(contract)
    gh.upsert_readme(owner, repo_name, readme)

    print("✓ Sync issues")
    tickets = contract.get("tickets", [])
    created = sync_issues(gh, owner, repo_name, tickets)

    print(f"🐛 Issues created: {created}")
    print("✅ Publish done")


