"""Quality Assurance Validator for PyStreamMCP.

Validates outputs, enforces SLAs, and ensures quality standards.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ValidationStatus(str, Enum):
    """Validation status."""
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass
class ValidationRule:
    """Quality validation rule."""

    name: str
    description: str
    metric: str  # cost_reduction, latency, accuracy, etc.
    operator: str  # >=, <=, >, <, ==
    threshold: float
    severity: str  # warning, error
    enabled: bool = True


@dataclass
class ValidationResult:
    """Result of validation."""

    rule_name: str
    status: ValidationStatus
    actual_value: float
    expected_value: float
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AuditEntry:
    """Audit log entry."""

    operation: str  # query, optimize, discover
    agent_id: str
    timestamp: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    cost_reduction: float
    duration_ms: float
    validation_status: ValidationStatus
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class QualityValidator:
    """Validator for output quality and cost-quality tradeoffs.

    Ensures that optimizations meet quality standards
    and SLA requirements.
    """

    def __init__(self):
        """Initialize validator."""
        self.rules: Dict[str, ValidationRule] = {}
        self.validation_history: List[ValidationResult] = []
        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """Setup default validation rules."""
        self.add_rule(ValidationRule(
            name="minimum_cost_reduction",
            description="Ensure minimum 60% cost reduction",
            metric="cost_reduction",
            operator=">=",
            threshold=60.0,
            severity="error",
        ))

        self.add_rule(ValidationRule(
            name="maximum_latency",
            description="Ensure latency under 500ms",
            metric="latency_ms",
            operator="<=",
            threshold=500.0,
            severity="warning",
        ))

        self.add_rule(ValidationRule(
            name="accuracy_threshold",
            description="Ensure model accuracy above 75%",
            metric="model_accuracy",
            operator=">=",
            threshold=75.0,
            severity="warning",
        ))

    def add_rule(self, rule: ValidationRule) -> None:
        """Add validation rule.

        Args:
            rule: Validation rule
        """
        self.rules[rule.name] = rule

    def validate(self, query_result: Dict[str, Any]) -> List[ValidationResult]:
        """Validate query result against all rules.

        Args:
            query_result: Query execution result

        Returns:
            List of validation results
        """
        results = []

        for rule in self.rules.values():
            if not rule.enabled:
                continue

            actual_value = query_result.get(rule.metric, 0.0)
            expected_value = rule.threshold

            status = self._check_rule(rule.operator, actual_value, expected_value)

            result = ValidationResult(
                rule_name=rule.name,
                status=status,
                actual_value=actual_value,
                expected_value=expected_value,
                message=f"{rule.name}: {rule.description}. Actual: {actual_value}, Expected: {expected_value}",
            )

            results.append(result)
            self.validation_history.append(result)

        return results

    def _check_rule(self, operator: str, actual: float, expected: float) -> ValidationStatus:
        """Check if actual value satisfies rule.

        Args:
            operator: Comparison operator
            actual: Actual value
            expected: Expected value

        Returns:
            Validation status
        """
        checks = {
            ">=": actual >= expected,
            "<=": actual <= expected,
            ">": actual > expected,
            "<": actual < expected,
            "==": actual == expected,
        }

        if checks.get(operator, False):
            return ValidationStatus.PASS
        else:
            return ValidationStatus.FAIL

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get validation summary.

        Returns:
            Summary statistics
        """
        if not self.validation_history:
            return {"total": 0, "passed": 0, "failed": 0, "pass_rate": 0.0}

        passed = sum(1 for r in self.validation_history if r.status == ValidationStatus.PASS)
        failed = sum(1 for r in self.validation_history if r.status == ValidationStatus.FAIL)
        total = len(self.validation_history)

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total > 0 else 0.0,
        }


class SLAChecker:
    """SLA (Service Level Agreement) checker."""

    def __init__(self):
        """Initialize SLA checker."""
        self.slas: Dict[str, Dict[str, Any]] = {
            "latency": {"threshold_ms": 100, "target_percent": 95},
            "cost_reduction": {"threshold_percent": 60, "target_percent": 90},
            "availability": {"target_percent": 99.9},
            "accuracy": {"threshold_percent": 80, "target_percent": 95},
        }

    def check_sla(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Check if metrics meet SLA.

        Args:
            metrics: Operation metrics

        Returns:
            SLA compliance report
        """
        report = {"compliant": True, "violations": []}

        # Check latency SLA
        latency = metrics.get("latency_ms", 0)
        if latency > self.slas["latency"]["threshold_ms"]:
            report["violations"].append(f"Latency SLA: {latency}ms > {self.slas['latency']['threshold_ms']}ms")
            report["compliant"] = False

        # Check cost reduction SLA
        reduction = metrics.get("cost_reduction_percent", 0)
        if reduction < self.slas["cost_reduction"]["threshold_percent"]:
            report["violations"].append(
                f"Cost reduction SLA: {reduction}% < {self.slas['cost_reduction']['threshold_percent']}%"
            )
            report["compliant"] = False

        # Check accuracy SLA
        accuracy = metrics.get("model_accuracy", 0)
        if accuracy < self.slas["accuracy"]["threshold_percent"]:
            report["violations"].append(
                f"Accuracy SLA: {accuracy}% < {self.slas['accuracy']['threshold_percent']}%"
            )
            report["compliant"] = False

        return report


class AuditLogger:
    """Audit logger for compliance and traceability."""

    def __init__(self, enable_encryption: bool = False):
        """Initialize audit logger.

        Args:
            enable_encryption: Enable audit log encryption
        """
        self.enable_encryption = enable_encryption
        self.audit_log: List[AuditEntry] = []

    def log_operation(
        self,
        operation: str,
        agent_id: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        cost_reduction: float,
        duration_ms: float,
        validation_status: ValidationStatus,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> str:
        """Log an operation.

        Args:
            operation: Operation type
            agent_id: Agent ID
            input_data: Input data
            output_data: Output data
            cost_reduction: Cost reduction percentage
            duration_ms: Duration in milliseconds
            validation_status: Validation result
            user_id: User ID
            session_id: Session ID

        Returns:
            Entry ID
        """
        entry = AuditEntry(
            operation=operation,
            agent_id=agent_id,
            timestamp=datetime.now().isoformat(),
            input_data=input_data,
            output_data=output_data,
            cost_reduction=cost_reduction,
            duration_ms=duration_ms,
            validation_status=validation_status,
            user_id=user_id,
            session_id=session_id,
        )

        self.audit_log.append(entry)
        return entry.timestamp

    def get_audit_trail(
        self,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> List[AuditEntry]:
        """Get audit trail with filters.

        Args:
            agent_id: Filter by agent ID
            session_id: Filter by session
            start_time: Start time (ISO format)
            end_time: End time (ISO format)

        Returns:
            Filtered audit entries
        """
        filtered = self.audit_log

        if agent_id:
            filtered = [e for e in filtered if e.agent_id == agent_id]

        if session_id:
            filtered = [e for e in filtered if e.session_id == session_id]

        if start_time:
            filtered = [e for e in filtered if e.timestamp >= start_time]

        if end_time:
            filtered = [e for e in filtered if e.timestamp <= end_time]

        return filtered

    def get_compliance_report(self) -> Dict[str, Any]:
        """Get compliance report.

        Returns:
            Compliance metrics
        """
        if not self.audit_log:
            return {"total_operations": 0, "compliance_rate": 0.0}

        total = len(self.audit_log)
        compliant = sum(1 for e in self.audit_log if e.validation_status == ValidationStatus.PASS)

        return {
            "total_operations": total,
            "compliant_operations": compliant,
            "compliance_rate": (compliant / total * 100) if total > 0 else 0.0,
            "avg_cost_reduction": sum(e.cost_reduction for e in self.audit_log) / total if total > 0 else 0.0,
            "avg_duration_ms": sum(e.duration_ms for e in self.audit_log) / total if total > 0 else 0.0,
        }
