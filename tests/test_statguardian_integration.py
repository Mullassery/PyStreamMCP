"""Tests for PyStreamMCP ↔ StatGuardian integration."""

import pytest
from datetime import datetime, timedelta
from pystreammcp.quality import (
    QualityValidator,
    ValidationGate,
    ValidationResult,
    QualityStatus,
    QualityCheck,
)


class TestQualityValidator:
    """Test quality validation functionality."""

    def test_validator_creation(self):
        """Test creating a quality validator."""
        validator = QualityValidator(statguardian_enabled=False)
        assert validator.statguardian_enabled is False
        assert len(validator._gates) == 0

    def test_register_gate(self):
        """Test registering validation gates."""
        validator = QualityValidator()
        gate = ValidationGate(
            dataset_id="orders",
            min_quality_score=0.8,
            block_on_failure=True
        )
        validator.register_gate(gate)
        assert "orders" in validator._gates

    def test_validation_gate_configuration(self):
        """Test validation gate configuration."""
        gate = ValidationGate(
            dataset_id="customers",
            enabled=True,
            block_on_failure=False,
            min_quality_score=0.7,
            max_staleness_seconds=7200
        )
        assert gate.dataset_id == "customers"
        assert gate.block_on_failure is False
        assert gate.min_quality_score == 0.7
        assert gate.max_staleness_seconds == 7200

    def test_validation_result_valid(self):
        """Test valid validation result."""
        result = ValidationResult(
            dataset_id="dataset_1",
            status=QualityStatus.VALID,
            quality_score=0.95
        )
        assert result.is_valid()
        assert result.is_usable()

    def test_validation_result_invalid(self):
        """Test invalid validation result."""
        result = ValidationResult(
            dataset_id="dataset_2",
            status=QualityStatus.INVALID,
            quality_score=0.4
        )
        assert not result.is_valid()
        assert not result.is_usable()

    def test_validation_result_stale_usable(self):
        """Test stale result that's still usable."""
        past_time = datetime.utcnow() - timedelta(minutes=30)
        result = ValidationResult(
            dataset_id="dataset_3",
            status=QualityStatus.STALE,
            quality_score=0.85,
            last_validated=past_time
        )
        # Should be usable within 1 hour
        assert result.is_usable(max_staleness_seconds=3600)
        # Should not be usable within 10 minutes
        assert not result.is_usable(max_staleness_seconds=600)

    def test_validation_result_degraded(self):
        """Test degraded result."""
        result = ValidationResult(
            dataset_id="dataset_4",
            status=QualityStatus.DEGRADED,
            quality_score=0.75
        )
        # Degraded but usable
        assert result.is_usable()
        assert not result.is_valid()

    def test_add_quality_check(self):
        """Test adding quality checks to result."""
        result = ValidationResult(
            dataset_id="dataset_5",
            status=QualityStatus.VALID,
            quality_score=1.0
        )
        check = QualityCheck(
            check_name="schema_check",
            passed=True,
            score=0.95,
            message="Schema validation passed"
        )
        result.add_check(check)
        assert len(result.checks) == 1
        assert result.checks[0].check_name == "schema_check"

    def test_add_error(self):
        """Test adding error messages."""
        result = ValidationResult(
            dataset_id="dataset_6",
            status=QualityStatus.INVALID,
            quality_score=0.5
        )
        result.add_error("Null ratio too high")
        result.add_error("Missing required field")
        assert len(result.errors) == 2

    def test_validate_with_gate_not_registered(self):
        """Test validation when no gate is registered."""
        validator = QualityValidator(statguardian_enabled=False)
        source_data = {
            "schema": {"fields": [{"name": "id"}, {"name": "name"}]},
            "rows": [{"id": 1, "name": "Alice"}]
        }
        result = validator.validate("unknown_dataset", source_data)
        assert result.status == QualityStatus.UNKNOWN

    def test_validate_with_statguardian_disabled(self):
        """Test validation with StatGuardian disabled."""
        validator = QualityValidator(statguardian_enabled=False)
        gate = ValidationGate(dataset_id="dataset_7", enabled=True)
        validator.register_gate(gate)

        source_data = {
            "schema": {"fields": [{"name": "id"}]},
            "rows": [{"id": 1}]
        }
        result = validator.validate("dataset_7", source_data)
        assert result.status == QualityStatus.VALID

    def test_validate_schema_validation(self):
        """Test schema validation checks."""
        validator = QualityValidator(statguardian_enabled=False)
        gate = ValidationGate(dataset_id="dataset_8", enabled=True)
        validator.register_gate(gate)

        # No schema
        source_data = {"rows": [{"id": 1}]}
        result = validator.validate("dataset_8", source_data)
        # Should still return VALID when StatGuardian disabled
        assert result.status == QualityStatus.VALID

    def test_validate_data_quality(self):
        """Test data quality validation."""
        validator = QualityValidator(statguardian_enabled=False)
        gate = ValidationGate(dataset_id="dataset_9", enabled=True)
        validator.register_gate(gate)

        source_data = {
            "schema": {
                "fields": [
                    {"name": "id", "type": "integer"},
                    {"name": "name", "type": "string"},
                    {"name": "email", "type": "string"}
                ]
            },
            "rows": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"},
                {"id": 3, "name": "Charlie", "email": None},
            ]
        }
        result = validator.validate("dataset_9", source_data)
        assert result.status == QualityStatus.VALID or result.status == QualityStatus.DEGRADED

    def test_should_include_valid(self):
        """Test inclusion check for valid source."""
        validator = QualityValidator()
        gate = ValidationGate(dataset_id="dataset_10", block_on_failure=True)
        validator.register_gate(gate)

        result = ValidationResult(
            dataset_id="dataset_10",
            status=QualityStatus.VALID,
            quality_score=0.95
        )
        assert validator.should_include("dataset_10", result)

    def test_should_include_invalid_blocking(self):
        """Test inclusion check for invalid source with blocking."""
        validator = QualityValidator()
        gate = ValidationGate(dataset_id="dataset_11", block_on_failure=True)
        validator.register_gate(gate)

        result = ValidationResult(
            dataset_id="dataset_11",
            status=QualityStatus.INVALID,
            quality_score=0.3
        )
        assert not validator.should_include("dataset_11", result)

    def test_should_include_invalid_nonblocking(self):
        """Test inclusion check for invalid source without blocking."""
        validator = QualityValidator()
        gate = ValidationGate(dataset_id="dataset_12", block_on_failure=False)
        validator.register_gate(gate)

        result = ValidationResult(
            dataset_id="dataset_12",
            status=QualityStatus.INVALID,
            quality_score=0.3
        )
        # Should include despite invalid status (not blocking)
        assert validator.should_include("dataset_12", result)

    def test_cache_validation_result(self):
        """Test that validation results are cached."""
        validator = QualityValidator(statguardian_enabled=False)
        gate = ValidationGate(dataset_id="dataset_13", enabled=True)
        validator.register_gate(gate)

        source_data = {
            "schema": {"fields": [{"name": "id"}]},
            "rows": [{"id": 1}]
        }

        # First validation
        result1 = validator.validate("dataset_13", source_data)
        # Second validation (should use cache)
        result2 = validator.validate("dataset_13", source_data)

        assert result1.validation_id == result2.validation_id

    def test_clear_cache(self):
        """Test clearing validation cache."""
        validator = QualityValidator(statguardian_enabled=False)
        gate = ValidationGate(dataset_id="dataset_14", enabled=True)
        validator.register_gate(gate)

        source_data = {
            "schema": {"fields": [{"name": "id"}]},
            "rows": [{"id": 1}]
        }
        validator.validate("dataset_14", source_data)
        assert len(validator._validation_cache) == 1

        validator.clear_cache("dataset_14")
        assert len(validator._validation_cache) == 0

    def test_clear_all_cache(self):
        """Test clearing all cached validations."""
        validator = QualityValidator(statguardian_enabled=False)
        for i in range(3):
            gate = ValidationGate(dataset_id=f"dataset_{i}", enabled=True)
            validator.register_gate(gate)

        source_data = {
            "schema": {"fields": [{"name": "id"}]},
            "rows": [{"id": 1}]
        }
        for i in range(3):
            validator.validate(f"dataset_{i}", source_data)

        assert len(validator._validation_cache) == 3
        validator.clear_cache()
        assert len(validator._validation_cache) == 0

    def test_get_stats(self):
        """Test getting validator statistics."""
        validator = QualityValidator(statguardian_enabled=False)
        gate1 = ValidationGate(dataset_id="dataset_15")
        gate2 = ValidationGate(dataset_id="dataset_16")
        validator.register_gate(gate1)
        validator.register_gate(gate2)

        source_data = {
            "schema": {"fields": [{"name": "id"}]},
            "rows": [{"id": 1}]
        }
        validator.validate("dataset_15", source_data)

        stats = validator.get_stats()
        assert stats["gates_registered"] == 2
        assert stats["cached_validations"] == 1
        assert stats["statguardian_enabled"] is False

    def test_quality_check_bounds(self):
        """Test that quality scores are bounded 0-1."""
        # Test upper bound
        check1 = QualityCheck("test", True, 1.5)
        assert check1.score == 1.0

        # Test lower bound
        check2 = QualityCheck("test", False, -0.5)
        assert check2.score == 0.0

    def test_validation_result_bounds(self):
        """Test that validation quality scores are bounded 0-1."""
        result1 = ValidationResult("d1", QualityStatus.VALID, 1.5)
        assert result1.quality_score == 1.0

        result2 = ValidationResult("d2", QualityStatus.VALID, -0.5)
        assert result2.quality_score == 0.0


class TestIntegrationWithDiscovery:
    """Test integration with PyStreamMCP discovery."""

    def test_quality_gating_in_discovery(self):
        """Test using quality validator with discovered sources."""
        from pystreammcp.discovery import Discovery, DiscoveredSource, SourceType

        validator = QualityValidator(statguardian_enabled=False)
        gate = ValidationGate(dataset_id="source_1", block_on_failure=True)
        validator.register_gate(gate)

        # Create discovered source
        source = DiscoveredSource(
            name="orders_table",
            source_type=SourceType.TABLE,
            relevance_score=0.9,
            estimated_tokens=500,
            source_id="source_1"
        )

        # Validate before including
        source_data = {
            "schema": {"fields": [{"name": "id"}, {"name": "amount"}]},
            "rows": [{"id": 1, "amount": 100.0}]
        }
        result = validator.validate(source.source_id, source_data)
        should_include = validator.should_include(source.source_id, result)

        assert should_include
        assert result.status in [QualityStatus.VALID, QualityStatus.UNKNOWN]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
