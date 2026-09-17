"""
DAY 3 - MULTI-AGENT AIRPORT OPERATIONS AI COPILOT

Architecture
------------
USER
  |
  v
ORCHESTRATOR
  |
  +--> Direct Answer
  |
  +--> Operations Investigator --> Tool
  |
  +--> Policy & Compliance Agent --> RAG
  |
  +--> Resolution Agent --> Recommendation

Features
--------
- Multi-agent architecture
- Agent orchestration
- Agent handoffs
- Tool usage
- RAG within agents
- ReAct-style execution
- Conversational memory
- Clarification handling
- Maximum iteration control
"""

import re

from src.tools import (
    get_airport_metrics,
    calculate_driver_incentive,
    trigger_surge_override,
)


# ============================================================
# CONFIGURATION
# ============================================================

MAX_ITERATIONS = 5

VALID_AIRPORTS = {"SFO", "LAX", "JFK"}

AIRPORT_NAMES = {
    "SFO": "San Francisco International Airport",
    "LAX": "Los Angeles International Airport",
    "JFK": "John F. Kennedy International Airport",
}


# ============================================================
# CONVERSATIONAL MEMORY
# ============================================================

conversation_memory = {
    "last_airport": None,
    "last_metrics": None,
    "pending_intent": None,
    "pending_details": {},
}


def update_memory(
    airport=None,
    metrics=None,
    pending_intent=None,
    pending_details=None,
):
    if airport:
        conversation_memory["last_airport"] = airport.upper()

    if metrics is not None:
        conversation_memory["last_metrics"] = metrics

    if pending_intent is not None:
        conversation_memory["pending_intent"] = pending_intent

    if pending_details is not None:
        conversation_memory["pending_details"] = pending_details


def clear_pending():
    conversation_memory["pending_intent"] = None
    conversation_memory["pending_details"] = {}


def get_last_airport():
    return conversation_memory.get("last_airport")


# ============================================================
# EXTRACTION HELPERS
# ============================================================

def extract_airport(text):
    """Extract SFO, LAX or JFK from text."""

    if not text:
        return None

    upper_text = text.upper()

    for airport in VALID_AIRPORTS:
        if re.search(rf"\b{airport}\b", upper_text):
            return airport

    return None


def extract_driver_count(text):
    """Extract driver count."""

    if not text:
        return None

    patterns = [
        r"(\d+)\s+drivers?",
        r"for\s+(\d+)",
        r"(\d+)\s+driver",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return int(match.group(1))

    return None


def extract_severity(text):
    """Extract LOW, MEDIUM or HIGH."""

    if not text:
        return None

    upper_text = text.upper()

    for severity in ["HIGH", "MEDIUM", "LOW"]:
        if re.search(rf"\b{severity}\b", upper_text):
            return severity

    return None


def extract_multiplier(text):
    """Extract surge multiplier such as 1.3x or 1.5."""

    if not text:
        return None

    patterns = [
        r"(?:to|at|of)\s+(\d+(?:\.\d+)?)\s*x?",
        r"(\d+(?:\.\d+)?)\s*x",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None

    return None


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(text):
    """
    Determine user intent.

    Returns:
        greeting
        explanation
        completion_rate
        airport_metrics
        surge
        incentive
        surge_override
        investigate
        unknown
    """

    text_lower = text.lower().strip()

    # --------------------------------------------------------
    # GREETING
    # --------------------------------------------------------

    greetings = {
        "hi",
        "hello",
        "hey",
        "hi there",
        "hello there",
        "good morning",
        "good afternoon",
        "good evening",
    }

    if text_lower in greetings:
        return "greeting"

    # --------------------------------------------------------
    # GENERAL EXPLANATION
    # --------------------------------------------------------

    if (
        "what does an airport operations ai copilot do"
        in text_lower
        or "what is an airport operations ai copilot"
        in text_lower
        or "what does this copilot do"
        in text_lower
    ):
        return "explanation"

    # --------------------------------------------------------
    # INCENTIVE
    # --------------------------------------------------------

    if "incentive" in text_lower or "incentives" in text_lower:
        return "incentive"

    # --------------------------------------------------------
    # SURGE OVERRIDE
    # --------------------------------------------------------

    surge_action_words = [
        "trigger a surge",
        "increase surge",
        "set the surge",
        "set surge",
        "surge override",
        "change surge",
        "raise surge",
        "increase the surge",
    ]

    if any(word in text_lower for word in surge_action_words):
        return "surge_override"

    # --------------------------------------------------------
    # INVESTIGATION
    # --------------------------------------------------------

    investigation_words = [
        "investigate",
        "investigation",
        "operational issue",
        "anomaly",
        "problem at",
        "why is",
        "why are",
        "what is wrong",
    ]

    if any(word in text_lower for word in investigation_words):
        return "investigate"

    # --------------------------------------------------------
    # SURGE INFORMATION
    # --------------------------------------------------------

    if (
        "surge" in text_lower
        or "multiplier" in text_lower
    ):
        return "surge"

    # --------------------------------------------------------
    # COMPLETION RATE
    # --------------------------------------------------------

    if "completion rate" in text_lower:
        return "completion_rate"

    # --------------------------------------------------------
    # GENERAL AIRPORT METRICS
    # --------------------------------------------------------

    metric_words = [
        "metrics",
        "eta",
        "active drivers",
        "drivers",
        "cancellation",
        "queue",
        "request volume",
        "wait time",
    ]

    if any(word in text_lower for word in metric_words):
        return "airport_metrics"

    return "unknown"


# ============================================================
# AGENT 1 - OPERATIONS INVESTIGATOR
# ============================================================

def operations_investigator(airport):
    """
    Investigate airport telemetry using the operational tool.
    """

    print()
    print("[INVESTIGATOR AGENT]")
    print("Analyzing operational telemetry...")

    result = get_airport_metrics(airport)

    if not result.get("success"):
        return {
            "success": False,
            "error": result.get(
                "error",
                "Unable to retrieve airport metrics.",
            ),
        }

    metrics = result["metrics"]

    update_memory(
        airport=airport,
        metrics=metrics,
    )

    completion = metrics["completion_rate"]

    # Project assumption:
    # completion >= 0.85 is considered normal.
    if completion < 0.85:
        status = "ANOMALY"
        severity = "HIGH" if completion < 0.75 else "MEDIUM"
    else:
        status = "NORMAL"
        severity = "LOW"

    print(f"Airport: {airport}")
    print(f"Status: {status}")
    print(f"Severity: {severity}")
    print(
        f"Completion rate: "
        f"{completion * 100:.1f}%"
    )

    if status == "ANOMALY":
        print("Potential contributing factors:")

        if metrics["driver_cancellation_rate"] > 0.10:
            print(
                "- High driver cancellation rate"
            )

        if metrics["queue_size"] > 100:
            print(
                "- Large airport queue"
            )

        if metrics["average_eta_minutes"] > 15:
            print(
                "- Increased ETA"
            )
    else:
        print(
            "No significant operational anomaly detected."
        )

    return {
        "success": True,
        "airport": airport,
        "metrics": metrics,
        "status": status,
        "severity": severity,
    }


# ============================================================
# AGENT 2 - POLICY & COMPLIANCE
# ============================================================

def policy_compliance_agent(
    airport,
    requested_multiplier=None,
):
    """
    Retrieve relevant airport policy.

    This implementation uses the existing local policy
    knowledge base through simple document matching.
    """

    print()
    print("[POLICY & COMPLIANCE AGENT]")
    print("Searching policy knowledge base...")

    policy_dir = "data/airport_policies"

    # Some projects use airport_policies directory.
    # Others may use airport_policies directly under data.
    from pathlib import Path

    policy_path = Path(policy_dir)

    if not policy_path.exists():
        # Fallback for the current repository structure.
        policy_path = Path("data/airport_policies")

    documents = []

    if policy_path.exists():
        for file in policy_path.glob("*.md"):
            name = file.name.lower()

            if airport.lower() in name:
                documents.append(file)

    # Fallback: search all markdown policy files.
    if not documents and policy_path.exists():
        documents = list(policy_path.glob("*.md"))

    retrieved_sources = [
        file.name
        for file in documents
    ]

    print(
        f"Retrieved sources: {retrieved_sources}"
    )

    # --------------------------------------------------------
    # Read policy content
    # --------------------------------------------------------

    policy_text = ""

    for file in documents:
        try:
            policy_text += "\n" + file.read_text(
                encoding="utf-8"
            )
        except Exception:
            pass

    # --------------------------------------------------------
    # Determine maximum surge
    # --------------------------------------------------------

    maximum_surge = 1.5

    matches = re.findall(
        r"(?:maximum|max(?:imum)? permitted surge)"
        r".{0,80}?(\d+(?:\.\d+)?)x?",
        policy_text,
        re.IGNORECASE,
    )

    if matches:
        try:
            maximum_surge = max(
                float(value)
                for value in matches
            )
        except ValueError:
            maximum_surge = 1.5

    # --------------------------------------------------------
    # Determine policy result
    # --------------------------------------------------------

    if requested_multiplier is None:
        policy_result = "ACTION ALLOWED"

    elif requested_multiplier > maximum_surge:
        policy_result = "POLICY VIOLATION"

    elif requested_multiplier >= 1.3:
        policy_result = "ACTION REQUIRES APPROVAL"

    else:
        policy_result = "ACTION ALLOWED"

    print(
        f"Policy result: {policy_result}"
    )

    return {
        "success": True,
        "airport": airport,
        "retrieved_sources": retrieved_sources,
        "maximum_surge": maximum_surge,
        "policy_result": policy_result,
        "requested_multiplier": requested_multiplier,
    }


# ============================================================
# AGENT 3 - RESOLUTION
# ============================================================

def resolution_agent(
    airport,
    investigation,
    policy_result=None,
    requested_multiplier=None,
):
    """
    Evaluate findings and recommend a resolution.
    """

    print()
    print("[RESOLUTION AGENT]")
    print("Evaluating possible interventions...")

    metrics = investigation["metrics"]

    # --------------------------------------------------------
    # Surge request
    # --------------------------------------------------------

    if requested_multiplier is not None:

        if policy_result == "POLICY VIOLATION":
            recommendation = (
                f"Do not increase surge to "
                f"{requested_multiplier:.1f}x. "
                "The requested action violates policy."
            )

        elif policy_result == "ACTION REQUIRES APPROVAL":
            recommendation = (
                f"Request approval to increase "
                f"surge to {requested_multiplier:.1f}x. "
                "Do not execute until approval is received."
            )

        else:
            recommendation = (
                f"Increase surge to "
                f"{requested_multiplier:.1f}x."
            )

    # --------------------------------------------------------
    # Operational anomaly
    # --------------------------------------------------------

    elif investigation["status"] == "ANOMALY":

        actions = []

        if metrics["driver_cancellation_rate"] > 0.10:
            actions.append(
                "Investigate elevated driver cancellations"
            )

        if metrics["queue_size"] > 100:
            actions.append(
                "Reduce airport queue pressure"
            )

        if metrics["average_eta_minutes"] > 15:
            actions.append(
                "Investigate increased ETA"
            )

        if not actions:
            actions.append(
                "Monitor airport operational metrics"
            )

        recommendation = "; ".join(actions)

    else:
        recommendation = (
            "No immediate operational intervention "
            "is required."
        )

    print(
        f"Recommended action: {recommendation}"
    )

    return {
        "success": True,
        "recommendation": recommendation,
    }


# ============================================================
# DIRECT ANSWERS
# ============================================================

def direct_answer(text):
    """
    Answer questions that do not require an agent/tool.
    """

    intent = detect_intent(text)

    if intent == "greeting":
        return (
            "Hello! How can I help you with "
            "airport operations today?"
        )

    if intent == "explanation":
        return (
            "An Airport Operations AI Copilot helps "
            "airport operations teams monitor performance, "
            "investigate operational issues, retrieve "
            "relevant policies, and generate resolution "
            "recommendations for SFO, LAX, and JFK."
        )

    return None


# ============================================================
# SIMPLE METRIC ANSWERS
# ============================================================

def answer_metric_question(
    intent,
    airport,
):
    """
    Use Investigator only for telemetry questions.
    """

    investigation = operations_investigator(
        airport
    )

    if not investigation["success"]:
        return investigation["error"]

    metrics = investigation["metrics"]

    if intent == "completion_rate":
        return (
            f"The completion rate at {airport} is "
            f"{metrics['completion_rate'] * 100:.1f}%."
        )

    if intent == "surge":
        return (
            f"The current surge multiplier at "
            f"{airport} is "
            f"{metrics['surge_multiplier']:.1f}x."
        )

    if intent == "airport_metrics":
        return (
            f"Current metrics at {airport}: "
            f"completion rate "
            f"{metrics['completion_rate'] * 100:.1f}%, "
            f"average ETA "
            f"{metrics['average_eta_minutes']} minutes, "
            f"active drivers "
            f"{metrics['active_drivers']}, "
            f"driver cancellation rate "
            f"{metrics['driver_cancellation_rate'] * 100:.1f}%, "
            f"queue size "
            f"{metrics['queue_size']}, "
            f"surge "
            f"{metrics['surge_multiplier']:.1f}x, "
            f"request volume "
            f"{metrics['request_volume']}."
        )

    return None


# ============================================================
# INCENTIVE TOOL
# ============================================================

def handle_incentive(text):
    """Handle driver incentive requests."""

    driver_count = extract_driver_count(text)
    severity = extract_severity(text)

    if driver_count is None:
        return (
            "Please provide the number of drivers."
        )

    if severity is None:
        return (
            "Please provide the severity level: "
            "LOW, MEDIUM, or HIGH."
        )

    result = calculate_driver_incentive(
        driver_count,
        severity,
    )

    if not result.get("success"):
        return result.get(
            "error",
            "Unable to calculate incentive.",
        )

    incentive = result[
        "recommended_incentive_per_driver"
    ]

    total = result[
        "estimated_total_cost"
    ]

    return (
        f"The recommended incentive is "
        f"${incentive:.2f} per driver for "
        f"{driver_count} drivers at {severity} severity. "
        f"The estimated total cost is "
        f"${total:.2f}."
    )


# ============================================================
# SURGE OVERRIDE
# ============================================================

def handle_surge_override(
    text,
    airport,
):
    """
    Day 3:
    Investigate -> Policy -> Resolution.

    Actual approval controls belong to Day 4.
    """

    multiplier = extract_multiplier(text)

    if multiplier is None:
        return (
            "Please provide the requested surge "
            "multiplier, for example 1.3x."
        )

    # --------------------------------------------------------
    # ITERATION 1
    # --------------------------------------------------------

    print()
    print("========== ITERATION 1 ==========")
    print(
        "[Iteration 1] THINK -> Orchestrator: "
        "Determine which specialist should investigate "
        "the airport before changing surge."
    )
    print(
        "[Iteration 1] ACT -> Operations Investigator"
    )

    investigation = operations_investigator(
        airport
    )

    print(
        "[Iteration 1] OBSERVE -> Orchestrator: "
        "Operational telemetry has been collected."
    )

    if not investigation["success"]:
        return investigation["error"]

    # --------------------------------------------------------
    # ITERATION 2
    # --------------------------------------------------------

    print()
    print("========== ITERATION 2 ==========")
    print(
        "[Iteration 2] THINK -> Orchestrator: "
        "Validate the requested surge change against "
        "operational policy."
    )
    print(
        "[Iteration 2] ACT -> Policy & Compliance Agent"
    )

    policy = policy_compliance_agent(
        airport,
        multiplier,
    )

    print(
        "[Iteration 2] OBSERVE -> Orchestrator: "
        "Relevant policy has been retrieved and checked."
    )

    # --------------------------------------------------------
    # ITERATION 3
    # --------------------------------------------------------

    print()
    print("========== ITERATION 3 ==========")
    print(
        "[Iteration 3] THINK -> Orchestrator: "
        "Evaluate operational findings and policy result "
        "before recommending an action."
    )
    print(
        "[Iteration 3] ACT -> Resolution Agent"
    )

    resolution = resolution_agent(
        airport,
        investigation,
        policy["policy_result"],
        multiplier,
    )

    print(
        "[Iteration 3] OBSERVE -> Orchestrator: "
        "A resolution recommendation has been generated."
    )

    # --------------------------------------------------------
    # FINAL RESPONSE
    # --------------------------------------------------------

    if policy["policy_result"] == "POLICY VIOLATION":

        return (
            f"The requested surge change at {airport} "
            f"to {multiplier:.1f}x violates the applicable "
            "airport policy and should not be executed.\n\n"
            f"Recommendation: "
            f"{resolution['recommendation']}"
        )

    if (
        policy["policy_result"]
        == "ACTION REQUIRES APPROVAL"
    ):

        return (
            f"The requested surge change at {airport} "
            f"to {multiplier:.1f}x requires approval "
            "before execution.\n\n"
            f"Recommendation: "
            f"{resolution['recommendation']}"
        )

    return (
        f"The requested surge change at {airport} "
        f"to {multiplier:.1f}x is allowed by the "
        "current policy.\n\n"
        f"Recommendation: "
        f"{resolution['recommendation']}"
    )


# ============================================================
# INVESTIGATION WORKFLOW
# ============================================================

def handle_investigation(
    text,
    airport,
):
    """
    Full multi-agent investigation workflow.
    """

    # --------------------------------------------------------
    # ITERATION 1
    # --------------------------------------------------------

    print()
    print("========== ITERATION 1 ==========")
    print(
        "[Iteration 1] THINK -> Orchestrator: "
        "Determine which specialist should investigate "
        "the airport."
    )
    print(
        "[Iteration 1] ACT -> Operations Investigator"
    )

    investigation = operations_investigator(
        airport
    )

    print(
        "[Iteration 1] OBSERVE -> Orchestrator: "
        "Operational telemetry has been collected."
    )

    if not investigation["success"]:
        return investigation["error"]

    # --------------------------------------------------------
    # ITERATION 2
    # --------------------------------------------------------

    print()
    print("========== ITERATION 2 ==========")
    print(
        "[Iteration 2] THINK -> Orchestrator: "
        "Determine whether relevant policy information "
        "is required for the investigation."
    )
    print(
        "[Iteration 2] ACT -> Policy & Compliance Agent"
    )

    policy = policy_compliance_agent(
        airport
    )

    print(
        "[Iteration 2] OBSERVE -> Orchestrator: "
        "Relevant policy has been retrieved and checked."
    )

    # --------------------------------------------------------
    # ITERATION 3
    # --------------------------------------------------------

    print()
    print("========== ITERATION 3 ==========")
    print(
        "[Iteration 3] THINK -> Orchestrator: "
        "Evaluate operational findings and generate "
        "a resolution."
    )
    print(
        "[Iteration 3] ACT -> Resolution Agent"
    )

    resolution = resolution_agent(
        airport,
        investigation,
        policy["policy_result"],
    )

    print(
        "[Iteration 3] OBSERVE -> Orchestrator: "
        "A resolution recommendation has been generated."
    )

    metrics = investigation["metrics"]

    return (
        f"The investigation of {airport} shows a "
        f"{investigation['status'].lower()} condition "
        f"with a completion rate of "
        f"{metrics['completion_rate'] * 100:.1f}% "
        f"and severity "
        f"{investigation['severity']}.\n\n"
        f"Recommendation:\n"
        f"{resolution['recommendation']}"
    )


# ============================================================
# MAIN ORCHESTRATOR
# ============================================================

def process_request(user_text):
    """
    Main Day 3 orchestrator.

    Important:
    The orchestrator decides whether the request needs
    a direct answer, a tool, or the full multi-agent flow.
    """

    text = user_text.strip()

    if not text:
        return ""

    # --------------------------------------------------------
    # Direct answers
    # --------------------------------------------------------

    answer = direct_answer(text)

    if answer:
        clear_pending()
        return answer

    intent = detect_intent(text)

    # --------------------------------------------------------
    # Extract airport
    # --------------------------------------------------------

    airport = extract_airport(text)

    # --------------------------------------------------------
    # Conversational memory
    # --------------------------------------------------------

    if not airport:
        airport = get_last_airport()

    # --------------------------------------------------------
    # Handle clarification
    # --------------------------------------------------------

    pending_intent = conversation_memory.get(
        "pending_intent"
    )

    if (
        pending_intent
        and text.upper() in VALID_AIRPORTS
    ):
        airport = text.upper()
        intent = pending_intent
        clear_pending()

    # --------------------------------------------------------
    # If an airport is explicitly mentioned, remember it.
    # --------------------------------------------------------

    if airport:
        update_memory(airport=airport)

    # --------------------------------------------------------
    # Missing airport for metric/investigation questions
    # --------------------------------------------------------

    if intent in {
        "completion_rate",
        "airport_metrics",
        "surge",
        "investigate",
        "surge_override",
    } and not airport:

        update_memory(
            pending_intent=intent
        )

        metric_name = {
            "completion_rate": "completion rate",
            "airport_metrics": "metrics",
            "surge": "surge multiplier",
            "investigate": "investigation",
            "surge_override": "surge change",
        }.get(intent, "request")

        return (
            f"Which airport would you like the "
            f"{metric_name} for? "
            "Please provide SFO, LAX, or JFK."
        )

    # --------------------------------------------------------
    # Incentive
    # --------------------------------------------------------

    if intent == "incentive":

        print()
        print(
            "[ORCHESTRATOR] Handoff -> "
            "Driver Incentive Tool"
        )

        return handle_incentive(text)

    # --------------------------------------------------------
    # Simple telemetry
    # --------------------------------------------------------

    if intent in {
        "completion_rate",
        "airport_metrics",
        "surge",
    }:

        print()
        print(
            "[ORCHESTRATOR] Handoff -> "
            "Operations Investigator"
        )

        return answer_metric_question(
            intent,
            airport,
        )

    # --------------------------------------------------------
    # Surge action
    # --------------------------------------------------------

    if intent == "surge_override":

        return handle_surge_override(
            text,
            airport,
        )

    # --------------------------------------------------------
    # Full investigation
    # --------------------------------------------------------

    if intent == "investigate":

        return handle_investigation(
            text,
            airport,
        )

    # --------------------------------------------------------
    # Airport-only follow-up
    # --------------------------------------------------------

    if (
        text.upper() in VALID_AIRPORTS
        and pending_intent is None
    ):

        update_memory(airport=text.upper())

        return (
            f"{text.upper()} is now the active airport. "
            "What would you like to know?"
        )

    # --------------------------------------------------------
    # Unknown
    # --------------------------------------------------------

    return (
        "I can help with airport metrics, "
        "completion rate, surge, driver incentives, "
        "airport investigations, and operational "
        "recommendations for SFO, LAX, and JFK."
    )


# ============================================================
# CLI
# ============================================================

def main():

    print("=" * 70)
    print("AIRPORT OPERATIONS AI COPILOT")
    print("DAY 3 - MULTI-AGENT SYSTEM")
    print("=" * 70)
    print("Agents:")
    print("1. Orchestrator")
    print("2. Operations Investigator")
    print("3. Policy & Compliance Agent")
    print("4. Resolution Agent")
    print("ReAct iterations: 5")
    print("=" * 70)
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 70)

    while True:

        try:
            user_text = input("\nUSER: ")

        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if user_text.strip().lower() in {
            "exit",
            "quit",
        }:
            print("Exiting...")
            break

        if not user_text.strip():
            continue

        print()
        print("PROCESSING...")
        print("-" * 70)

        try:
            result = process_request(
                user_text
            )

            print()
            print("FINAL ANSWER")
            print("-" * 70)
            print(result)

        except Exception as exc:

            print()
            print("ERROR")
            print("-" * 70)
            print(
                f"{type(exc).__name__}: {exc}"
            )


if __name__ == "__main__":
    main()