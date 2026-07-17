"""PyStreamMCP ↔ StatGuardian Integration - Context Quality Validation

This module provides quality validation gates for discovered context using StatGuardian.
Ensures all context included in queries has passed data quality checks.
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class QualityStatus(str, Enum):
    """Quality status of a data source."""
    VALID = "valid"
    INVALID = "invalid"
    STALE = "stale"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"


@dataclass
class QualityCheck:
    """A single quality check result."""
    check_name: str
    passed: bool
    score: float  # 0.0-1.0
    message: str = ""
    checked_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        self.score = max(0.0, min(1.0, self.score))


@dataclass
class ValidationResult:
    """Result of validating data source quality."""
    dataset_id: str
    status: QualityStatus
    quality_score: float  # 0.0-1.0
    checks: List[QualityCheck] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    last_validated: datetime = field(default_factory=datetime.utcnow)
    validation_id: str = ""

    def __post_init__(self):
        self.quality_score = max(0.0, min(1.0, self.quality_score))
        if not self.validation_id:
            import uuid
            self.validation_id = str(uuid.uuid4())

    def is_valid(self) -> bool:
        """Check if data source is valid."""
        return self.status == QualityStatus.VALID

    def is_usable(self, max_staleness_seconds: Optional[int] = None) -> bool:
        """Check if data source is usable (valid or acceptably stale)."""
        if self.status == QualityStatus.VALID:
            return True

        if self.status == QualityStatus.STALE and max_staleness_seconds:
            age = (datetime.utcnow() - self.last_validated).total_seconds()
            return age <= max_staleness_seconds

        if self.status == QualityStatus.DEGRADED:
            # Use degraded data if quality score is acceptable
            return self.quality_score >= 0.7

        return False

    def add_check(self, check: QualityCheck) -> "ValidationResult":
        """Add a quality check result."""
        self.checks.append(check)
        return self

    def add_error(self, error: str) -> "ValidationResult":
        """Add an error message."""
        self.errors.append(error)
        return self


@dataclass
class ValidationGate:
    """Configuration for a quality validation gate."""
    dataset_id: str
    enabled: bool = True
    block_on_failure: bool = True
    min_quality_score: float = 0.7  # 0.0-1.0
    max_staleness_seconds: int = 3600  # 1 hour
    require_recent_check: bool = True

    def __post_init__(self):
        self.min_quality_score = max(0.0, min(1.0, self.min_quality_score))


class QualityValidator:
    """Validates data source quality using StatGuardian contracts."""

    def __init__(self, statguardian_enabled: bool = True):
        """
        Initialize quality validator.

        Args:
            statguardian_enabled: Whether StatGuardian validation is enabled
        """
        self.statguardian_enabled = statguardian_enabled
        self._validation_cache: Dict[str, ValidationResult] = {}
        self._gates: Dict[str, ValidationGate] = {}
        logger.info(f"QualityValidator initialized (StatGuardian: {statguardian_enabled})")

    def register_gate(self, gate: ValidationGate) -> None:
        """Register a validation gate for a dataset."""
        self._gates[gate.dataset_id] = gate
        logger.debug(f"Registered validation gate for dataset: {gate.dataset_id}")

    def validate(self, dataset_id: str, source_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate a data source using StatGuardian.

        Args:
            dataset_id: ID of the dataset to validate
            source_data: The data to validate (schema + sample rows)

        Returns:
            ValidationResult with status and quality score
        """
        gate = self._gates.get(dataset_id)
        if not gate or not gate.enabled:
            logger.debug(f"No validation gate for {dataset_id}, skipping validation")
            return ValidationResult(
                dataset_id=dataset_id,
                status=QualityStatus.UNKNOWN,
                quality_score=1.0,
            )

        # Check cache first
        cached = self._validation_cache.get(dataset_id)
        if cached:
            age = (datetime.utcnow() - cached.last_validated).total_seconds()
            if age < gate.max_staleness_seconds:
                logger.debug(f"Using cached validation for {dataset_id}")
                return cached

        # Perform validation
        result = self._perform_validation(dataset_id, source_data, gate)

        # Cache result
        self._validation_cache[dataset_id] = result

        return result

    def _perform_validation(
        self,
        dataset_id: str,
        source_data: Dict[str, Any],
        gate: ValidationGate,
    ) -> ValidationResult:
        """Internal method to perform actual validation."""
        result = ValidationResult(dataset_id=dataset_id, status=QualityStatus.UNKNOWN, quality_score=1.0)

        if not self.statguardian_enabled:
            logger.debug(f"StatGuardian disabled, marking {dataset_id} as valid")
            result.status = QualityStatus.VALID
            return result

        try:
            # Try to import StatGuardian
            try:
                import statguardian
            except ImportError:
                logger.warning("StatGuardian not installed, skipping validation")
                result.status = QualityStatus.UNKNOWN
                return result

            # Validate schema
            checks = self._validate_schema(source_data)
            for check in checks:
                result.add_check(check)

            # Validate data quality
            quality_checks = self._validate_data_quality(source_data)
            for check in quality_checks:
                result.add_check(check)

            # Calculate overall quality score
            if result.checks:
                avg_score = sum(c.score for c in result.checks) / len(result.checks)
                result.quality_score = avg_score
            else:
                result.quality_score = 1.0

            # Determine status
            if result.quality_score >= gate.min_quality_score:
                result.status = QualityStatus.VALID
            elif result.quality_score >= 0.7:
                result.status = QualityStatus.DEGRADED
            else:
                result.status = QualityStatus.INVALID
                result.add_error(f"Quality score {result.quality_score:.2f} below threshold {gate.min_quality_score}")

        except Exception as e:
            logger.error(f"Error validating {dataset_id}: {e}")
            result.status = QualityStatus.UNKNOWN
            result.add_error(str(e))

        return result

    def _validate_schema(self, source_data: Dict[str, Any]) -> List[QualityCheck]:
        """Validate schema consistency."""
        checks = []

        if "schema" not in source_data:
            checks.append(QualityCheck(
                check_name="schema_present",
                passed=False,
                score=0.0,
                message="No schema information provided"
            ))
            return checks

        schema = source_data["schema"]

        # Check schema has fields
        if not schema.get("fields"):
            checks.append(QualityCheck(
                check_name="schema_fields",
                passed=False,
                score=0.0,
                message="Schema has no fields"
            ))
        else:
            checks.append(QualityCheck(
                check_name="schema_fields",
                passed=True,
                score=1.0,
                message=f"Schema has {len(schema['fields'])} fields"
            ))

        return checks

    def _validate_data_quality(self, source_data: Dict[str, Any]) -> List[QualityCheck]:
        """Validate data quality (nulls, duplicates, etc)."""
        checks = []

        if "rows" not in source_data or not source_data["rows"]:
            checks.append(QualityCheck(
                check_name="data_rows",
                passed=False,
                score=0.0,
                message="No data rows provided"
            ))
            return checks

        rows = source_data["rows"]
        schema = source_data.get("schema", {})
        fields = schema.get("fields", [])

        # Check for null values
        if fields:
            null_counts = {field["name"]: 0 for field in fields}
            for row in rows:
                for field in fields:
                    if row.get(field["name"]) is None:
                        null_counts[field["name"]] += 1

            total_values = len(rows) * len(fields)
            total_nulls = sum(null_counts.values())
            null_ratio = total_nulls / total_values if total_values > 0 else 0

            checks.append(QualityCheck(
                check_name="null_ratio",
                passed=null_ratio < 0.1,
                score=1.0 - min(null_ratio, 1.0),
                message=f"Null ratio: {null_ratio:.2%}"
            ))

        # Check for duplicates (simplified)
        row_count = len(rows)
        unique_rows = len(set(tuple(row.values()) for row in rows))
        duplicate_ratio = 1.0 - (unique_rows / row_count) if row_count > 0 else 0

        checks.append(QualityCheck(
            check_name="duplicate_ratio",
            passed=duplicate_ratio < 0.05,
            score=1.0 - duplicate_ratio,
            message=f"Duplicate ratio: {duplicate_ratio:.2%}"
        ))

        return checks

    def should_include(
        self,
        dataset_id: str,
        result: Optional[ValidationResult] = None,
    ) -> bool:
        """
        Determine if source should be included in query context.

        Args:
            dataset_id: ID of the dataset
            result: Validation result (will validate if not provided)

        Returns:
            True if source should be included, False otherwise
        """
        gate = self._gates.get(dataset_id)
        if not gate or not gate.enabled:
            return True

        if result is None:
            result = self._validation_cache.get(dataset_id)
            if result is None:
                # Haven't validated yet, allow by default
                return True

        # Check if usable
        if not result.is_usable(gate.max_staleness_seconds):
            if gate.block_on_failure:
                logger.warning(f"Blocking source {dataset_id}: {result.status}")
                return False
            else:
                logger.warning(f"Using degraded source {dataset_id}: {result.status}")
                return True

        # Check quality score
        if result.quality_score < gate.min_quality_score:
            if gate.block_on_failure:
                logger.warning(f"Blocking source {dataset_id}: quality {result.quality_score:.2f} < {gate.min_quality_score}")
                return False

        return True

    def clear_cache(self, dataset_id: Optional[str] = None) -> None:
        """Clear validation cache."""
        if dataset_id:
            self._validation_cache.pop(dataset_id, None)
        else:
            self._validation_cache.clear()
        logger.debug(f"Cleared validation cache for {dataset_id or 'all'}")

    def get_stats(self) -> Dict[str, Any]:
        """Get validation statistics."""
        return {
            "gates_registered": len(self._gates),
            "cached_validations": len(self._validation_cache),
            "statguardian_enabled": self.statguardian_enabled,
            "cache_entries": {
                dataset_id: {
                    "status": result.status,
                    "quality_score": result.quality_score,
                    "age_seconds": (datetime.utcnow() - result.last_validated).total_seconds(),
                }
                for dataset_id, result in self._validation_cache.items()
            }
        }
