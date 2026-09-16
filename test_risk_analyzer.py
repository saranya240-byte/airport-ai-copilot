from src.risk_analyzer import RiskAnalyzer


DATA_PATH = "data/airport_operations.csv"


# ==================================================
# INITIALIZE
# ==================================================

print("\nINITIALIZING RISK ANALYZER")
print("=" * 60)

analyzer = RiskAnalyzer(DATA_PATH)

print("Risk analyzer initialized successfully.")


# ==================================================
# SFO RISK
# ==================================================

print("\nSFO OVERALL RISK")
print("=" * 60)

sfo_risk = analyzer.overall_risk("SFO")

print("Airport:", sfo_risk["airport"])
print("Risk Score:", sfo_risk["risk_score"])
print("Risk Level:", sfo_risk["risk_level"])

print("Main Reasons:")

for reason in sfo_risk["reasons"]:
    print("-", reason)


# ==================================================
# LAX RISK
# ==================================================

print("\nLAX OVERALL RISK")
print("=" * 60)

lax_risk = analyzer.overall_risk("LAX")

print("Airport:", lax_risk["airport"])
print("Risk Score:", lax_risk["risk_score"])
print("Risk Level:", lax_risk["risk_level"])

print("Main Reasons:")

for reason in lax_risk["reasons"]:
    print("-", reason)


# ==================================================
# JFK RISK
# ==================================================

print("\nJFK OVERALL RISK")
print("=" * 60)

jfk_risk = analyzer.overall_risk("JFK")

print("Airport:", jfk_risk["airport"])
print("Risk Score:", jfk_risk["risk_score"])
print("Risk Level:", jfk_risk["risk_level"])

print("Main Reasons:")

for reason in jfk_risk["reasons"]:
    print("-", reason)


# ==================================================
# AIRPORT COMPARISON
# ==================================================

print("\nAIRPORT RISK COMPARISON")
print("=" * 60)

comparison = analyzer.compare_airports()

for result in comparison:

    print(
        f"{result['airport']} | "
        f"Score: {result['risk_score']} | "
        f"Risk: {result['risk_level']}"
    )
