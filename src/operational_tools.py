from src.operational_analyzer import OperationalAnalyzer
from src.risk_analyzer import RiskAnalyzer


DATA_PATH = "data/airport_operations.csv"


# Initialize analyzers once
operational_analyzer = OperationalAnalyzer(DATA_PATH)
risk_analyzer = RiskAnalyzer(DATA_PATH)


def get_airport_kpis(airport):
    """
    Return operational KPIs for an airport.
    """

    return operational_analyzer.calculate_kpis(
        airport
    )


def get_airport_issues(airport):
    """
    Return detected operational issues
    for an airport.
    """

    return operational_analyzer.detect_issues(
        airport
    )


def get_airport_risk(airport):
    """
    Return the overall operational risk
    for an airport.
    """

    return risk_analyzer.overall_risk(
        airport
    )


def get_airport_operational_status(airport):
    """
    Return a combined operational view containing:

    - KPIs
    - Demand pressure
    - Operational issues
    - Risk score
    - Risk level
    - Risk reasons
    """

    kpis = operational_analyzer.calculate_kpis(
        airport
    )

    demand_pressure = (
        operational_analyzer.calculate_demand_pressure(
            airport
        )
    )

    issues = operational_analyzer.detect_issues(
        airport
    )

    risk = risk_analyzer.overall_risk(
        airport
    )

    return {
        "airport": airport.upper(),
        "kpis": kpis,
        "demand_pressure": demand_pressure,
        "issues": issues,
        "risk": risk
    }
