from src.tools import (
    get_airport_metrics,
    calculate_driver_incentive,
    trigger_surge_override,
)


# ============================================================
# TOOL 1 — AIRPORT METRICS
# ============================================================

print("\n" + "=" * 60)
print("TOOL 1 — AIRPORT METRICS")
print("=" * 60)

result = get_airport_metrics("SFO")

print(result)


# ============================================================
# TOOL 2 — DRIVER INCENTIVE
# ============================================================

print("\n" + "=" * 60)
print("TOOL 2 — DRIVER INCENTIVE CALCULATOR")
print("=" * 60)

result = calculate_driver_incentive(
    driver_count=50,
    severity_level="HIGH",
)

print(result)


# ============================================================
# TOOL 3 — SURGE OVERRIDE
# ============================================================

print("\n" + "=" * 60)
print("TOOL 3 — SURGE OVERRIDE")
print("=" * 60)

result = trigger_surge_override(
    airport_code="SFO",
    new_multiplier=1.4,
    reason="High passenger demand and low driver availability",
)

print(result)


# ============================================================
# ERROR HANDLING
# ============================================================

print("\n" + "=" * 60)
print("ERROR HANDLING")
print("=" * 60)


print("\nInvalid airport:")
print(get_airport_metrics("ABC"))


print("\nMissing airport:")
print(get_airport_metrics(""))


print("\nInvalid severity:")
print(
    calculate_driver_incentive(
        driver_count=50,
        severity_level="CRITICAL",
    )
)


print("\nInvalid driver count:")
print(
    calculate_driver_incentive(
        driver_count=-5,
        severity_level="HIGH",
    )
)


print("\nInvalid surge multiplier:")
print(
    trigger_surge_override(
        airport_code="SFO",
        new_multiplier=-1,
        reason="Testing error handling",
    )
)


print("\nMissing reason:")
print(
    trigger_surge_override(
        airport_code="SFO",
        new_multiplier=1.4,
        reason="",
    )
)
