from rich.console import Console
from rich.table import Table
from rich.logging import RichHandler
import logging


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()]
    )


def display_help():
    console = Console()

    table = Table(title="[bold]Fetch Command[/bold]", title_style="bold cyan")
    table.add_column("[bold]Options[/bold]", style="cyan", justify="left")
    table.add_column("[bold]Description[/bold]", style="magenta", justify="left")

    table.add_row("[yellow]-t, --ticker TICKER[/yellow]", "Ticker symbol (required)")
    table.add_row("[yellow]-s, --source {yahoo}[/yellow]", "Data source (default: yahoo)")
    table.add_row("[yellow]-z, --timezone TIMEZONE[/yellow]", "Timezone")
    table.add_row("[yellow]--asset-type {stock,etf,crypto,currency,commodity}[/yellow]",
                  "Asset type to fetch data for (required)")

    console.print("\n[bold yellow]Usage:[/bold yellow]\n")
    console.print("guard fetch [OPTIONS]\n")

    console.print("\n[bold yellow]Options:[/bold yellow]\n")
    console.print(table)

    console.print("\n[bold yellow]Description:[/bold yellow]\n")
    console.print("Fetch data from different sources.\n")


if __name__ == "__main__":
    setup_logging()
    display_help()
