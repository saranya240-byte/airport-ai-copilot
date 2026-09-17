import pandas as pd


DATA_PATH = "data/airport_operations.csv"

VALID_AIRPORTS = {"SFO", "LAX", "JFK"}


# ============================================================
# LOAD DATA
# ============================================================

def load_operational_data():
    """
    Load airport operational telemetry.
    """

    try:
        data = pd.read_csv(DATA_PATH)

        required_columns = {
            "timestamp",
            "airport",
            "queue_size",
            "active_drivers",
            "request_volume",
            "completion_rate",
            "average_eta_minutes",
            "passenger_wait_time_minutes",
            "driver_cancellation_rate",
            "surge_multiplier",
        }

        missing_columns = required_columns - set(data.columns)

        if missing_columns:
            return {
                "success": False,
                "error": (
                    "Dataset is missing required columns: "
                    + ", ".join(sorted(missing_columns))
                ),
            }

        return {
            "success": True,
            "data": data,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to load operational data: {str(e)}",
        }


# ============================================================
# TOOL 1 — AIRPORT METRICS
# ============================================================

def get_airport_metrics(airport_code):
    """
    Return operational metrics for an airport.
    """

    if not airport_code:
        return {
            "success": False,
            "error": "airport_code is required.",
        }

    airport_code = airport_code.upper().strip()

    if airport_code not in VALID_AIRPORTS:
        return {
            "success": False,
            "error": (
                f"Invalid airport code '{airport_code}'. "
                "Valid airports are SFO, LAX, and JFK."
            ),
        }

    result = load_operational_data()

    if not result["success"]:
        return result

    data = result["data"]

    airport_data = data[
        data["airport"].str.upper() == airport_code
    ]

    if airport_data.empty:
        return {
            "success": False,
            "error": f"No operational data found for {airport_code}.",
        }

    try:
        latest = airport_data.sort_values(
            "timestamp"
        ).iloc[-1]

        return {
            "success": True,
            "tool": "get_airport_metrics",
            "airport_code": airport_code,
            "metrics": {
                "completion_rate": round(
                    float(latest["completion_rate"]), 3
                ),
                "average_eta_minutes": round(
                    float(latest["average_eta_minutes"]), 2
                ),
                "active_drivers": int(
                    latest["active_drivers"]
                ),
                "driver_cancellation_rate": round(
                    float(
                        latest[
                            "driver_cancellation_rate"
                        ]
                    ),
                    3,
                ),
                "queue_size": int(
                    latest["queue_size"]
                ),
                "surge_multiplier": round(
                    float(latest["surge_multiplier"]),
                    2,
                ),
                "request_volume": int(
                    latest["request_volume"]
                ),
                "timestamp": str(
                    latest["timestamp"]
                ),
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": (
                f"Failed to calculate airport metrics: {str(e)}"
            ),
        }


# ============================================================
# TOOL 2 — DRIVER INCENTIVE CALCULATOR
# ============================================================

def calculate_driver_incentive(
    driver_count,
    severity_level,
):
    """
    Calculate a recommended driver incentive.
    """

    if driver_count is None:
        return {
            "success": False,
            "error": "driver_count is required.",
        }

    if severity_level is None:
        return {
            "success": False,
            "error": "severity_level is required.",
        }

    try:
        driver_count = int(driver_count)

    except (TypeError, ValueError):
        return {
            "success": False,
            "error": "driver_count must be an integer.",
        }

    if driver_count <= 0:
        return {
            "success": False,
            "error": "driver_count must be greater than zero.",
        }

    severity_level = str(
        severity_level
    ).upper().strip()

    incentive_rates = {
        "LOW": 5.0,
        "MEDIUM": 10.0,
        "HIGH": 20.0,
    }

    if severity_level not in incentive_rates:
        return {
            "success": False,
            "error": (
                f"Invalid severity_level '{severity_level}'. "
                "Use LOW, MEDIUM, or HIGH."
            ),
        }

    incentive_per_driver = incentive_rates[
        severity_level
    ]

    estimated_total_cost = (
        driver_count * incentive_per_driver
    )

    return {
        "success": True,
        "tool": "calculate_driver_incentive",
        "driver_count": driver_count,
        "severity_level": severity_level,
        "recommended_incentive_per_driver": (
            incentive_per_driver
        ),
        "estimated_total_cost": (
            estimated_total_cost
        ),
    }


# ============================================================
# TOOL 3 — SURGE OVERRIDE
# ============================================================

def trigger_surge_override(
    airport_code,
    new_multiplier,
    reason,
):
    """
    Mock surge override execution.

    Day 2 only performs a mock execution.
    Approval controls will be implemented on Day 4.
    """

    if not airport_code:
        return {
            "success": False,
            "error": "airport_code is required.",
        }

    if new_multiplier is None:
        return {
            "success": False,
            "error": "new_multiplier is required.",
        }

    if not reason:
        return {
            "success": False,
            "error": "reason is required.",
        }

    airport_code = airport_code.upper().strip()

    if airport_code not in VALID_AIRPORTS:
        return {
            "success": False,
            "error": (
                f"Invalid airport code '{airport_code}'. "
                "Valid airports are SFO, LAX, and JFK."
            ),
        }

    try:
        new_multiplier = float(new_multiplier)

    except (TypeError, ValueError):
        return {
            "success": False,
            "error": "new_multiplier must be a number.",
        }

    if new_multiplier <= 0:
        return {
            "success": False,
            "error": (
                "new_multiplier must be greater than zero."
            ),
        }

    return {
        "success": True,
        "tool": "trigger_surge_override",
        "execution": "MOCK",
        "airport_code": airport_code,
        "new_multiplier": new_multiplier,
        "reason": reason,
        "status": "SURGE_OVERRIDE_TRIGGERED",
        "message": (
            "Mock surge override executed successfully. "
            "Approval controls will be applied in Day 4."
        ),
    }


# ============================================================
# OLLAMA TOOL DEFINITIONS
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_airport_metrics",
            "description": (
                "Retrieve current operational metrics "
                "for a specific airport."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_code": {
                        "type": "string",
                        "description": (
                            "Airport code such as SFO, LAX, or JFK."
                        ),
                    }
                },
                "required": [
                    "airport_code"
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_driver_incentive",
            "description": (
                "Calculate the recommended driver incentive "
                "for a given number of drivers and severity."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "driver_count": {
                        "type": "integer",
                        "description": (
                            "Number of drivers."
                        ),
                    },
                    "severity_level": {
                        "type": "string",
                        "enum": [
                            "LOW",
                            "MEDIUM",
                            "HIGH",
                        ],
                        "description": (
                            "Operational severity level."
                        ),
                    },
                },
                "required": [
                    "driver_count",
                    "severity_level",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trigger_surge_override",
            "description": (
                "Trigger a mock surge override "
                "for a specific airport."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "airport_code": {
                        "type": "string",
                        "description": (
                            "Airport code such as SFO, LAX, or JFK."
                        ),
                    },
                    "new_multiplier": {
                        "type": "number",
                        "description": (
                            "New surge multiplier."
                        ),
                    },
                    "reason": {
                        "type": "string",
                        "description": (
                            "Reason for the surge override."
                        ),
                    },
                },
                "required": [
                    "airport_code",
                    "new_multiplier",
                    "reason",
                ],
            },
        },
    },
]


# ============================================================
# TOOL DISPATCHER
# ============================================================

def execute_tool(tool_name, arguments):
    """
    Execute a tool using its name and arguments.
    """

    if tool_name == "get_airport_metrics":

        return get_airport_metrics(
            arguments.get("airport_code")
        )

    if tool_name == "calculate_driver_incentive":

        return calculate_driver_incentive(
            arguments.get("driver_count"),
            arguments.get("severity_level"),
        )

    if tool_name == "trigger_surge_override":

        return trigger_surge_override(
            arguments.get("airport_code"),
            arguments.get("new_multiplier"),
            arguments.get("reason"),
        )

    return {
        "success": False,
        "error": f"Unknown tool '{tool_name}'.",
    }