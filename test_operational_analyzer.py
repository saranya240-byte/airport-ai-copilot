from src.operational_analyzer import OperationalAnalyzer


analyzer = OperationalAnalyzer(
    "data/airport_operations.csv"
)


# ------------------------------------------
# Dataset Summary
# ------------------------------------------

print("\nDATASET SUMMARY")
print("=" * 60)

print(
    analyzer.summary()
)


# ------------------------------------------
# SFO KPIs
# ------------------------------------------

print("\nSFO KPIs")
print("=" * 60)

kpis = analyzer.calculate_kpis("SFO")

for key, value in kpis.items():

    print(
        f"{key}: {value}"
    )


# ------------------------------------------
# SFO Operational Issues
# ------------------------------------------

print("\nSFO OPERATIONAL ISSUES")
print("=" * 60)

issues = analyzer.detect_issues("SFO")

for issue in issues:

    print(issue)
