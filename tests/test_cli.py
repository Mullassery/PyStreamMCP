"""Tests for the `pystreammcp` CLI entry point (pystreammcp.cli).

Regression coverage for the "CLI is dead code" bug documented in
ROADMAP_HONEST.md §2.2: the file previously defined a Click group that
was never installed (no `[project.scripts]` entry) and never reached by
its own `if __name__ == "__main__":` guard (which called a second,
smaller, hand-rolled command set instead). These tests exercise the
actual Click group via `CliRunner`, which is what both the installed
`pystreammcp` command and `python -m pystreammcp.cli` now invoke.
"""

import json

from click.testing import CliRunner

from pystreammcp.cli import cli


def test_cli_group_lists_the_real_subcommands():
    """The advertised commands must actually be registered on the group
    (not just defined as functions nothing ever attaches)."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    for command in ("query", "server", "version", "dashboard"):
        assert command in result.output


def test_cli_version_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])

    assert result.exit_code == 0
    assert "PyStreamMCP v" in result.output


def test_cli_version_option():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0


def test_cli_query_json_output_has_real_fields():
    runner = CliRunner()
    result = runner.invoke(cli, ["query", "Find top customers", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["query_id"]
    assert payload["baseline_tokens"] > payload["optimized_tokens"]
    assert payload["cost_reduction_percent"] > 0


def test_cli_query_missing_text_errors():
    runner = CliRunner()
    result = runner.invoke(cli, ["query"])

    assert result.exit_code != 0
