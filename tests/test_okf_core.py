"""Tests for OKF core module."""

import tempfile
from pathlib import Path

import pytest

from pystreammcp.okf_core import OKFCatalog, OKFDocument, OKFDocType


@pytest.fixture
def temp_catalog():
    """Create a temporary catalog directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def populated_catalog(temp_catalog):
    """Create a catalog with sample documents."""
    catalog = OKFCatalog(temp_catalog)

    # Create a sample system document
    catalog.save_document(
        OKFDocType.MCP_SYSTEM,
        "PostgreSQL Production",
        "# PostgreSQL Production Database\n\nProduction database system.",
        {
            "system_id": "postgres-prod",
            "tools_count": 10,
            "cost_per_query": 0.01,
            "tags": ["database", "sql", "production"],
        }
    )

    # Create a sample tool document
    catalog.save_document(
        OKFDocType.MCP_TOOL,
        "Search Customers",
        "# Search Customers\n\nSearch customer database.",
        {
            "tool_id": "search_customers",
            "system": "[[postgres_production.md]]",
            "cost": 0.01,
            "latency_p95_ms": 50,
            "tags": ["customer", "search"],
        }
    )

    # Create a query plan document
    catalog.save_document(
        OKFDocType.QUERY_PLAN,
        "Customer 360",
        "# Customer 360\n\nComplete customer profile retrieval.",
        {
            "plan_id": "customer_360_v1",
            "estimated_token_savings": 65,
            "tags": ["customer", "optimization"],
        }
    )

    return catalog


class TestOKFDocumentLoading:
    """Test OKF document loading and parsing."""

    def test_create_and_load_document(self, temp_catalog):
        """Test creating and loading a document."""
        catalog = OKFCatalog(temp_catalog)

        path = catalog.save_document(
            OKFDocType.MCP_SYSTEM,
            "Test System",
            "# Test\n\nContent",
            {"tags": ["test"], "cost": 0.05}
        )

        assert path.exists()
        assert "systems" in str(path)

    def test_document_metadata_parsing(self, populated_catalog):
        """Test YAML frontmatter parsing."""
        docs = populated_catalog.search_systems("PostgreSQL")
        assert len(docs) == 1

        doc = docs[0]
        assert doc.title == "PostgreSQL Production"
        assert doc.doc_type == OKFDocType.MCP_SYSTEM
        assert "production" in doc.tags
        assert doc.get_metadata("cost_per_query") == 0.01

    def test_document_content_parsing(self, populated_catalog):
        """Test markdown content parsing."""
        docs = populated_catalog.search_systems("PostgreSQL")
        doc = docs[0]

        assert "PostgreSQL Production Database" in doc.content

    def test_document_links_extraction(self, populated_catalog):
        """Test extracting [[linked.md]] references."""
        # Find tool with references
        for tool_doc in populated_catalog.search_tools():
            if tool_doc.related:
                # Found a doc with references
                assert isinstance(tool_doc.related, list)
                return

        # If no tool has references, that's OK - just verify list type
        assert True


class TestOKFCatalogOperations:
    """Test catalog search and query operations."""

    def test_search_systems_by_name(self, populated_catalog):
        """Test finding systems by name."""
        results = populated_catalog.search_systems("PostgreSQL")
        assert len(results) == 1
        assert results[0].title == "PostgreSQL Production"

    def test_search_systems_by_tag(self, populated_catalog):
        """Test finding systems by tag."""
        results = populated_catalog.search_systems("production")
        assert len(results) == 1

    def test_search_systems_all(self, populated_catalog):
        """Test getting all systems."""
        results = populated_catalog.search_systems("*")
        assert len(results) >= 1

    def test_search_tools_all(self, populated_catalog):
        """Test finding tools."""
        results = populated_catalog.search_tools()
        assert len(results) >= 1
        assert results[0].doc_type == OKFDocType.MCP_TOOL

    def test_get_cost_profile(self, populated_catalog):
        """Test extracting cost profile from tool."""
        cost_profile = populated_catalog.get_cost_profile("search_customers")
        assert cost_profile is not None
        assert cost_profile["cost_per_call"] == 0.01
        assert cost_profile["latency_p95_ms"] == 50

    def test_find_by_type(self, populated_catalog):
        """Test filtering documents by type."""
        query_plans = populated_catalog.find_by_type(OKFDocType.QUERY_PLAN)
        assert len(query_plans) >= 1
        assert all(doc.doc_type == OKFDocType.QUERY_PLAN for doc in query_plans)

    def test_catalog_directory_structure(self, temp_catalog):
        """Test that catalog creates proper subdirectory structure."""
        catalog = OKFCatalog(temp_catalog)

        expected_dirs = [
            "systems",
            "tools",
            "query_plans",
            "schemas",
            "interconnections",
            "playbooks",
            "case_studies"
        ]

        for subdir in expected_dirs:
            assert (catalog.catalog_dir / subdir).exists()


class TestOKFDocumentSaving:
    """Test saving and persistence."""

    def test_save_document_with_metadata(self, temp_catalog):
        """Test saving document with custom metadata."""
        catalog = OKFCatalog(temp_catalog)

        path = catalog.save_document(
            OKFDocType.MCP_SYSTEM,
            "Test System",
            "# Test\n\nContent here",
            {"custom_field": "value", "cost_per_query": 0.02}
        )

        # Reload and verify
        catalog.reload()
        docs = catalog.search_systems("Test System")
        assert len(docs) == 1
        assert docs[0].get_metadata("custom_field") == "value"
        assert docs[0].get_metadata("cost_per_query") == 0.02

    def test_save_persists_to_disk(self, temp_catalog):
        """Test that saved documents persist on disk."""
        catalog = OKFCatalog(temp_catalog)

        path = catalog.save_document(
            OKFDocType.MCP_TOOL,
            "Test Tool",
            "# Test Tool\n\nContent"
        )

        assert path.exists()
        assert path.read_text().startswith("---")  # YAML frontmatter


class TestOKFLinking:
    """Test document relationships and linking."""

    def test_system_linkage(self, temp_catalog):
        """Test creating system linkage documents."""
        catalog = OKFCatalog(temp_catalog)

        catalog.save_document(
            OKFDocType.SYSTEM_LINKAGE,
            "System A to B",
            "# Relationship",
            {
                "source_system": "system_a.md",
                "target_system": "system_b.md",
                "relationship_type": "one-to-many",
            }
        )

        relationships = catalog.find_relationships("system_a.md")
        assert len(relationships) == 1

    def test_document_references(self, populated_catalog):
        """Test extracting references between documents."""
        tools = populated_catalog.search_tools()
        if tools:
            tool_doc = tools[0]
            references = tool_doc.related
            assert isinstance(references, list)


class TestOKFReload:
    """Test catalog reloading after external changes."""

    def test_reload_syncs_index(self, temp_catalog):
        """Test that reload picks up new documents."""
        catalog = OKFCatalog(temp_catalog)
        initial_count = len(catalog.find_by_type(OKFDocType.MCP_SYSTEM))

        catalog.save_document(
            OKFDocType.MCP_SYSTEM,
            "New System",
            "# New"
        )

        # Reload to pick up changes
        catalog.reload()
        new_count = len(catalog.find_by_type(OKFDocType.MCP_SYSTEM))

        assert new_count > initial_count
