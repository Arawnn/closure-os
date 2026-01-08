from pathlib import Path
import typer
from rich import print

from pcos.config import load_config, ConfigError
from pcos.parser import load_contract, ContractError

from pcos.obsidian import ObsidianClient, ObsidianError
from pcos.parser import read_input_text
from pcos.config import get_env

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