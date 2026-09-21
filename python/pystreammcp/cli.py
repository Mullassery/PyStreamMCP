"""CLI for PyStreamMCP - command-line interface for workflow tools."""

import json
import sys
import click

from pystreammcp import Agent, __version__
from pystreammcp.cli_dashboard import PyStreamMCPDashboard


@click.group()
@click.version_option(version=__version__)
def cli():
    """PyStreamMCP - Intelligence Layer for AI Agents."""
    pass


@cli.command()
@click.argument("query_text")
@click.option("--agent-id", default="cli_agent", help="Agent ID")
@click.option(
    "--intent",
    type=click.Choice(["retrieve", "discover", "aggregate", "synthesize", "analyze"]),
    default="retrieve",
)
@click.option(
    "--strategy",
    type=click.Choice(["balanced", "token_efficient", "quality_first"]),
    default="balanced",
)
@click.option("--max-tokens", type=int, default=2000)
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def query(
    query_text: str,
    agent_id: str,
    intent: str,
    strategy: str,
    max_tokens: int,
    output_json: bool,
):
    """Execute optimized query."""
    try:
        agent = Agent(
            agent_id=agent_id,
            optimization_strategy=strategy,
            max_tokens=max_tokens,
        )
        result = agent.query(query_text)

        if output_json:
            click.echo(
                json.dumps(
                    {
                        "query_id": result.query_id,
                        "baseline_tokens": result.baseline_tokens,
                        "optimized_tokens": result.optimized_tokens,
                        "cost_reduction_percent": result.cost_reduction_percent,
                        "execution_time_ms": result.execution_time_ms,
                    },
                    indent=2,
                )
            )
        else:
            click.echo(f"Query ID: {result.query_id}")
            click.echo(f"Reduction: {result.cost_reduction_percent:.1f}%")
            click.echo(f"Time: {result.execution_time_ms:.1f}ms")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise SystemExit(1)


@cli.command()
@click.option(
    "--host",
    default="127.0.0.1",
    help="Bind address. Defaults to localhost-only; pass --host 0.0.0.0 "
    "explicitly to accept connections from other hosts (e.g. in a "
    "container behind its own network boundary).",
)
@click.option("--port", type=int, default=8000)
@click.option("--reload", is_flag=True)
def server(host: str, port: int, reload: bool):
    """Start PyStreamMCP API server."""
    try:
        from pystreammcp.api import PyStreamMCPAPI
    except ImportError:
        click.echo(
            "Error: the 'server' command requires the 'api' extra. "
            "Install with: pip install 'pystreammcp[api]'",
            err=True,
        )
        raise SystemExit(1)

    click.echo(f"Starting server on {host}:{port}...")
    api = PyStreamMCPAPI()
    api.run(host=host, port=port, reload=reload)


@cli.command()
def version():
    """Show version."""
    click.echo(f"PyStreamMCP v{__version__}")


@cli.command()
@click.option("--static", is_flag=True, help="Show static snapshot (non-interactive)")
@click.option("--alerts", is_flag=True, help="Show alerts only")
@click.option("--recommendations", is_flag=True, help="Show recommendations only")
@click.option("--export", type=str, metavar="FILE", help="Export metrics to JSON file")
@click.option("--config", type=str, metavar="PATH", help="Path to config file")
def dashboard(
    static: bool, alerts: bool, recommendations: bool, export: str, config: str
):
    """View real-time orchestration dashboard."""
    try:
        dash = PyStreamMCPDashboard(config_path=config)

        if export:
            dash.export_json(export)
        elif alerts:
            dash.show_alerts()
        elif recommendations:
            dash.show_recommendations()
        else:
            dash.run_dashboard(interactive=not static)

    except KeyboardInterrupt:
        click.echo("\n\nDashboard stopped.")
        sys.exit(0)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
