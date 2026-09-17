"""
AIRPORT OPERATIONS AI COPILOT
DAY 4 - SAFE OPERATIONAL TOOLS

Tools:
1. get_airport_metrics
2. calculate_driver_incentive
3. trigger_surge_override

Day 4 additions:
- Input validation
- Risk classification
- Policy validation
- Human approval
- Output validation
"""

from typing import Any, Dict

from .guardrails import (
    VALID_AIRPORTS,
    validate_airport_code,
    validate_driver_count,
    validate_severity,
    validate_reason,
    validate_surge_multiplier,
    classify_incentive_risk,
    validate_tool_output,
    guard_surge_action,
)


# ============================================================
# MOCK AIRPORT DATA
# ============================================================

AIRPORT_METRICS = {
    "SFO": {
        "completion_rate": 0.943,
        "average_eta_minutes": 8.8,
        "active_drivers": 145,
        "driver_cancellation_rate": 0.060,
        "queue_size": 45,
        "surge_multiplier": 1.1,
        "request_volume": 146,
        "timestamp": "2026-09-01 22:00",
    },
    "LAX": {
        "completion_rate": 0.947,
        "average_eta_minutes": 8.5,
        "active_drivers": 149,
        "driver_cancellation_rate": 0.055,
        "queue_size": 44,
        "surge_multiplier": 1.0,
        "request_volume": 142,
        "timestamp": "2026-09-01 22:00",
    },
    "JFK": {
        "completion_rate": 0.935,
        "average_eta_minutes": 9.9,
        "active_drivers": 133,
        "driver_cancellation_rate": 0.067,
        "queue_size": 42,
        "surge_multiplier": 1.1,
        "request_volume": 140,
        "timestamp": "2026-09-01 22:00",
    },
}


# ============================================================
# TOOL 1 — GET AIRPORT METRICS
# ============================================================

def get_airport_metrics(
    airport_code: str,
) -> Dict[str, Any]:
    """
    Read airport operational metrics.

    Risk level:
        LOW

    Approval:
        NOT REQUIRED
    """

    validation = validate_airport_code(
        airport_code
    )

    if not validation["valid"]:
        return {
            "success": False,
            "tool": "get_airport_metrics",
            "error": validation["error"],
        }

    airport = validation["airport_code"]

    result = {
        "success": True,
        "tool": "get_airport_metrics",
        "airport_code": airport,
        "metrics": AIRPORT_METRICS[airport],
    }

    output_check = validate_tool_output(
        "get_airport_metrics",
        result,
    )

    if not output_check["valid"]:
        return {
            "success": False,
            "tool": "get_airport_metrics",
            "error": output_check["error"],
        }

    return result


# ============================================================
# TOOL 2 — CALCULATE DRIVER INCENTIVE
# ============================================================

INCENTIVE_PER_DRIVER = {
    "LOW": 5.0,
    "MEDIUM": 10.0,
    "HIGH": 20.0,
}


def calculate_driver_incentive(
    driver_count: Any,
    severity_level: Any,
) -> Dict[str, Any]:
    """
    Calculate recommended driver incentive.

    Calculation is allowed without approval.

    Actual execution/payment is not performed here.
    """

    driver_validation = validate_driver_count(
        driver_count
    )

    if not driver_validation["valid"]:
        return {
            "success": False,
            "tool": "calculate_driver_incentive",
            "error": driver_validation["error"],
        }

    severity_validation = validate_severity(
        severity_level
    )

    if not severity_validation["valid"]:
        return {
            "success": False,
            "tool": "calculate_driver_incentive",
            "error": severity_validation["error"],
        }

    count = driver_validation["driver_count"]
    severity = severity_validation["severity_level"]

    incentive_per_driver = INCENTIVE_PER_DRIVER[
        severity
    ]

    estimated_total_cost = (
        count * incentive_per_driver
    )

    risk = classify_incentive_risk(
        estimated_total_cost
    )

    result = {
        "success": True,
        "tool": "calculate_driver_incentive",
        "driver_count": count,
        "severity_level": severity,
        "recommended_incentive_per_driver": (
            incentive_per_driver
        ),
        "estimated_total_cost": (
            estimated_total_cost
        ),
        "risk_level": risk["risk_level"],
        "approval_required": (
            risk["approval_required"]
        ),
    }

    output_check = validate_tool_output(
        "calculate_driver_incentive",
        result,
    )

    if not output_check["valid"]:
        return {
            "success": False,
            "tool": "calculate_driver_incentive",
            "error": output_check["error"],
        }

    return result


# ============================================================
# TOOL 3 — SAFE SURGE OVERRIDE
# ============================================================

def trigger_surge_override(
    airport_code: Any,
    new_multiplier: Any,
    reason: Any,
) -> Dict[str, Any]:
    """
    Day 4 SAFE surge override.

    IMPORTANT:

    The surge action will NOT execute unless:

    1. Airport is valid
    2. Multiplier is valid
    3. Reason is present
    4. Requested surge is within policy
    5. Risk classification passes
    6. Human explicitly approves

    The AI cannot bypass the approval layer.
    """

    print()
    print("[DAY 4 GUARDRAIL]")
    print("Validating surge override request...")

    # --------------------------------------------------------
    # 1. Airport validation
    # --------------------------------------------------------

    airport_validation = validate_airport_code(
        airport_code
    )

    if not airport_validation["valid"]:
        result = {
            "success": False,
            "tool": "trigger_surge_override",
            "status": "BLOCKED",
            "risk_level": "BLOCKED",
            "error": airport_validation["error"],
        }

        print(
            "[GUARDRAIL] BLOCKED:",
            airport_validation["error"],
        )

        return result

    airport = airport_validation[
        "airport_code"
    ]

    # --------------------------------------------------------
    # 2. Surge validation
    # --------------------------------------------------------

    surge_validation = validate_surge_multiplier(
        new_multiplier
    )

    if not surge_validation["valid"]:
        result = {
            "success": False,
            "tool": "trigger_surge_override",
            "status": "BLOCKED",
            "risk_level": "BLOCKED",
            "error": surge_validation["error"],
        }

        print(
            "[GUARDRAIL] BLOCKED:",
            surge_validation["error"],
        )

        return result

    multiplier = surge_validation[
        "new_multiplier"
    ]

    # --------------------------------------------------------
    # 3. Reason validation
    # --------------------------------------------------------

    reason_validation = validate_reason(
        reason
    )

    if not reason_validation["valid"]:
        result = {
            "success": False,
            "tool": "trigger_surge_override",
            "status": "BLOCKED",
            "risk_level": "BLOCKED",
            "error": reason_validation["error"],
        }

        print(
            "[GUARDRAIL] BLOCKED:",
            reason_validation["error"],
        )

        return result

    clean_reason = reason_validation["reason"]

    # --------------------------------------------------------
    # 4. Complete guardrail pipeline
    # --------------------------------------------------------

    guardrail_result = guard_surge_action(
        airport_code=airport,
        new_multiplier=multiplier,
        reason=clean_reason,
        policy_max_surge=1.5,
    )

    # --------------------------------------------------------
    # 5. BLOCKED / REJECTED
    # --------------------------------------------------------

    if not guardrail_result["allowed"]:

        print(
            "[GUARDRAIL]",
            guardrail_result["status"],
        )

        return {
            "success": False,
            "tool": "trigger_surge_override",
            "status": guardrail_result["status"],
            "risk_level": guardrail_result[
                "risk_level"
            ],
            "airport_code": airport,
            "new_multiplier": multiplier,
            "reason": clean_reason,
            "policy_result": guardrail_result.get(
                "policy_result"
            ),
            "approval_required": guardrail_result.get(
                "approval_required",
                False,
            ),
            "approval_decision": guardrail_result.get(
                "approval_decision"
            ),
            "error": guardrail_result["reason"],
        }

    # --------------------------------------------------------
    # 6. APPROVED
    # --------------------------------------------------------

    print(
        "[GUARDRAIL] APPROVED - executing mock action..."
    )

    result = {
        "success": True,
        "tool": "trigger_surge_override",
        "execution": "MOCK",
        "airport_code": airport,
        "new_multiplier": multiplier,
        "reason": clean_reason,
        "risk_level": guardrail_result[
            "risk_level"
        ],
        "policy_result": guardrail_result[
            "policy_result"
        ],
        "approval_required": guardrail_result[
            "approval_required"
        ],
        "approval_decision": guardrail_result[
            "approval_decision"
        ],
        "status": "SURGE_OVERRIDE_TRIGGERED",
        "message": (
            "Mock surge override executed successfully "
            "after Day 4 guardrail validation and "
            "human approval."
        ),
    }

    output_check = validate_tool_output(
        "trigger_surge_override",
        result,
    )

    if not output_check["valid"]:
        return {
            "success": False,
            "tool": "trigger_surge_override",
            "status": "BLOCKED",
            "error": output_check["error"],
        }

    return result


# ============================================================
# TOOL TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("DAY 4 SAFE TOOLS TEST")
    print("=" * 70)

    print("\nTEST 1 - Airport metrics")
    print(
        get_airport_metrics("SFO")
    )

    print("\nTEST 2 - Invalid airport")
    print(
        get_airport_metrics("UNKNOWN")
    )

    print("\nTEST 3 - Driver incentive")
    print(
        calculate_driver_incentive(
            40,
            "HIGH",
        )
    )

    print("\nTEST 4 - Invalid driver count")
    print(
        calculate_driver_incentive(
            -50,
            "HIGH",
        )
    )

    print("\nTEST 5 - Invalid surge")
    print(
        trigger_surge_override(
            "SFO",
            100,
            "high demand",
        )
    )

    print("\nTEST 6 - Policy violation")
    print(
        trigger_surge_override(
            "SFO",
            1.6,
            "high demand",
        )
    )

    print("\nTEST 7 - Valid HIGH risk action")
    print(
        trigger_surge_override(
            "SFO",
            1.5,
            "completion rate below threshold",
        )
    )
