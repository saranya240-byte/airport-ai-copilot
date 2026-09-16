from src.operational_tools import (
    get_airport_kpis,
    get_airport_issues,
    get_airport_risk,
    get_airport_operational_status
)


print("\nAIRPORT OPERATIONAL TOOLS")
print("=" * 60)


# ==================================================
# KPI TOOL
# ==================================================

print("\n1. SFO KPIs")
print("-" * 60)

kpis = get_airport_kpis("SFO")

for key, value in kpis.items():
    print(f"{key}: {value}")


# ==================================================
# ISSUE TOOL
# ==================================================

print("\n2. SFO OPERATIONAL ISSUES")
print("-" * 60)

issues = get_airport_issues("SFO")

print("Issues detected:", len(issues))

for issue in issues[:5]:

    print(
        issue["issue"],
        "|",
        issue["severity"],
        "|",
        issue["value"]
    )


# ==================================================
# RISK TOOL
# ==================================================

print("\n3. SFO RISK")
print("-" * 60)

risk = get_airport_risk("SFO")

print("Risk Score:", risk["risk_score"])
print("Risk Level:", risk["risk_level"])

for reason in risk["reasons"]:
    print("-", reason)


# ==================================================
# COMBINED OPERATIONAL STATUS
# ==================================================

print("\n4. COMPLETE SFO OPERATIONAL STATUS")
print("-" * 60)

status = get_airport_operational_status("SFO")

print("Airport:", status["airport"])

print(
    "Demand Pressure:",
    status["demand_pressure"]
)

print(
    "Risk Level:",
    status["risk"]["risk_level"]
)

print(
    "Risk Score:",
    status["risk"]["risk_score"]
)

print(
    "Number of Issues:",
    len(status["issues"])
)
