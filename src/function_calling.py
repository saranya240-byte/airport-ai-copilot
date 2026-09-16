import re
import json

from src.tools import (
    get_airport_metrics,
    calculate_driver_incentive,
    trigger_surge_override,
)


# ============================================================
# AIRPORT OPERATIONS AI COPILOT
# DAY 2 - FUNCTION CALLING
# ============================================================

VALID_AIRPORTS = {"SFO", "LAX", "JFK"}


# ------------------------------------------------------------
# PENDING QUESTION STATE
# ------------------------------------------------------------

pending_question = None


# ------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------

def normalize_text(text):
    """Normalize user input."""
    return " ".join(text.strip().split())


def extract_airport(text):
    """
    Extract SFO, LAX, or JFK from user input.
    """
    text_upper = text.upper()

    for airport in VALID_AIRPORTS:
        if re.search(rf"\b{airport}\b", text_upper):
            return airport

    return None


def extract_driver_count(text):
    """
    Extract number of drivers from the user input.
    """

    patterns = [
        r"\b(\d+)\s+drivers?\b",
        r"\bfor\s+(\d+)\b",
        r"\b(\d+)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass

    return None


def extract_severity(text):
    """
    Extract LOW, MEDIUM, or HIGH severity.
    """

    text_upper = text.upper()

    for severity in ["HIGH", "MEDIUM", "LOW"]:
        if re.search(rf"\b{severity}\b", text_upper):
            return severity

    return None


def extract_multiplier(text):
    """
    Extract surge multiplier correctly.

    Examples:
        1.3x
        1.3 x
        1.3
        to 1.4x
    """

    patterns = [
        r"\b(\d+(?:\.\d+)?)\s*x\b",
        r"\bto\s+(\d+(?:\.\d+)?)\b",
        r"\bmultiplier\s+(?:of\s+)?(\d+(?:\.\d+)?)\b",
        r"\b(\d+\.\d+)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass

    return None


def extract_reason(text):
    """
    Extract the reason for surge override.
    """

    patterns = [
        r"because of\s+(.+?)(?:\.|$)",
        r"due to\s+(.+?)(?:\.|$)",
        r"reason(?:\s+is)?\s+(.+?)(?:\.|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            reason = match.group(1).strip()

            if reason:
                return reason.rstrip(".")

    return "operational demand"


# ------------------------------------------------------------
# METRIC RESPONSE
# ------------------------------------------------------------

def format_metric_response(airport, result, requested_metric=None):
    """
    Format airport metric response.
    """

    if not result.get("success"):
        return f"Error: {result.get('error', 'Unknown error.')}"

    metrics = result.get("metrics", {})

    if not metrics:
        return "No airport metrics were returned."

    if requested_metric == "completion_rate":
        value = metrics.get("completion_rate")

        if value is not None:
            return (
                f"The completion rate at {airport} is "
                f"{value * 100:.1f}%."
            )

    if requested_metric == "active_drivers":
        value = metrics.get("active_drivers")

        if value is not None:
            return (
                f"There are {value} active drivers at {airport}."
            )

    if requested_metric == "queue_size":
        value = metrics.get("queue_size")

        if value is not None:
            return (
                f"The queue size at {airport} is {value}."
            )

    if requested_metric == "average_eta":
        value = metrics.get("average_eta_minutes")

        if value is not None:
            return (
                f"The average ETA at {airport} is "
                f"{value} minutes."
            )

    if requested_metric == "cancellation_rate":
        value = metrics.get("driver_cancellation_rate")

        if value is not None:
            return (
                f"The driver cancellation rate at {airport} is "
                f"{value * 100:.1f}%."
            )

    if requested_metric == "surge_multiplier":
        value = metrics.get("surge_multiplier")

        if value is not None:
            return (
                f"The current surge multiplier at {airport} is "
                f"{value}x."
            )

    # Generic metric response
    return (
        f"At {airport}, the completion rate is "
        f"{metrics.get('completion_rate', 0) * 100:.1f}%, "
        f"the average ETA is "
        f"{metrics.get('average_eta_minutes', 0)} minutes, "
        f"there are "
        f"{metrics.get('active_drivers', 0)} active drivers, "
        f"the driver cancellation rate is "
        f"{metrics.get('driver_cancellation_rate', 0) * 100:.1f}%, "
        f"the queue size is "
        f"{metrics.get('queue_size', 0)}, "
        f"the surge multiplier is "
        f"{metrics.get('surge_multiplier', 0)}x, "
        f"and the request volume is "
        f"{metrics.get('request_volume', 0)}."
    )


# ------------------------------------------------------------
# IDENTIFY REQUESTED METRIC
# ------------------------------------------------------------

def identify_metric(text):
    """
    Identify which airport metric the user wants.
    """

    text_lower = text.lower()

    if (
        "completion rate" in text_lower
        or "completion" in text_lower
    ):
        return "completion_rate"

    if (
        "active drivers" in text_lower
        or "how many drivers" in text_lower
        or "number of drivers" in text_lower
        or "drivers are at" in text_lower
    ):
        return "active_drivers"

    if (
        "queue size" in text_lower
        or "queue" in text_lower
    ):
        return "queue_size"

    if (
        "average eta" in text_lower
        or "eta" in text_lower
    ):
        return "average_eta"

    if (
        "cancellation rate" in text_lower
        or "cancellation" in text_lower
    ):
        return "cancellation_rate"

    if (
        "surge multiplier" in text_lower
        or "current surge" in text_lower
    ):
        return "surge_multiplier"

    return None


# ------------------------------------------------------------
# TOOL EXECUTION DISPLAY
# ------------------------------------------------------------

def execute_and_display(tool_name, arguments, function):
    """
    Execute a tool and display the result.
    """

    print()
    print(f"TOOL SELECTED: {tool_name}")
    print(f"TOOL ARGUMENTS: {arguments}")

    try:
        result = function(**arguments)
    except Exception as e:
        result = {
            "success": False,
            "error": str(e),
        }

    print(f"TOOL RESULT: {result}")

    return result


# ------------------------------------------------------------
# MAIN REQUEST HANDLER
# ------------------------------------------------------------

def handle_request(user_input):
    """
    Deterministic intent router.

    This prevents the LLM from inventing tool arguments.
    """

    global pending_question

    text = normalize_text(user_input)

    if not text:
        return ""

    text_lower = text.lower()

    # ========================================================
    # EXIT
    # ========================================================

    if text_lower in {"exit", "quit"}:
        return "__EXIT__"

    # ========================================================
    # HANDLE AIRPORT FOLLOW-UP
    # Example:
    #
    # User: What is the completion rate?
    # Assistant: Which airport?
    # User: SFO
    # ========================================================

    if pending_question is not None:
        airport = extract_airport(text)

        if airport:
            question = pending_question
            pending_question = None

            requested_metric = identify_metric(question)

            arguments = {
                "airport_code": airport
            }

            result = execute_and_display(
                "get_airport_metrics",
                arguments,
                get_airport_metrics,
            )

            return format_metric_response(
                airport,
                result,
                requested_metric,
            )

        # If user enters something other than an airport,
        # keep the pending question.
        return (
            "Please provide a valid airport code: "
            "SFO, LAX, or JFK."
        )

    # ========================================================
    # GREETINGS
    # ========================================================

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
        return (
            "Hello! How can I help you with airport operations today?"
        )

    # ========================================================
    # COPILOT DESCRIPTION
    # ========================================================

    if (
        "what does an airport operations ai copilot do" in text_lower
        or "what is an airport operations ai copilot" in text_lower
        or "what does the ai copilot do" in text_lower
        or "what can the ai copilot do" in text_lower
    ):
        return (
            "An Airport Operations AI Copilot helps airport "
            "operations teams monitor performance and make "
            "operational decisions. In this project, it can "
            "retrieve airport metrics, calculate driver "
            "incentives, and trigger mock surge overrides "
            "for SFO, LAX, and JFK."
        )

    # ========================================================
    # DRIVER INCENTIVE
    # ========================================================

    if (
        "incentive" in text_lower
        or "incentives" in text_lower
    ):
        driver_count = extract_driver_count(text)
        severity = extract_severity(text)

        if driver_count is None:
            return (
                "Please provide the number of drivers. "
                "For example: Calculate an incentive for "
                "40 drivers at high severity."
            )

        if severity is None:
            return (
                "Please provide the severity level: "
                "LOW, MEDIUM, or HIGH."
            )

        arguments = {
            "driver_count": driver_count,
            "severity_level": severity,
        }

        result = execute_and_display(
            "calculate_driver_incentive",
            arguments,
            calculate_driver_incentive,
        )

        if not result.get("success"):
            return f"Error: {result.get('error')}"

        per_driver = result.get(
            "recommended_incentive_per_driver"
        )

        total_cost = result.get(
            "estimated_total_cost"
        )

        return (
            f"The recommended incentive is "
            f"${per_driver:.2f} per driver for "
            f"{driver_count} drivers at {severity} severity. "
            f"The estimated total cost is "
            f"${total_cost:.2f}."
        )

    # ========================================================
    # SURGE OVERRIDE
    # ========================================================

    if (
        "surge" in text_lower
        or "multiplier" in text_lower
        or "override" in text_lower
    ):
        airport = extract_airport(text)
        multiplier = extract_multiplier(text)

        if airport is None:
            return (
                "Please provide an airport code: "
                "SFO, LAX, or JFK."
            )

        if multiplier is None:
            return (
                "Please provide the surge multiplier. "
                "For example: 1.3x."
            )

        reason = extract_reason(text)

        arguments = {
            "airport_code": airport,
            "new_multiplier": multiplier,
            "reason": reason,
        }

        result = execute_and_display(
            "trigger_surge_override",
            arguments,
            trigger_surge_override,
        )

        if not result.get("success"):
            return f"Error: {result.get('error')}"

        return (
            f"The mock surge override has been triggered "
            f"at {airport} with a multiplier of "
            f"{multiplier}x because of {reason}. "
            f"Status: {result.get('status')}."
        )

    # ========================================================
    # AIRPORT METRICS
    # ========================================================

    metric = identify_metric(text)

    if metric is not None:
        airport = extract_airport(text)

        if airport is None:
            pending_question = text

            return (
                "Which airport would you like the metrics for? "
                "Please provide SFO, LAX, or JFK."
            )

        arguments = {
            "airport_code": airport
        }

        result = execute_and_display(
            "get_airport_metrics",
            arguments,
            get_airport_metrics,
        )

        return format_metric_response(
            airport,
            result,
            metric,
        )

    # ========================================================
    # GENERAL AIRPORT QUESTION
    # ========================================================

    if (
        "airport" in text_lower
        or "operations" in text_lower
        or "operational" in text_lower
    ):
        return (
            "I can help with airport operations metrics, "
            "driver incentives, and mock surge overrides. "
            "Available airports are SFO, LAX, and JFK."
        )

    # ========================================================
    # UNKNOWN REQUEST
    # ========================================================

    return (
        "I can help with airport metrics, driver incentives, "
        "and mock surge overrides. "
        "Try asking something like:\n\n"
        "- What is the completion rate at SFO?\n"
        "- How many drivers are at LAX?\n"
        "- What is the queue size at JFK?\n"
        "- Calculate an incentive for 40 drivers at high severity.\n"
        "- Trigger a surge override at JFK to 1.3x because of high passenger demand."
    )


# ------------------------------------------------------------
# MAIN CLI
# ------------------------------------------------------------

def main():

    print("=" * 70)
    print("AIRPORT OPERATIONS AI COPILOT")
    print("=" * 70)
    print("Type your question below.")
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

        print("\nPROCESSING...")
        print("-" * 70)

        try:
            answer = handle_request(user_input)

            if answer == "__EXIT__":
                print("Exiting...")
                break

            print("\nFINAL ANSWER")
            print("-" * 70)
            print(answer)

        except Exception as e:
            print("\nERROR:")
            print(str(e))


if __name__ == "__main__":
    main()