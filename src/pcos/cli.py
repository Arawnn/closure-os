from pathlib import Path
import typer
from rich import print

from pcos.config import load_config, ConfigError
from pcos.parser import load_contract, ContractError

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
