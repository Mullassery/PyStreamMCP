"""Example: PyStreamMCP MCP 2.0 Multi-Project Orchestration"""

import logging
import time

from pystreammcp import Orchestrator

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 70)
    logger.info("PyStreamMCP MCP 2.0 Multi-Project Orchestration")
    logger.info("=" * 70)

    orchestrator = Orchestrator()

    logger.info("\n1. Starting MCP orchestrator...")
    try:
        endpoint = orchestrator.start_mcp_connector(port=8772)
        logger.info(f"✓ MCP endpoint ready: {endpoint}")
    except Exception as e:
        logger.error(f"Failed: {e}")
        return

    logger.info("\n2. MCP Tools Available (12 total):")
    tools = [
        "discover_mcp_projects",
        "plan_query_execution",
        "optimize_cross_project_query",
        "execute_federated_query",
        "detect_compatible_projects",
        "rank_tools_by_relevance",
        "handle_cross_database_join",
        "cache_management",
        "error_recovery_retry",
        "report_performance_metrics",
        "estimate_query_cost_multi_project",
        "manage_endpoint_federation",
    ]
    for i, tool in enumerate(tools, 1):
        logger.info(f"  {i:2d}. {tool}")

    logger.info("\n3. Connected Projects & Tools:")
    projects = [
        ("StatGuardian", 8765, 9, "Data Quality"),
        ("PyReverseETL", 8766, 12, "Data Activation"),
        ("PrismNote", 8767, 10, "SQL Queries"),
        ("ClusterAudienceKit", 8768, 10, "Segmentation"),
        ("PyWeatherEnriched", 8769, 10, "Weather"),
        ("PyTerrainMap", 8770, 10, "Spatial"),
        ("PyRoboFrames", 8771, 11, "Datasets"),
    ]
    total_projects = len(projects)
    total_tools = sum(t[2] for t in projects)
    for name, port, tools_count, capability in projects:
        logger.info(f"  • {name:20s} ({port}) — {tools_count:2d} tools — {capability}")

    logger.info(f"\n4. Platform Summary:")
    logger.info(f"  Total Projects:   {total_projects}")
    logger.info(f"  Total Tools:      {total_tools}")
    logger.info(f"  Orchestrator:     Port 8772 (12 tools)")
    logger.info(f"  Total MCP Tools:  {total_tools + 12}")

    logger.info("\n5. Claude Can Now:")
    logger.info('  • "What MCP tools are available?"')
    logger.info('  • "Plan a data pipeline: validate → segment → sync"')
    logger.info('  • "Optimize this query to reduce tokens by 70%"')
    logger.info('  • "Execute federated query across all projects"')
    logger.info('  • "Which projects can correlate weather with revenue?"')
    logger.info('  • "Join data from PrismNote and ClusterAudienceKit"')
    logger.info('  • "Get performance metrics for the last 24 hours"')

    logger.info("\n   MCP orchestrator is running! Press Ctrl+C to stop...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n\nStopping...")
        orchestrator.stop_mcp_connector()


if __name__ == "__main__":
    main()
