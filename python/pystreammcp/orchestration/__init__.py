"""Orchestration tool integrations for PyStreamMCP.

Enables workflow orchestration platforms to use PyStreamMCP for
intelligent query planning and cost optimization in automated workflows.

Supported tools:
- Temporal (durable execution, event sourcing)
- Apache Airflow (DAGs, scheduling, backfill)
- n8n (no-code workflows, integrations)
- Power Automate (Microsoft cloud workflows)
- UiPath (Robotic Process Automation)
- Automation Anywhere (RPA platform)
"""

__all__ = [
    "TemporalWorkflow",
    "TemporalActivity",
    "AirflowOperator",
    "N8nWebhook",
    "PowerAutomateConnector",
    "RoboticProcessAdapter",
]
