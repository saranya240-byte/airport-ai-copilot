"""
DAY 4 - AI SAFETY, GUARDRAILS & HUMAN-IN-THE-LOOP

Responsibilities:
- Input validation
- Output validation
- Risk classification
- Policy validation
- Human approval
- Permission enforcement

Project assumptions:
- Valid airports: SFO, LAX, JFK
- Maximum surge: 1.5x
- Surge >= 1.3x: HIGH risk and approval required
- Surge < 1.3x: MEDIUM risk and approval required
- Driver incentive above $500: HIGH risk and approval required
- Driver incentive <= $500: MEDIUM risk
"""

from typing import Any, Dict, Optional


# ============================================================
# PROJECT ASSUMPTIONS
# ============================================================

VALID_AIRPORTS = {"SFO", "LAX", "JFK"}

MAX_SURGE_MULTIPLIER = 1.5
MIN_SURGE_MULTIPLIER = 1.0

HIGH_RISK_SURGE_THRESHOLD = 1.3

INCENTIVE_HIGH_RISK_THRESHOLD = 500.0

VALID_SEVERITY_LEVELS = {
    "LOW",
    "MEDIUM",
    "HIGH",
}


# ============================================================
# INPUT GUARDRAILS
# ============================================================

def validate_airport_code(airport_code: Any) -> Dict[str, Any]:
    """Validate airport code."""

    if airport_code is None:
        return {
            "valid": False,
            "error": "airport_code is required.",
        }

    code = str(airport_code).strip().upper()

    if not code:
        return {
            "valid": False,
            "error": "airport_code is required.",
        }

    if code not in VALID_AIRPORTS:
        return {
            "valid": False,
            "error": (
                f"Invalid airport code '{code}'. "
                "Valid airports are SFO, LAX, and JFK."
            ),
        }

    return {
        "valid": True,
        "airport_code": code,
    }


def validate_surge_multiplier(
    new_multiplier: Any,
) -> Dict[str, Any]:
    """Validate surge multiplier."""

    if new_multiplier is None:
        return {
            "valid": False,
            "error": "new_multiplier is required.",
        }

    try:
        multiplier = float(new_multiplier)
    except (TypeError, ValueError):
        return {
            "valid": False,
            "error": "new_multiplier must be a number.",
        }

    if multiplier < MIN_SURGE_MULTIPLIER:
        return {
            "valid": False,
            "error": (
                f"new_multiplier must be at least "
                f"{MIN_SURGE_MULTIPLIER}x."
            ),
        }

    if multiplier > MAX_SURGE_MULTIPLIER:
        return {
            "valid": False,
            "error": (
                f"new_multiplier {multiplier}x exceeds the "
                f"maximum permitted surge of "
                f"{MAX_SURGE_MULTIPLIER}x."
            ),
        }

    return {
        "valid": True,
        "new_multiplier": multiplier,
    }


def validate_driver_count(
    driver_count: Any,
) -> Dict[str, Any]:
    """Validate driver count."""

    if driver_count is None:
        return {
            "valid": False,
            "error": "driver_count is required.",
        }

    try:
        count = int(driver_count)
    except (TypeError, ValueError):
        return {
            "valid": False,
            "error": "driver_count must be an integer.",
        }

    if count <= 0:
        return {
            "valid": False,
            "error": "driver_count must be greater than zero.",
        }

    return {
        "valid": True,
        "driver_count": count,
    }


def validate_incentive_amount(
    incentive_amount: Any,
) -> Dict[str, Any]:
    """Validate incentive amount."""

    if incentive_amount is None:
        return {
            "valid": False,
            "error": "incentive_amount is required.",
        }

    try:
        amount = float(incentive_amount)
    except (TypeError, ValueError):
        return {
            "valid": False,
            "error": "incentive_amount must be a number.",
        }

    if amount < 0:
        return {
            "valid": False,
            "error": "incentive_amount cannot be negative.",
        }

    return {
        "valid": True,
        "incentive_amount": amount,
    }


def validate_severity(
    severity_level: Any,
) -> Dict[str, Any]:
    """Validate severity level."""

    if severity_level is None:
        return {
            "valid": False,
            "error": "severity_level is required.",
        }

    severity = str(severity_level).strip().upper()

    if severity not in VALID_SEVERITY_LEVELS:
        return {
            "valid": False,
            "error": (
                f"Invalid severity '{severity}'. "
                "Valid values are LOW, MEDIUM, and HIGH."
            ),
        }

    return {
        "valid": True,
        "severity_level": severity,
    }


def validate_reason(reason: Any) -> Dict[str, Any]:
    """Validate action reason."""

    if reason is None:
        return {
            "valid": False,
            "error": "reason is required.",
        }

    cleaned = str(reason).strip()

    if not cleaned:
        return {
            "valid": False,
            "error": "reason is required.",
        }

    return {
        "valid": True,
        "reason": cleaned,
    }


# ============================================================
# RISK CLASSIFICATION
# ============================================================

def classify_surge_risk(
    new_multiplier: float,
) -> Dict[str, Any]:
    """
    Classify surge action according to Day 4 assumptions.

    < 1.3x  -> MEDIUM
    >= 1.3x -> HIGH
    """

    multiplier = float(new_multiplier)

    if multiplier >= HIGH_RISK_SURGE_THRESHOLD:
        return {
            "risk_level": "HIGH",
            "approval_required": True,
            "action": "increase_surge",
            "reason": (
                f"Surge {multiplier}x is at or above "
                f"the {HIGH_RISK_SURGE_THRESHOLD}x "
                "high-risk threshold."
            ),
        }

    return {
        "risk_level": "MEDIUM",
        "approval_required": True,
        "action": "increase_surge",
        "reason": (
            f"Surge {multiplier}x is below the "
            f"{HIGH_RISK_SURGE_THRESHOLD}x high-risk "
            "threshold but still requires approval."
        ),
    }


def classify_incentive_risk(
    estimated_total_cost: float,
) -> Dict[str, Any]:
    """
    Classify driver incentive action.

    <= $500 -> MEDIUM
    > $500  -> HIGH
    """

    amount = float(estimated_total_cost)

    if amount > INCENTIVE_HIGH_RISK_THRESHOLD:
        return {
            "risk_level": "HIGH",
            "approval_required": True,
            "action": "calculate_driver_incentive",
            "reason": (
                f"Estimated incentive cost ${amount:.2f} "
                f"exceeds the ${INCENTIVE_HIGH_RISK_THRESHOLD:.2f} "
                "high-risk threshold."
            ),
        }

    return {
        "risk_level": "MEDIUM",
        "approval_required": False,
        "action": "calculate_driver_incentive",
        "reason": (
            f"Estimated incentive cost ${amount:.2f} "
            "is within the conditional approval threshold."
        ),
    }


def classify_action(
    action: str,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Central risk classifier.
    """

    normalized_action = (
        str(action).strip().lower()
    )

    if normalized_action in {
        "get_airport_metrics",
        "read_airport_metrics",
        "search_policy",
    }:
        return {
            "risk_level": "LOW",
            "approval_required": False,
            "action": normalized_action,
            "reason": "Read/search operation does not modify operations.",
        }

    if normalized_action in {
        "trigger_surge_override",
        "increase_surge",
    }:
        multiplier = kwargs.get("new_multiplier")

        validation = validate_surge_multiplier(
            multiplier
        )

        if not validation["valid"]:
            return {
                "risk_level": "BLOCKED",
                "approval_required": False,
                "action": normalized_action,
                "reason": validation["error"],
            }

        return classify_surge_risk(
            validation["new_multiplier"]
        )

    if normalized_action in {
        "calculate_driver_incentive",
        "driver_incentive",
    }:
        estimated_cost = kwargs.get(
            "estimated_total_cost"
        )

        if estimated_cost is None:
            return {
                "risk_level": "MEDIUM",
                "approval_required": False,
                "action": normalized_action,
                "reason": (
                    "Incentive calculation is a "
                    "medium-risk operation until "
                    "the final cost is known."
                ),
            }

        return classify_incentive_risk(
            estimated_cost
        )

    return {
        "risk_level": "BLOCKED",
        "approval_required": False,
        "action": normalized_action,
        "reason": (
            f"Unknown or unauthorized action: "
            f"{action}"
        ),
    }


# ============================================================
# POLICY GUARDRAILS
# ============================================================

def validate_surge_against_policy(
    airport_code: str,
    new_multiplier: float,
    policy_max_surge: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Ensure the requested surge does not exceed policy.

    The AI cannot override this check.
    """

    airport_result = validate_airport_code(
        airport_code
    )

    if not airport_result["valid"]:
        return {
            "allowed": False,
            "result": "INPUT_BLOCKED",
            "reason": airport_result["error"],
        }

    multiplier_result = validate_surge_multiplier(
        new_multiplier
    )

    if not multiplier_result["valid"]:
        return {
            "allowed": False,
            "result": "INPUT_BLOCKED",
            "reason": multiplier_result["error"],
        }

    if policy_max_surge is None:
        policy_max_surge = MAX_SURGE_MULTIPLIER

    multiplier = multiplier_result[
        "new_multiplier"
    ]

    if multiplier > policy_max_surge:
        return {
            "allowed": False,
            "result": "POLICY_VIOLATION",
            "airport_code": airport_result[
                "airport_code"
            ],
            "requested_surge": multiplier,
            "policy_max_surge": policy_max_surge,
            "reason": (
                f"Requested surge {multiplier}x "
                f"exceeds the policy maximum of "
                f"{policy_max_surge}x."
            ),
        }

    return {
        "allowed": True,
        "result": "POLICY_ALLOWED",
        "airport_code": airport_result[
            "airport_code"
        ],
        "requested_surge": multiplier,
        "policy_max_surge": policy_max_surge,
        "reason": (
            f"Requested surge {multiplier}x is "
            f"within the policy maximum of "
            f"{policy_max_surge}x."
        ),
    }


# ============================================================
# OUTPUT GUARDRAILS
# ============================================================

def validate_tool_output(
    tool_name: str,
    result: Any,
) -> Dict[str, Any]:
    """
    Validate structured tool output before it is
    presented as a trusted result.
    """

    if result is None:
        return {
            "valid": False,
            "error": (
                f"Tool '{tool_name}' returned no result."
            ),
        }

    if not isinstance(result, dict):
        return {
            "valid": False,
            "error": (
                f"Tool '{tool_name}' returned an "
                "unexpected response type."
            ),
        }

    if result.get("success") is False:
        return {
            "valid": False,
            "error": result.get(
                "error",
                f"Tool '{tool_name}' failed.",
            ),
        }

    if "success" not in result:
        return {
            "valid": False,
            "error": (
                f"Tool '{tool_name}' response does "
                "not contain a success field."
            ),
        }

    return {
        "valid": True,
        "result": result,
    }


# ============================================================
# HUMAN-IN-THE-LOOP
# ============================================================

def request_human_approval(
    action: str,
    risk_level: str,
    reason: str,
) -> bool:
    """
    Interactive human approval.

    HIGH and MEDIUM operational actions cannot execute
    until the human explicitly approves them.
    """

    print()
    print("=" * 70)
    print("HUMAN APPROVAL REQUIRED")
    print("=" * 70)
    print(f"Action : {action}")
    print(f"Risk   : {risk_level}")
    print(f"Reason : {reason}")
    print("=" * 70)

    while True:
        decision = input(
            "Approve this action? [approve/reject]: "
        ).strip().lower()

        if decision in {
            "approve",
            "approved",
            "yes",
            "y",
        }:
            print("APPROVAL DECISION: APPROVED")
            return True

        if decision in {
            "reject",
            "rejected",
            "no",
            "n",
        }:
            print("APPROVAL DECISION: REJECTED")
            return False

        print(
            "Please enter 'approve' or 'reject'."
        )


# ============================================================
# COMPLETE SURGE GUARDRAIL
# ============================================================

def guard_surge_action(
    airport_code: str,
    new_multiplier: float,
    reason: str,
    policy_max_surge: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Run the complete Day 4 safety pipeline for a
    surge change.

    Order:

    1. Validate input
    2. Validate policy
    3. Classify risk
    4. Request human approval
    5. Return permission decision

    IMPORTANT:
    This function does NOT execute the surge tool.
    The caller must only execute when allowed=True.
    """

    airport_result = validate_airport_code(
        airport_code
    )

    if not airport_result["valid"]:
        return {
            "allowed": False,
            "status": "BLOCKED",
            "risk_level": "BLOCKED",
            "reason": airport_result["error"],
            "approval_required": False,
            "approval_decision": None,
        }

    multiplier_result = validate_surge_multiplier(
        new_multiplier
    )

    if not multiplier_result["valid"]:
        return {
            "allowed": False,
            "status": "BLOCKED",
            "risk_level": "BLOCKED",
            "reason": multiplier_result["error"],
            "approval_required": False,
            "approval_decision": None,
        }

    reason_result = validate_reason(reason)

    if not reason_result["valid"]:
        return {
            "allowed": False,
            "status": "BLOCKED",
            "risk_level": "BLOCKED",
            "reason": reason_result["error"],
            "approval_required": False,
            "approval_decision": None,
        }

    policy_result = validate_surge_against_policy(
        airport_code=airport_result["airport_code"],
        new_multiplier=multiplier_result[
            "new_multiplier"
        ],
        policy_max_surge=policy_max_surge,
    )

    if not policy_result["allowed"]:
        return {
            "allowed": False,
            "status": "BLOCKED",
            "risk_level": "BLOCKED",
            "reason": policy_result["reason"],
            "policy_result": policy_result[
                "result"
            ],
            "approval_required": False,
            "approval_decision": None,
        }

    risk_result = classify_surge_risk(
        multiplier_result["new_multiplier"]
    )

    approved = request_human_approval(
        action=(
            f"Increase {airport_result['airport_code']} "
            f"surge to "
            f"{multiplier_result['new_multiplier']}x"
        ),
        risk_level=risk_result["risk_level"],
        reason=reason_result["reason"],
    )

    if not approved:
        return {
            "allowed": False,
            "status": "REJECTED",
            "risk_level": risk_result["risk_level"],
            "reason": "Human approval was rejected.",
            "policy_result": policy_result[
                "result"
            ],
            "approval_required": True,
            "approval_decision": "REJECTED",
        }

    return {
        "allowed": True,
        "status": "APPROVED",
        "risk_level": risk_result["risk_level"],
        "reason": reason_result["reason"],
        "policy_result": policy_result[
            "result"
        ],
        "approval_required": True,
        "approval_decision": "APPROVED",
        "airport_code": airport_result[
            "airport_code"
        ],
        "new_multiplier": multiplier_result[
            "new_multiplier"
        ],
    }


# ============================================================
# DEMO / SELF TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("DAY 4 GUARDRAILS SELF TEST")
    print("=" * 70)

    print("\n1. Valid airport")
    print(validate_airport_code("SFO"))

    print("\n2. Invalid airport")
    print(validate_airport_code("UNKNOWN"))

    print("\n3. Valid surge")
    print(validate_surge_multiplier(1.3))

    print("\n4. Invalid surge")
    print(validate_surge_multiplier(100))

    print("\n5. Invalid driver count")
    print(validate_driver_count(-50))

    print("\n6. Risk classification - 1.2x")
    print(classify_surge_risk(1.2))

    print("\n7. Risk classification - 1.3x")
    print(classify_surge_risk(1.3))

    print("\n8. Policy check - 1.5x")
    print(
        validate_surge_against_policy(
            "SFO",
            1.5,
            1.5,
        )
    )

    print("\n9. Policy check - 2.0x")
    print(
        validate_surge_against_policy(
            "SFO",
            2.0,
            1.5,
        )
    )

    print("\n" + "=" * 70)
    print("DAY 4 GUARDRAILS SELF TEST COMPLETE")
    print("=" * 70)
