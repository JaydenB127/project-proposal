"""exp-cli — command-line interface for the Experiment Tracker"""
import os
import sys
import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from exp_tracker.client import ExperimentTracker

console = Console()


def _get_tracker(api_key: str, base_url: str) -> ExperimentTracker:
    key = api_key or os.environ.get("EXP_API_KEY")
    url = base_url or os.environ.get("EXP_BASE_URL", "http://localhost:8000")
    if not key:
        console.print("[bold red]✗ No API key. Set --api-key or EXP_API_KEY env var[/bold red]")
        sys.exit(1)
    return ExperimentTracker(api_key=key, base_url=url, auto_sync_offline=False)


@click.group()
def cli():
    """🧪 Experiment Tracker CLI"""
    pass


@cli.group()
def run():
    """Manage experiment runs"""
    pass


@run.command("create")
@click.option("--name", "-n", required=True, help="Run name (pattern: proj_Model_data_YYYYMMDD)")
@click.option("--experiment", "-e", required=True, help="Experiment name")
@click.option("--params", "-p", multiple=True, help="Params as key=value (repeatable)")
@click.option("--data-version", default=None, help="Dataset version tag")
@click.option("--api-key", default=None)
@click.option("--base-url", default=None)
def create_run(name, experiment, params, data_version, api_key, base_url):
    """Create a new run"""
    tracker = _get_tracker(api_key, base_url)
    parsed_params = {}
    for p in params:
        try:
            k, v = p.split("=", 1)
            try:
                parsed_params[k] = float(v) if "." in v else int(v)
            except ValueError:
                parsed_params[k] = v
        except ValueError:
            console.print(f"[red]ERR_INVALID_PARAMS → Use key=value format (got: {p})[/red]")
            sys.exit(1)

    r = tracker.run(name=name, experiment=experiment, params=parsed_params, data_version=data_version)
    console.print(f"[green]✓ Run created[/green]")
    console.print(f"  [bold]ID:[/bold]     {r.run_id}")
    console.print(f"  [bold]Name:[/bold]   {name}")
    console.print(f"  [bold]Params:[/bold] {parsed_params}")
    # Immediately finish (for CLI one-shot use; SDK usage handles lifecycle)
    r.finish()


@run.command("list")
@click.option("--experiment", "-e", default=None)
@click.option("--status", "-s", default=None)
@click.option("--limit", default=20)
@click.option("--api-key", default=None)
@click.option("--base-url", default=None)
def list_runs(experiment, status, limit, api_key, base_url):
    """List experiment runs"""
    tracker = _get_tracker(api_key, base_url)
    runs = tracker.get_runs(experiment=experiment, status=status, limit=limit)

    table = Table(title="Experiment Runs", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="dim", max_width=10)
    table.add_column("Name")
    table.add_column("Status")
    table.add_column("Created")
    table.add_column("Git Commit", style="dim")

    STATUS_COLOR = {
        "completed": "green", "running": "yellow",
        "failed": "red", "created": "blue", "paused": "magenta"
    }
    for r in runs:
        status_str = r["status"]
        color = STATUS_COLOR.get(status_str, "white")
        table.add_row(
            r["id"][:8] + "…",
            r["name"],
            f"[{color}]{status_str}[/{color}]",
            r["created_at"][:19],
            (r.get("git_commit") or "—")[:8],
        )
    console.print(table)


@run.command("compare")
@click.option("--ids", "-i", required=True, help="Comma-separated run IDs")
@click.option("--metrics", "-m", required=True, help="Comma-separated metric keys")
@click.option("--api-key", default=None)
@click.option("--base-url", default=None)
def compare_runs(ids, metrics, api_key, base_url):
    """Compare runs side-by-side"""
    tracker = _get_tracker(api_key, base_url)
    id_list = [i.strip() for i in ids.split(",")]
    metric_list = [m.strip() for m in metrics.split(",")]
    report = tracker.compare_runs(id_list, metric_list)

    for w in report.get("warnings", []):
        console.print(f"[bold yellow]⚠ {w}[/bold yellow]")

    table = Table(title="Run Comparison", show_header=True, header_style="bold magenta")
    table.add_column("Run Name")
    table.add_column("Params")
    for m in metric_list:
        table.add_column(f"{m} (last)", justify="right")

    for r in report["results"]:
        metric_vals = []
        for m in metric_list:
            summary = r["metrics_summary"].get(m, {})
            last = summary.get("last", "—")
            metric_vals.append(f"{last:.4f}" if isinstance(last, float) else str(last))
        table.add_row(r["run_name"], str(r["params"]), *metric_vals)

    console.print(table)


@cli.command("sync")
@click.option("--api-key", default=None)
@click.option("--base-url", default=None)
def sync_offline(api_key, base_url):
    """Sync offline-buffered metrics"""
    tracker = _get_tracker(api_key, base_url)
    count = tracker.sync_offline()
    console.print(f"[green]✓ Synced {count} offline file(s)[/green]")


if __name__ == "__main__":
    cli()
