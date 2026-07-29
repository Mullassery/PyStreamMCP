"""
PyStreamMCP CLI Dashboard - Real-time orchestration monitoring

Shows: connected MCP tools, execution status, performance metrics
"""

import sys
import platform
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class DashboardMetrics:
    """Standard metrics container"""
    timestamp: str
    title: str
    metrics: Dict[str, Any]
    alerts: list
    recommendations: list


def get_dashboard_impl(product_name: str):
    """Get platform-specific dashboard implementation"""
    platform_name = platform.system()

    if platform_name == "Darwin":  # macOS
        try:
            from rich.console import Console
            return RichDashboard(product_name)
        except ImportError:
            return SimpleDashboard(product_name)

    elif platform_name == "Linux":
        try:
            from textual.app import App
            return TextualDashboard(product_name)
        except ImportError:
            try:
                from rich.console import Console
                return RichDashboard(product_name)
            except ImportError:
                return SimpleDashboard(product_name)

    else:  # Windows or other
        try:
            from rich.console import Console
            return RichDashboard(product_name)
        except ImportError:
            return SimpleDashboard(product_name)


class SimpleDashboard:
    """Fallback plain-text dashboard"""

    def __init__(self, product_name: str):
        self.product_name = product_name

    def render(self, data: DashboardMetrics) -> None:
        print(f"\n{'='*80}")
        print(f"✓ {data.title}")
        print(f"  {data.timestamp}")
        print(f"{'='*80}\n")

        print("KEY METRICS:")
        for key, value in data.metrics.items():
            if isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k}: {v}")
            else:
                print(f"  {key}: {value}")

        if data.alerts:
            print("\n⚠️  ALERTS:")
            for alert in data.alerts:
                print(f"  [{alert.get('level', '').upper()}] {alert.get('message', '')}")

        if data.recommendations:
            print("\n💡 RECOMMENDATIONS:")
            for rec in data.recommendations:
                print(f"  [{rec.get('type', '').upper()}] {rec.get('message', '')}")

        print(f"\n{'='*80}\n")

    def run(self) -> None:
        sample_data = DashboardMetrics(
            timestamp=datetime.now().isoformat(),
            title=f"{self.product_name} Dashboard",
            metrics={"Status": "Active"},
            alerts=[],
            recommendations=[]
        )
        self.render(sample_data)


class RichDashboard:
    """Rich-based dashboard (macOS and Windows primary)"""

    def __init__(self, product_name: str):
        self.product_name = product_name
        try:
            from rich.console import Console
            self.console = Console()
        except ImportError:
            print("Error: Rich library required. Install with: pip install rich")
            sys.exit(1)

    def render(self, data: DashboardMetrics) -> None:
        from rich.table import Table

        self.console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
        self.console.print(f"[bold cyan]✓ {data.title}[/bold cyan]")
        self.console.print(f"[dim cyan]{data.timestamp}[/dim cyan]")
        self.console.print(f"[bold cyan]{'='*80}[/bold cyan]\n")

        # Metrics table
        table = Table(title="[bold]Key Metrics[/bold]")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        for key, value in data.metrics.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    table.add_row(f"  {key} → {k}", str(v))
            else:
                table.add_row(key, str(value))

        self.console.print(table)

        # Alerts
        if data.alerts:
            self.console.print("\n[bold red]⚠️  ALERTS[/bold red]")
            for alert in data.alerts:
                level = alert.get("level", "info").upper()
                msg = alert.get("message", "")
                self.console.print(f"  [{level}] {msg}")

        # Recommendations
        if data.recommendations:
            self.console.print("\n[bold yellow]💡 RECOMMENDATIONS[/bold yellow]")
            for rec in data.recommendations:
                rec_type = rec.get("type", "").upper()
                msg = rec.get("message", "")
                self.console.print(f"  [{rec_type}] {msg}")

        self.console.print(f"\n[bold cyan]{'='*80}[/bold cyan]\n")

    def run(self) -> None:
        sample_data = DashboardMetrics(
            timestamp=datetime.now().isoformat(),
            title=f"{self.product_name} Dashboard",
            metrics={"Status": "Active ✓"},
            alerts=[],
            recommendations=[]
        )
        self.render(sample_data)


class TextualDashboard:
    """Textual-based interactive dashboard (Linux)"""

    def __init__(self, product_name: str):
        self.product_name = product_name
        self.has_textual = False
        try:
            from textual.app import App
            self.has_textual = True
        except ImportError:
            pass

    def render(self, data: DashboardMetrics) -> None:
        if not self.has_textual:
            dash = RichDashboard(self.product_name)
            dash.render(data)
            return

        dash = RichDashboard(self.product_name)
        dash.render(data)

    def run(self) -> None:
        if not self.has_textual:
            dash = RichDashboard(self.product_name)
            dash.run()
            return

        sample_data = DashboardMetrics(
            timestamp=datetime.now().isoformat(),
            title=f"{self.product_name} Dashboard",
            metrics={"Status": "Active ✓"},
            alerts=[],
            recommendations=[]
        )
        self.render(sample_data)


class PyStreamMCPDashboard:
    """PyStreamMCP-specific dashboard implementation"""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "./pystreammcp.yaml"
        self.dashboard = get_dashboard_impl("PyStreamMCP v2.0")

    def get_mock_metrics(self) -> DashboardMetrics:
        """Get sample metrics (replace with real metrics in production)"""
        return DashboardMetrics(
            timestamp=datetime.now().isoformat(),
            title="PyStreamMCP Orchestration Dashboard",
            metrics={
                "Status": "🟢 Active",
                "Uptime": "5 days 12h 45m",
                "Connected Tools": 8,
                "Active Routes": 12,
                "Total Executions": "567,234",
                "Connected Tools Details": {
                    "calculator": "✓ 2.4ms avg",
                    "web_search": "✓ 156ms avg",
                    "file_editor": "✓ 12ms avg",
                    "code_executor": "✓ 89ms avg",
                    "browser": "✓ 234ms avg",
                    "knowledge_base": "✓ 45ms avg",
                    "email_client": "✓ 234ms avg",
                    "data_analyzer": "✓ 123ms avg",
                },
                "Selective Intelligence": {
                    "Filtered": "47%",
                    "Processed": "53%",
                    "Avg Reduction": "90-95%",
                },
                "Active Execution Jobs": {
                    "Running": "3 jobs",
                    "Queued": "8 jobs",
                    "Completed (24h)": "1,234 jobs",
                },
                "Routing Performance": {
                    "Success Rate": "99.8%",
                    "Avg Latency": "145ms",
                    "P99 Latency": "287ms",
                },
                "Resource Usage": {
                    "Memory": "2.4/8 GB",
                    "CPU": "34%",
                    "Network": "12.5 Mbps",
                },
            },
            alerts=[
                {"level": "info", "message": "All orchestration systems operational"},
                {"level": "warning", "message": "web_search latency trending up (156ms)"},
            ],
            recommendations=[
                {"type": "routing", "message": "Consider routing 20% of web_search to backup tool"},
                {"type": "performance", "message": "browser tool latency at 234ms - may need optimization"},
            ]
        )

    def run_dashboard(self, interactive: bool = True) -> None:
        """Run the dashboard"""
        try:
            metrics = self.get_mock_metrics()

            if interactive:
                self.dashboard.run()
            else:
                self.dashboard.render(metrics)

        except KeyboardInterrupt:
            print("\n\nDashboard stopped.")
            sys.exit(0)
        except Exception as e:
            print(f"Error running dashboard: {e}", file=sys.stderr)
            sys.exit(1)

    def show_alerts(self) -> None:
        """Show only alerts"""
        metrics = self.get_mock_metrics()
        print("\n[ALERTS]")
        if metrics.alerts:
            for alert in metrics.alerts:
                print(f"  [{alert['level'].upper()}] {alert['message']}")
        else:
            print("  ✓ No alerts")

    def show_recommendations(self) -> None:
        """Show only recommendations"""
        metrics = self.get_mock_metrics()
        print("\n[RECOMMENDATIONS]")
        if metrics.recommendations:
            for rec in metrics.recommendations:
                print(f"  [{rec['type'].upper()}] {rec['message']}")
        else:
            print("  ✓ No recommendations")

    def export_json(self, output_file: str) -> None:
        """Export metrics as JSON"""
        import json
        metrics = self.get_mock_metrics()
        data = {
            "timestamp": metrics.timestamp,
            "title": metrics.title,
            "metrics": metrics.metrics,
            "alerts": metrics.alerts,
            "recommendations": metrics.recommendations,
        }
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✓ Metrics exported to {output_file}")
