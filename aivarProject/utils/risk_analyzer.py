"""
risk_analyzer.py
Risk analysis and mitigation recommendation engine.
"""

from typing import Any, Dict, List


def analyze_integration_risks(
    source_system: str,
    target_system: str,
    data_sensitivity: str = "Medium",
    integration_type: str = "REST API",
) -> Dict[str, Any]:
    """
    Analyze integration risks and generate mitigation strategies.

    Args:
        source_system: Name of source system.
        target_system: Name of target system.
        data_sensitivity: Level of data sensitivity (Low, Medium, High).
        integration_type: Type of integration (REST API, etc.).

    Returns:
        Dictionary with risk assessment and mitigations.
    """
    risks = {
        "security_risk": _assess_security_risk(integration_type, data_sensitivity),
        "data_loss_risk": _assess_data_loss_risk(source_system, target_system),
        "failure_impact": _assess_failure_impact(source_system, target_system),
        "performance_risk": _assess_performance_risk(integration_type),
        "compliance_risk": _assess_compliance_risk(data_sensitivity),
    }

    mitigations = {
        "security_mitigation": _get_security_mitigations(integration_type, data_sensitivity),
        "data_loss_mitigation": _get_data_loss_mitigations(),
        "failure_mitigation": _get_failure_mitigations(integration_type),
        "performance_mitigation": _get_performance_mitigations(),
        "compliance_mitigation": _get_compliance_mitigations(data_sensitivity),
    }

    return {
        "risks": risks,
        "mitigations": mitigations,
        "overall_risk_level": _calculate_overall_risk_level(risks),
    }


def _assess_security_risk(integration_type: str, data_sensitivity: str) -> str:
    """Assess security risk based on integration type and data sensitivity."""
    if data_sensitivity == "High" and integration_type == "REST API":
        return "High"
    if data_sensitivity == "High":
        return "Medium"
    if data_sensitivity == "Medium":
        return "Medium"
    return "Low"


def _assess_data_loss_risk(source_system: str, target_system: str) -> str:
    """Assess data loss risk."""
    erp_systems = {"SAP", "Oracle", "NetSuite"}
    crm_systems = {"Salesforce", "HubSpot"}

    if source_system in erp_systems or target_system in erp_systems:
        return "High"
    if source_system in crm_systems or target_system in crm_systems:
        return "Medium"
    return "Low"


def _assess_failure_impact(source_system: str, target_system: str) -> str:
    """Assess the impact of integration failure."""
    critical_systems = {"Salesforce", "SAP", "Oracle", "NetSuite", "QuickBooks"}

    if source_system in critical_systems or target_system in critical_systems:
        return "High"
    return "Medium"


def _assess_performance_risk(integration_type: str) -> str:
    """Assess performance risk based on integration type."""
    if integration_type in ("File Transfer", "Database Sync"):
        return "Medium"
    return "Low"


def _assess_compliance_risk(data_sensitivity: str) -> str:
    """Assess compliance risk based on data sensitivity."""
    if data_sensitivity == "High":
        return "High"
    if data_sensitivity == "Medium":
        return "Medium"
    return "Low"


def _get_security_mitigations(integration_type: str, data_sensitivity: str) -> List[str]:
    """Get security mitigation strategies."""
    mitigations = [
        "Use OAuth2 authentication with token rotation",
        "Enable SSL/TLS encryption for all data in transit",
        "Implement API rate limiting and throttling",
    ]

    if data_sensitivity == "High":
        mitigations.extend([
            "Use VPN or private network connections",
            "Implement end-to-end encryption",
            "Enable audit logging for all data access",
            "Use service accounts with minimal required permissions",
        ])

    return mitigations


def _get_data_loss_mitigations() -> List[str]:
    """Get data loss mitigation strategies."""
    return [
        "Implement transaction logging for all data transfers",
        "Enable backup and rollback mechanisms",
        "Use idempotent operations where possible",
        "Implement data validation before target system write",
        "Set up monitoring and alerting for data mismatches",
    ]


def _get_failure_mitigations(integration_type: str) -> List[str]:
    """Get failure mitigation strategies."""
    mitigations = [
        "Implement retry logic with exponential backoff",
        "Set up monitoring and alerting for integration failures",
        "Create runbooks for manual intervention",
        "Test failover scenarios regularly",
    ]

    if integration_type == "REST API":
        mitigations.append("Implement circuit breaker pattern for API resilience")

    return mitigations


def _get_performance_mitigations() -> List[str]:
    """Get performance mitigation strategies."""
    return [
        "Implement caching where appropriate",
        "Batch API requests to reduce overhead",
        "Monitor integration latency and throughput",
        "Optimize transformation logic for performance",
        "Use connection pooling for database integrations",
    ]


def _get_compliance_mitigations(data_sensitivity: str) -> List[str]:
    """Get compliance mitigation strategies."""
    mitigations = [
        "Document all data processing steps",
        "Maintain audit trails for data access",
    ]

    if data_sensitivity == "High":
        mitigations.extend([
            "Implement data retention policies",
            "Ensure GDPR/CCPA compliance for personal data",
            "Conduct regular security audits",
            "Implement data masking for sensitive fields in logs",
        ])

    return mitigations


def _calculate_overall_risk_level(risks: Dict[str, str]) -> str:
    """Calculate overall risk level from individual risk assessments."""
    risk_values = {"High": 3, "Medium": 2, "Low": 1}
    scores = [risk_values.get(risk, 1) for risk in risks.values()]
    avg_score = sum(scores) / len(scores) if scores else 1

    if avg_score >= 2.5:
        return "High"
    if avg_score >= 1.5:
        return "Medium"
    return "Low"
