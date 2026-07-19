"""OKF (Open Knowledge Format) core module for PyStreamMCP.

Provides native OKF document storage, parsing, and search capabilities.
OKF is Google's vendor-neutral markdown/YAML specification for representing
enterprise knowledge that's optimized for AI agents and LLMs.

See: https://github.com/GoogleCloudPlatform/knowledge-catalog
"""

import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import frontmatter
except ImportError:
    raise ImportError(
        "python-frontmatter is required for OKF support. "
        "Install with: pip install python-frontmatter"
    )


class OKFDocType(str, Enum):
    """Valid OKF document types."""
    MCP_SYSTEM = "mcp-system"
    MCP_TOOL = "mcp-tool"
    QUERY_PLAN = "query-plan"
    DATA_SCHEMA = "data-schema"
    SYSTEM_LINKAGE = "system-linkage"
    PLAYBOOK = "playbook"
    CASE_STUDY = "case-study"


class OKFDocument:
    """Represents a single OKF document (YAML frontmatter + markdown content)."""

    def __init__(self, path: Path):
        """Load OKF document from disk.

        Args:
            path: Path to .md file with YAML frontmatter
        """
        self.path = path
        self.post = frontmatter.load(str(path))
        self.metadata = self.post.metadata
        self.content = self.post.content

    @property
    def doc_type(self) -> str:
        """OKF document type (mcp-system, mcp-tool, etc)."""
        return self.metadata.get("type", "unknown")

    @property
    def title(self) -> str:
        """Document title."""
        return self.metadata.get("title", self.path.stem)

    @property
    def description(self) -> str:
        """Document description."""
        return self.metadata.get("description", "")

    @property
    def tags(self) -> List[str]:
        """Document tags."""
        return self.metadata.get("tags", [])

    @property
    def related(self) -> List[str]:
        """Extract [[linked-doc.md]] references from content."""
        links = re.findall(r'\[\[(.+?\.md)\]\]', self.content)
        return links

    @property
    def timestamp(self) -> Optional[str]:
        """Last update timestamp."""
        return self.metadata.get("timestamp")

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get arbitrary metadata field."""
        return self.metadata.get(key, default)


class OKFCatalog:
    """Native OKF document store—source of truth for system and tool metadata."""

    def __init__(self, catalog_dir: Path):
        """Initialize catalog from directory.

        Args:
            catalog_dir: Root directory containing OKF documents
        """
        self.catalog_dir = Path(catalog_dir)
        self.docs: Dict[str, OKFDocument] = {}
        self.doc_index: Dict[str, List[str]] = {}  # type -> [doc_ids]
        self._ensure_structure()
        self._load_all()

    def _ensure_structure(self) -> None:
        """Create catalog directory structure if missing."""
        subdirs = [
            "systems",
            "tools",
            "query_plans",
            "schemas",
            "interconnections",
            "playbooks",
            "case_studies"
        ]
        self.catalog_dir.mkdir(parents=True, exist_ok=True)
        for subdir in subdirs:
            (self.catalog_dir / subdir).mkdir(exist_ok=True)

    def _load_all(self) -> None:
        """Load all OKF documents from disk into memory."""
        self.docs.clear()
        self.doc_index.clear()

        for doc_path in self.catalog_dir.glob("**/*.md"):
            try:
                doc = OKFDocument(doc_path)
                doc_id = str(doc_path.relative_to(self.catalog_dir))
                self.docs[doc_id] = doc

                # Index by type
                doc_type = doc.doc_type
                if doc_type not in self.doc_index:
                    self.doc_index[doc_type] = []
                self.doc_index[doc_type].append(doc_id)
            except Exception as e:
                print(f"Warning: Failed to load {doc_path}: {e}")

    def search_systems(self, query: str = "*") -> List[OKFDocument]:
        """Find MCP systems by name, tag, or keyword.

        Args:
            query: Search term or "*" for all systems

        Returns:
            List of matching MCP system documents
        """
        results = []
        query_lower = query.lower() if query != "*" else ""

        for doc_id in self.doc_index.get(OKFDocType.MCP_SYSTEM, []):
            doc = self.docs[doc_id]

            if query == "*":
                results.append(doc)
            elif (query_lower in doc.title.lower() or
                  any(query_lower in tag for tag in doc.tags) or
                  query_lower in doc.content.lower()):
                results.append(doc)

        return results

    def search_tools(self, system_id: Optional[str] = None,
                     query: str = "*") -> List[OKFDocument]:
        """Find MCP tools, optionally filtered by system.

        Args:
            system_id: Optional system to filter by (e.g., "postgres.md")
            query: Search term or "*" for all tools

        Returns:
            List of matching tool documents
        """
        results = []
        query_lower = query.lower() if query != "*" else ""

        for doc_id in self.doc_index.get(OKFDocType.MCP_TOOL, []):
            doc = self.docs[doc_id]

            # Filter by system if specified
            if system_id and system_id not in doc.content:
                continue

            # Filter by query
            if query != "*":
                if not (query_lower in doc.title.lower() or
                       any(query_lower in tag for tag in doc.tags)):
                    continue

            results.append(doc)

        return results

    def get_cost_profile(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Extract cost profile from a tool's OKF document.

        Args:
            tool_id: Tool identifier or path

        Returns:
            Cost profile dict or None if not found
        """
        for doc_id, doc in self.docs.items():
            if doc.doc_type == OKFDocType.MCP_TOOL and tool_id in doc_id:
                return {
                    "cost_per_call": doc.get_metadata("cost"),
                    "latency_p95_ms": doc.get_metadata("latency_p95_ms"),
                    "latency_p99_ms": doc.get_metadata("latency_p99_ms"),
                    "cache_hit_rate": doc.get_metadata("cache_hit_rate"),
                }
        return None

    def find_relationships(self, system_id: str) -> List[OKFDocument]:
        """Navigate system interconnections via OKF linkage docs.

        Args:
            system_id: System identifier to find relationships for

        Returns:
            List of system linkage documents
        """
        relationships = []

        for doc_id in self.doc_index.get(OKFDocType.SYSTEM_LINKAGE, []):
            doc = self.docs[doc_id]
            source = doc.get_metadata("source_system")
            target = doc.get_metadata("target_system")

            if system_id in [source, target]:
                relationships.append(doc)

        return relationships

    def find_by_type(self, doc_type: str) -> List[OKFDocument]:
        """Get all documents of a specific type.

        Args:
            doc_type: OKF document type

        Returns:
            List of documents matching type
        """
        results = []
        for doc_id in self.doc_index.get(doc_type, []):
            results.append(self.docs[doc_id])
        return results

    def save_document(self, doc_type: str, title: str, content: str,
                     metadata: Optional[Dict[str, Any]] = None) -> Path:
        """Save a new OKF document to catalog.

        Args:
            doc_type: OKF document type
            title: Document title
            content: Markdown content
            metadata: Additional YAML metadata

        Returns:
            Path to saved document
        """
        if metadata is None:
            metadata = {}

        # Convert Enum to string if needed
        if isinstance(doc_type, OKFDocType):
            doc_type_str = doc_type.value
        else:
            doc_type_str = str(doc_type)

        # Convert any Enum values in metadata to strings
        clean_metadata = {}
        for key, value in metadata.items():
            if isinstance(value, Enum):
                clean_metadata[key] = value.value
            elif isinstance(value, list):
                clean_metadata[key] = [v.value if isinstance(v, Enum) else v for v in value]
            else:
                clean_metadata[key] = value

        clean_metadata.update({
            "type": doc_type_str,
            "title": title,
            "timestamp": datetime.now().isoformat(),
        })

        # Determine subdirectory
        subdir_map = {
            OKFDocType.MCP_SYSTEM: "systems",
            OKFDocType.MCP_TOOL: "tools",
            OKFDocType.QUERY_PLAN: "query_plans",
            OKFDocType.DATA_SCHEMA: "schemas",
            OKFDocType.SYSTEM_LINKAGE: "interconnections",
            OKFDocType.PLAYBOOK: "playbooks",
            OKFDocType.CASE_STUDY: "case_studies",
        }
        subdir = subdir_map.get(doc_type, "misc")

        # Generate filename from title
        filename = title.lower().replace(" ", "_").replace("/", "_") + ".md"
        doc_path = self.catalog_dir / subdir / filename

        # Create OKF document
        post = frontmatter.Post(content)
        post.metadata = clean_metadata

        doc_path.write_text(frontmatter.dumps(post))

        # Reload to sync index
        self._load_all()

        return doc_path

    def reload(self) -> None:
        """Reload catalog from disk (useful after external changes)."""
        self._load_all()
