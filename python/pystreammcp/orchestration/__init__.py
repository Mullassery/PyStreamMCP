"""Orchestration helpers for PyStreamMCP.

Temporal and Apache Airflow modules are experimental, unsupported in-process
helpers, not vendor SDK integrations. Constructing them requires an explicit
opt-in. The n8n/Power Automate/UiPath/Automation Anywhere classes are local
helpers that model webhook/RPA payloads; they are not vendor clients either.
"""

from .airflow import (
    AirflowOperatorConfig,
    PyStreamMCPDAGFactory,
    PyStreamMCPDiscoveryOperator,
    PyStreamMCPOptimizeOperator,
    PyStreamMCPQueryOperator,
)
from .temporal import (
    TemporalClient,
    TemporalDiscoveryActivity,
    TemporalQueryActivity,
    TemporalWorkflow,
)

__all__ = [
    "AirflowOperatorConfig",
    "PyStreamMCPDAGFactory",
    "PyStreamMCPDiscoveryOperator",
    "PyStreamMCPOptimizeOperator",
    "PyStreamMCPQueryOperator",
    "TemporalClient",
    "TemporalDiscoveryActivity",
    "TemporalQueryActivity",
    "TemporalWorkflow",
]
