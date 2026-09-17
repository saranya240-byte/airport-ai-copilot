"""
DAY 3 - MULTI-AGENT AIRPORT OPERATIONS AI COPILOT

Agents:
1. Orchestrator
2. Operations Investigator
3. Policy & Compliance Agent
4. Resolution Agent

Features:
- Multi-agent architecture
- Agent handoffs
- Tool usage
- Policy/RAG lookup
- ReAct-style execution trace
- Conversation memory
- Follow-up questions
- Clarification handling
- Maximum iteration control
"""

import os
import re
from pathlib import Path

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

# Short-term conversation memory
conversation_memory = {
    "last_airport": None,
    "last_metrics": None,
    "pending_intent": None,
    "pending_details": {},
}


# ============================================================
# MEMORY
# ============================================================

def update_memory(
    airport=None,
    metrics=None,
    pending_intent=None,
    pending_details=None,
):
    """Update short-term conversational memory."""

    if airport:
        conversation_memory["last_airport"] = airport.upper()

    if metrics is not None:
        conversation_memory["last_metrics"] = metrics

    if pending_intent is not None:
        conversation_memory["pending_intent"] = pending_intent

    if pending_details is not None:
        conversation_memory["pending_details"] = pending_details


def clear_pending():
    """Clear pending clarification state."""

    conversation_memory["pending_intent"] = None
    conversation_memory["pending_details"] = {}


def get_last_airport():
    """Return the most recently referenced airport."""

    return conversation_memory.get("last_airport")


# ============================================================
# BASIC PARSING
# ============================================================

def extract_airport(text):
    """
    Extract SFO, LAX or JFK from user text.
    """

    if not text:
        return None

    upper_text = text.upper()

    for airport in VALID_AIRPORTS:
        # Match complete airport code only
        if re.search(rf"\b{airport}\b", upper_text):
            return airport

    return None


def extract_driver_count(text):
    """
    Extract driver count from natural language.

    Examples:
        40 drivers -> 40
        for 25 drivers -> 25
    """

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
    """Extract LOW, MEDIUM or HIGH severity."""

    if not text:
        return None

    upper_text = text.upper()

    for severity in ["HIGH", "MEDIUM", "LOW"]:
        if re.search(rf"\b{severity}\b", upper_text):
            return severity

    return None


def extract_multiplier(text):
    """
    Extract surge multiplier.

    Supports:
        1.3x
        1.5x
        1.3
        to 1.5x
    """

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
                pass

    return None


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(text):
    """
    Determine the user's operational intent.

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

    # Greeting
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

    # Explanation
    if (
        "what does an airport operations ai copilot do" in text_lower
        or "what is an airport operations ai copilot" in text_lower
        or "what does this copilot do" in text_lower
    ):
        return "explanation"

    # Driver incentive
    if (
        "incentive" in text_lower
        or "incentives" in text_lower
    ):
        return "incentive"

    # Surge override/action
    if (
        "trigger a surge" in text_lower
        or "increase surge" in text_lower
        or "set the surge" in text_lower
        or "set surge" in text_lower
        or "surge override" in text_lower
        or "change surge" in text_lower
        or "raise surge" in text_lower
    ):
        return "surge_override"

    # Investigation
    if (
        "investigate" in text_lower
        or "investigation" in text_lower
        or "operational issue" in text_lower
        or "anomaly" in text_lower
        or "problem at" in text_lower
    ):
        return "investigate"

    # Surge metric
    if (
        "surge" in text_lower
        or "multiplier" in text_lower
    ):
        return "surge"

    # Completion rate
    if "completion rate" in text_lower:
        return "completion_rate"

    # General airport metrics
    metric_words = [
        "metrics",
        "active drivers",
        "drivers",
        "queue",
        "queue size",
        "eta",
        "cancellation",
        "request volume",
    ]

    if any(word in text_lower for word in metric_words):
        return "airport_metrics"

    return "unknown"


# ============================================================
# CLARIFICATION HANDLING
# ============================================================

def resolve_pending_input(text):
    """
    Handle a response to a previous clarification.

    Example:

        USER: What is the completion rate?
        AI: Which airport?
        USER: LAX

    This function converts LAX into the pending completion-rate request.
    """

    pending_intent = conversation_memory.get("pending_intent")

    if not pending_intent:
        return None

    airport = extract_airport(text)

    if airport:
        details = conversation_memory.get(
            "pending_details",
            {},
        ).copy()

        details["airport_code"] = airport

        original_intent = pending_intent

        clear_pending()

        return original_intent, details

    return None


# ============================================================
# ORCHESTRATOR AGENT
# ============================================================

class OrchestratorAgent:
    """
    Central controller.

    Determines which specialist should act.
    """

    def route(self, intent):
        if intent in {
            "completion_rate",
            "airport_metrics",
            "surge",
            "investigate",
        }:
            return "Operations Investigator"

        if intent == "incentive":
            return "Operations Investigator"

        if intent == "surge_override":
            return "Operations Investigator"

        return None


# ============================================================
# OPERATIONS INVESTIGATOR AGENT
# ============================================================

class OperationsInvestigatorAgent:
    """
    Investigates airport operational telemetry.
    """

    def investigate(self, airport_code):
        print("\n[INVESTIGATOR AGENT]")
        print("Analyzing operational telemetry...")
        print(f"Airport: {airport_code}")

        result = get_airport_metrics(airport_code)

        if not result.get("success"):
            print(f"Investigation failed: {result.get('error')}")
            return result

        metrics = result["metrics"]

        completion_rate = metrics["completion_rate"]
        cancellation_rate = metrics["driver_cancellation_rate"]
        queue_size = metrics["queue_size"]
        eta = metrics["average_eta_minutes"]

        # Operational severity rules
        if completion_rate < 0.80:
            severity = "HIGH"
            status = "CRITICAL"
        elif completion_rate < 0.90:
            severity = "MEDIUM"
            status = "ANOMALY"
        else:
            severity = "LOW"
            status = "NORMAL"

        print(f"Status: {status}")
        print(f"Severity: {severity}")
        print(
            f"Completion rate: "
            f"{completion_rate * 100:.1f}%"
        )

        if status == "NORMAL":
            print(
                "No significant operational anomaly detected."
            )
        else:
            print("Potential contributing factors:")

            if cancellation_rate > 0.06:
                print("- Elevated driver cancellation rate")

            if queue_size > 50:
                print("- Large airport queue")

            if eta > 10:
                print("- Increased average ETA")

        return {
            "success": True,
            "airport_code": airport_code,
            "metrics": metrics,
            "severity": severity,
            "status": status,
        }


# ============================================================
# POLICY & COMPLIANCE AGENT
# ============================================================

class PolicyComplianceAgent:
    """
    Searches local policy/RAG knowledge base.

    The agent looks for markdown/text policy documents.
    """

    def find_policy_files(self, airport_code):
        """
        Find policy documents associated with the airport.
        """

        project_root = Path(__file__).resolve().parent.parent

        possible_directories = [
            project_root / "knowledge_base",
            project_root / "knowledge",
            project_root / "data",
            project_root / "docs",
            project_root / "rag",
        ]

        files = []

        for directory in possible_directories:
            if not directory.exists():
                continue

            for extension in ["*.md", "*.txt"]:
                files.extend(directory.rglob(extension))

        airport_lower = airport_code.lower()

        airport_files = [
            file
            for file in files
            if airport_lower in file.name.lower()
        ]

        return airport_files

    def search_policy(
        self,
        airport_code,
        action=None,
        new_multiplier=None,
    ):
        print("\n[POLICY & COMPLIANCE AGENT]")
        print("Searching policy knowledge base...")

        policy_files = self.find_policy_files(airport_code)

        retrieved_sources = [
            file.name for file in policy_files
        ]

        if retrieved_sources:
            print(
                f"Retrieved sources: "
                f"{retrieved_sources}"
            )
        else:
            print(
                "No local policy documents found; "
                "using configured policy rules."
            )

        # ----------------------------------------------------
        # Default policy rules
        # ----------------------------------------------------
        #
        # These rules provide a safe fallback if policy files
        # are unavailable.
        #
        # Maximum surge is 1.5x.
        # Increasing surge requires approval.
        #

        if action == "surge_override":

            if new_multiplier is None:
                return {
                    "success": False,
                    "policy_result": "UNKNOWN",
                    "error": (
                        "Surge multiplier is required."
                    ),
                    "sources": retrieved_sources,
                }

            if new_multiplier > 1.5:
                policy_result = "ACTION NOT ALLOWED"
                reason = (
                    "Requested surge exceeds the "
                    "maximum permitted multiplier of 1.5x."
                )

            elif new_multiplier > 1.1:
                policy_result = "ACTION REQUIRES APPROVAL"
                reason = (
                    "Increasing surge above the current "
                    "baseline requires approval."
                )

            else:
                policy_result = "ACTION ALLOWED"
                reason = (
                    "Requested surge is within the "
                    "configured policy limit."
                )

        else:
            policy_result = "ACTION ALLOWED"
            reason = "No restricted operational action requested."

        print(f"Policy result: {policy_result}")

        return {
            "success": True,
            "policy_result": policy_result,
            "reason": reason,
            "sources": retrieved_sources,
        }


# ============================================================
# RESOLUTION AGENT
# ============================================================

class ResolutionAgent:
    """
    Generates operational recommendations.
    """

    def recommend(
        self,
        investigation,
        policy_result=None,
        requested_action=None,
        requested_multiplier=None,
    ):
        print("\n[RESOLUTION AGENT]")
        print("Evaluating possible interventions...")

        if not investigation:
            recommendation = (
                "Insufficient operational information "
                "to generate a recommendation."
            )

            print(
                f"Recommended action: {recommendation}"
            )

            return recommendation

        metrics = investigation["metrics"]

        completion_rate = metrics["completion_rate"]
        cancellation_rate = metrics[
            "driver_cancellation_rate"
        ]
        queue_size = metrics["queue_size"]

        # Surge request
        if requested_action == "surge_override":

            if policy_result == "ACTION NOT ALLOWED":
                recommendation = (
                    "Do not execute the requested surge "
                    "override because it violates policy."
                )

            elif policy_result == "ACTION REQUIRES APPROVAL":
                recommendation = (
                    f"Request approval to increase surge "
                    f"to {requested_multiplier:.1f}x. "
                    f"Do not execute until approval is received."
                )

            else:
                recommendation = (
                    f"The requested surge change to "
                    f"{requested_multiplier:.1f}x is allowed "
                    f"under the current policy."
                )

            print(
                f"Recommended action: {recommendation}"
            )

            return recommendation

        # Operational anomaly
        if completion_rate < 0.90:

            actions = []

            if queue_size > 50:
                actions.append(
                    "reduce airport queue pressure"
                )

            if cancellation_rate > 0.06:
                actions.append(
                    "investigate elevated driver cancellations"
                )

            actions.append(
                "consider additional driver incentives"
            )

            recommendation = (
                "Recommended actions: "
                + "; ".join(actions)
                + "."
            )

        else:
            recommendation = (
                "No immediate operational intervention "
                "is required."
            )

        print(
            f"Recommended action: {recommendation}"
        )

        return recommendation


# ============================================================
# REACT TRACE
# ============================================================

def print_think(iteration, message):
    print(
        f"[Iteration {iteration}] "
        f"THINK -> Orchestrator: {message}"
    )


def print_act(iteration, agent):
    print(
        f"[Iteration {iteration}] "
        f"ACT -> {agent}"
    )


def print_observe(iteration, message):
    print(
        f"[Iteration {iteration}] "
        f"OBSERVE -> Orchestrator: {message}"
    )


# ============================================================
# RESPONSE GENERATION
# ============================================================

def answer_completion_rate(metrics):
    return (
        f"The completion rate at "
        f"{metrics['airport_code']} is "
        f"{metrics['metrics']['completion_rate'] * 100:.1f}%."
    )


def answer_surge(metrics):
    return (
        f"The current surge multiplier at "
        f"{metrics['airport_code']} is "
        f"{metrics['metrics']['surge_multiplier']:.1f}x."
    )


def answer_metrics(metrics):
    data = metrics["metrics"]
    airport = metrics["airport_code"]

    return (
        f"At {airport}, the completion rate is "
        f"{data['completion_rate'] * 100:.1f}%, "
        f"the average ETA is "
        f"{data['average_eta_minutes']:.1f} minutes, "
        f"there are {data['active_drivers']} active drivers, "
        f"the driver cancellation rate is "
        f"{data['driver_cancellation_rate'] * 100:.1f}%, "
        f"the queue size is {data['queue_size']}, "
        f"the surge multiplier is "
        f"{data['surge_multiplier']:.1f}x, "
        f"and the request volume is "
        f"{data['request_volume']}."
    )


# ============================================================
# PROCESS METRIC REQUEST
# ============================================================

def process_metric_request(
    intent,
    airport_code,
):
    """
    Process normal telemetry questions.

    Simple metric questions only require the investigator.
    """

    investigator = OperationsInvestigatorAgent()

    result = investigator.investigate(
        airport_code
    )

    if not result.get("success"):
        return result.get(
            "error",
            "Unable to retrieve airport metrics.",
        )

    update_memory(
        airport=airport_code,
        metrics=result,
    )

    if intent == "completion_rate":
        return answer_completion_rate(result)

    if intent == "surge":
        return answer_surge(result)

    return answer_metrics(result)


# ============================================================
# PROCESS INCENTIVE
# ============================================================

def process_incentive(
    driver_count,
    severity,
):
    """
    Driver incentive does not require airport investigation.
    """

    if driver_count is None:
        return (
            "How many drivers should receive the incentive?"
        )

    if severity is None:
        return (
            "What severity level should I use? "
            "Please provide LOW, MEDIUM, or HIGH."
        )

    result = calculate_driver_incentive(
        driver_count,
        severity,
    )

    if not result.get("success"):
        return (
            f"Error: {result.get('error')}"
        )

    per_driver = result[
        "recommended_incentive_per_driver"
    ]

    total = result[
        "estimated_total_cost"
    ]

    return (
        f"The recommended incentive is "
        f"${per_driver:.2f} per driver for "
        f"{driver_count} drivers at {severity} severity. "
        f"The estimated total cost is ${total:.2f}."
    )


# ============================================================
# PROCESS SURGE OVERRIDE
# ============================================================

def process_surge_override(
    airport_code,
    multiplier,
    reason,
):
    """
    Surge override requires:
    1. Investigator
    2. Policy Agent
    3. Resolution Agent

    Actual execution is NOT performed when approval
    is required.
    """

    if not airport_code:
        return (
            "Which airport should I apply the surge "
            "override to? Please provide SFO, LAX, or JFK."
        )

    if multiplier is None:
        return (
            "What surge multiplier would you like to set?"
        )

    if not reason:
        reason = "operational demand"

    investigator = OperationsInvestigatorAgent()
    policy_agent = PolicyComplianceAgent()
    resolution_agent = ResolutionAgent()

    # --------------------------------------------------------
    # ITERATION 1
    # --------------------------------------------------------

    print("\n========== ITERATION 1 ==========")

    print_think(
        1,
        "Determine which specialist should investigate "
        "the airport before changing surge.",
    )

    print_act(
        1,
        "Operations Investigator",
    )

    investigation = investigator.investigate(
        airport_code
    )

    if not investigation.get("success"):
        return (
            f"Investigation failed: "
            f"{investigation.get('error')}"
        )

    print_observe(
        1,
        "Operational telemetry has been collected.",
    )

    # --------------------------------------------------------
    # ITERATION 2
    # --------------------------------------------------------

    print("\n========== ITERATION 2 ==========")

    print_think(
        2,
        "Validate the requested surge change "
        "against operational policy.",
    )

    print_act(
        2,
        "Policy & Compliance Agent",
    )

    policy = policy_agent.search_policy(
        airport_code=airport_code,
        action="surge_override",
        new_multiplier=multiplier,
    )

    print_observe(
        2,
        "Relevant policy has been retrieved and checked.",
    )

    # --------------------------------------------------------
    # ITERATION 3
    # --------------------------------------------------------

    print("\n========== ITERATION 3 ==========")

    print_think(
        3,
        "Evaluate the operational situation and "
        "policy result before recommending an action.",
    )

    print_act(
        3,
        "Resolution Agent",
    )

    recommendation = resolution_agent.recommend(
        investigation=investigation,
        policy_result=policy.get(
            "policy_result"
        ),
        requested_action="surge_override",
        requested_multiplier=multiplier,
    )

    print_observe(
        3,
        "A resolution recommendation has been generated.",
    )

    # --------------------------------------------------------
    # FINAL ANSWER
    # --------------------------------------------------------

    policy_result = policy.get(
        "policy_result"
    )

    if policy_result == "ACTION REQUIRES APPROVAL":

        return (
            f"The requested surge change at "
            f"{airport_code} to {multiplier:.1f}x "
            f"requires approval before execution.\n\n"
            f"Recommendation: {recommendation}"
        )

    if policy_result == "ACTION NOT ALLOWED":

        return (
            f"The requested surge change at "
            f"{airport_code} to {multiplier:.1f}x "
            f"cannot be executed because it violates policy.\n\n"
            f"Recommendation: {recommendation}"
        )

    # Only execute when policy allows it.
    execution = trigger_surge_override(
        airport_code=airport_code,
        new_multiplier=multiplier,
        reason=reason,
    )

    if not execution.get("success"):
        return (
            f"Surge override failed: "
            f"{execution.get('error')}"
        )

    return (
        f"The surge override was successfully triggered "
        f"at {airport_code} to {multiplier:.1f}x "
        f"because of {reason}. "
        f"Status: {execution.get('status')}."
    )


# ============================================================
# PROCESS INVESTIGATION
# ============================================================

def process_investigation(
    airport_code,
    user_text,
):
    """
    Full multi-agent investigation.
    """

    if not airport_code:
        return (
            "Which airport would you like me to investigate? "
            "Please provide SFO, LAX, or JFK."
        )

    investigator = OperationsInvestigatorAgent()
    policy_agent = PolicyComplianceAgent()
    resolution_agent = ResolutionAgent()

    # --------------------------------------------------------
    # ITERATION 1
    # --------------------------------------------------------

    print("\n========== ITERATION 1 ==========")

    print_think(
        1,
        "Determine which specialist should investigate "
        "the airport.",
    )

    print_act(
        1,
        "Operations Investigator",
    )

    investigation = investigator.investigate(
        airport_code
    )

    if not investigation.get("success"):
        return (
            f"Investigation failed: "
            f"{investigation.get('error')}"
        )

    print_observe(
        1,
        "Operational telemetry has been collected.",
    )

    # --------------------------------------------------------
    # ITERATION 2
    # --------------------------------------------------------

    print("\n========== ITERATION 2 ==========")

    print_think(
        2,
        "Determine whether relevant policy information "
        "is required for the investigation.",
    )

    print_act(
        2,
        "Policy & Compliance Agent",
    )

    policy = policy_agent.search_policy(
        airport_code=airport_code,
    )

    print_observe(
        2,
        "Relevant policy has been retrieved and checked.",
    )

    # --------------------------------------------------------
    # ITERATION 3
    # --------------------------------------------------------

    print("\n========== ITERATION 3 ==========")

    print_think(
        3,
        "Evaluate operational findings and "
        "generate a resolution.",
    )

    print_act(
        3,
        "Resolution Agent",
    )

    recommendation = resolution_agent.recommend(
        investigation=investigation,
        policy_result=policy.get(
            "policy_result"
        ),
    )

    print_observe(
        3,
        "A resolution recommendation has been generated.",
    )

    metrics = investigation["metrics"]

    return (
        f"The investigation of {airport_code} shows "
        f"a {investigation['status'].lower()} condition "
        f"with a completion rate of "
        f"{metrics['completion_rate'] * 100:.1f}% "
        f"and severity {investigation['severity']}.\n\n"
        f"Recommendation:\n"
        f"{recommendation}"
    )


# ============================================================
# MAIN REQUEST PROCESSOR
# ============================================================

def process_request(user_text):
    """
    Main Day 3 request processor.
    """

    text = user_text.strip()

    if not text:
        return None

    # --------------------------------------------------------
    # Check whether this is a response to a clarification.
    # --------------------------------------------------------

    pending = resolve_pending_input(text)

    if pending:
        intent, details = pending

        airport_code = details.get(
            "airport_code"
        )

        if intent in {
            "completion_rate",
            "airport_metrics",
            "surge",
        }:
            print("\nPROCESSING...")
            print("-" * 70)

            return process_metric_request(
                intent,
                airport_code,
            )

    # --------------------------------------------------------
    # Detect normal intent.
    # --------------------------------------------------------

    intent = detect_intent(text)

    airport_code = extract_airport(text)

    # --------------------------------------------------------
    # Greeting
    # --------------------------------------------------------

    if intent == "greeting":
        return (
            "Hello! How can I help you with "
            "airport operations today?"
        )

    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    if intent == "explanation":
        return (
            "An Airport Operations AI Copilot helps "
            "airport operations teams monitor performance "
            "and make operational decisions. In this project, "
            "it can retrieve airport metrics, calculate "
            "driver incentives, retrieve applicable policies, "
            "investigate operational issues, and generate "
            "resolution recommendations for SFO, LAX, and JFK."
        )

    # --------------------------------------------------------
    # COMPLETION RATE
    # --------------------------------------------------------

    if intent == "completion_rate":

        if not airport_code:
            # Use conversation memory if available.
            airport_code = get_last_airport()

        if not airport_code:

            update_memory(
                pending_intent="completion_rate",
                pending_details={},
            )

            return (
                "Which airport would you like the "
                "completion rate for? "
                "Please provide SFO, LAX, or JFK."
            )

        print("\nPROCESSING...")
        print("-" * 70)

        return process_metric_request(
            "completion_rate",
            airport_code,
        )

    # --------------------------------------------------------
    # SURGE METRIC
    # --------------------------------------------------------

    if intent == "surge":

        # "its surge" should use last airport.
        if not airport_code:
            airport_code = get_last_airport()

        if not airport_code:

            update_memory(
                pending_intent="surge",
                pending_details={},
            )

            return (
                "Which airport would you like the "
                "surge multiplier for? "
                "Please provide SFO, LAX, or JFK."
            )

        print("\nPROCESSING...")
        print("-" * 70)

        return process_metric_request(
            "surge",
            airport_code,
        )

    # --------------------------------------------------------
    # GENERAL AIRPORT METRICS
    # --------------------------------------------------------

    if intent == "airport_metrics":

        if not airport_code:
            airport_code = get_last_airport()

        if not airport_code:

            update_memory(
                pending_intent="airport_metrics",
                pending_details={},
            )

            return (
                "Which airport would you like the "
                "metrics for? "
                "Please provide SFO, LAX, or JFK."
            )

        print("\nPROCESSING...")
        print("-" * 70)

        return process_metric_request(
            "airport_metrics",
            airport_code,
        )

    # --------------------------------------------------------
    # INCENTIVE
    # --------------------------------------------------------

    if intent == "incentive":

        driver_count = extract_driver_count(
            text
        )

        severity = extract_severity(
            text
        )

        print("\nPROCESSING...")
        print("-" * 70)

        return process_incentive(
            driver_count,
            severity,
        )

    # --------------------------------------------------------
    # SURGE OVERRIDE
    # --------------------------------------------------------

    if intent == "surge_override":

        if not airport_code:
            airport_code = get_last_airport()

        multiplier = extract_multiplier(
            text
        )

        reason = None

        lower_text = text.lower()

        if "because of" in lower_text:
            reason = text.lower().split(
                "because of",
                1,
            )[1].strip()

        elif "due to" in lower_text:
            reason = text.lower().split(
                "due to",
                1,
            )[1].strip()

        if not airport_code:

            update_memory(
                pending_intent="surge_override",
                pending_details={
                    "multiplier": multiplier,
                    "reason": reason,
                },
            )

            return (
                "Which airport should I apply the "
                "surge override to? "
                "Please provide SFO, LAX, or JFK."
            )

        if multiplier is None:

            update_memory(
                pending_intent="surge_override",
                pending_details={
                    "airport_code": airport_code,
                    "reason": reason,
                },
            )

            return (
                "What surge multiplier would you "
                "like to set?"
            )

        print("\nPROCESSING...")
        print("-" * 70)

        update_memory(
            airport=airport_code
        )

        return process_surge_override(
            airport_code=airport_code,
            multiplier=multiplier,
            reason=reason,
        )

    # --------------------------------------------------------
    # INVESTIGATION
    # --------------------------------------------------------

    if intent == "investigate":

        if not airport_code:
            airport_code = get_last_airport()

        if not airport_code:

            update_memory(
                pending_intent="investigate",
                pending_details={},
            )

            return (
                "Which airport would you like me "
                "to investigate? "
                "Please provide SFO, LAX, or JFK."
            )

        print("\nPROCESSING...")
        print("-" * 70)

        update_memory(
            airport=airport_code
        )

        return process_investigation(
            airport_code,
            text,
        )

    # --------------------------------------------------------
    # UNKNOWN
    # --------------------------------------------------------

    return (
        "I can help with airport metrics, completion rate, "
        "surge multipliers, driver incentives, operational "
        "investigations, policy checks, and surge overrides.\n\n"
        "Examples:\n"
        "- What is the completion rate at SFO?\n"
        "- What about its surge?\n"
        "- Calculate an incentive for 40 drivers at HIGH severity.\n"
        "- Investigate SFO.\n"
        "- Can we increase surge at JFK to 1.3x?"
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
    print(f"ReAct iterations: {MAX_ITERATIONS}")
    print("=" * 70)
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 70)

    while True:

        try:
            user_input = input("\nUSER: ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if not user_input:
            continue

        if user_input.lower() in {
            "exit",
            "quit",
        }:
            print("Exiting...")
            break

        try:
            answer = process_request(
                user_input
            )

            if answer is not None:
                print("\nFINAL ANSWER")
                print("-" * 70)
                print(answer)

        except Exception as e:
            print("\nERROR:")
            print(str(e))


if __name__ == "__main__":
    main()