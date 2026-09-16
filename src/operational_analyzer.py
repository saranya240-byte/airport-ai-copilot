import pandas as pd


class OperationalAnalyzer:

    def __init__(self, data_path):
        """
        Load airport operational data from CSV.
        """

        self.data_path = data_path

        self.df = pd.read_csv(
            data_path,
            parse_dates=["timestamp"]
        )

    # ==================================================
    # DATASET SUMMARY
    # ==================================================

    def summary(self):
        """
        Return basic information about the dataset.
        """

        return {
            "rows": len(self.df),
            "airports": sorted(
                self.df["airport"].unique().tolist()
            ),
            "columns": self.df.columns.tolist()
        }

    # ==================================================
    # AIRPORT DATA
    # ==================================================

    def get_airport_data(self, airport):
        """
        Return operational records for a specific airport.
        """

        return self.df[
            self.df["airport"].str.upper()
            == airport.upper()
        ].copy()

    # ==================================================
    # KPI CALCULATION
    # ==================================================

    def calculate_kpis(self, airport):
        """
        Calculate operational KPIs for an airport.
        """

        data = self.get_airport_data(airport)

        if data.empty:
            return {}

        return {
            "airport": airport.upper(),

            "average_queue_size": round(
                data["queue_size"].mean(),
                2
            ),

            "average_active_drivers": round(
                data["active_drivers"].mean(),
                2
            ),

            "average_request_volume": round(
                data["request_volume"].mean(),
                2
            ),

            "total_completed_trips": int(
                data["completed_trips"].sum()
            ),

            "average_completion_rate": round(
                data["completion_rate"].mean(),
                3
            ),

            "average_eta_minutes": round(
                data["average_eta_minutes"].mean(),
                2
            ),

            "average_passenger_wait_time": round(
                data["passenger_wait_time_minutes"].mean(),
                2
            ),

            "average_driver_cancellation_rate": round(
                data["driver_cancellation_rate"].mean(),
                3
            ),

            "maximum_surge_multiplier": round(
                data["surge_multiplier"].max(),
                1
            )
        }

    # ==================================================
    # DEMAND PRESSURE
    # ==================================================

    def calculate_demand_pressure(self, airport):
        """
        Calculate demand pressure.

        Demand Pressure =
        Request Volume / Active Drivers
        """

        data = self.get_airport_data(airport)

        if data.empty:
            return None

        # Avoid division by zero
        data = data[
            data["active_drivers"] > 0
        ].copy()

        if data.empty:
            return None

        data["demand_pressure"] = (
            data["request_volume"]
            / data["active_drivers"]
        )

        return round(
            data["demand_pressure"].mean(),
            2
        )

    # ==================================================
    # OPERATIONAL ISSUE DETECTION
    # ==================================================

    def detect_issues(self, airport):
        """
        Detect operational issues based on
        predefined KPI thresholds.
        """

        data = self.get_airport_data(airport)

        if data.empty:
            return []

        issues = []

        for _, row in data.iterrows():

            timestamp = row["timestamp"]

            # ------------------------------------------
            # Low Completion Rate
            # ------------------------------------------

            if row["completion_rate"] < 0.80:

                issues.append({
                    "timestamp": str(timestamp),
                    "airport": airport.upper(),
                    "issue": "Low completion rate",
                    "value": row["completion_rate"],
                    "severity": "HIGH"
                })

            # ------------------------------------------
            # High Driver Cancellation Rate
            # ------------------------------------------

            if row["driver_cancellation_rate"] > 0.15:

                issues.append({
                    "timestamp": str(timestamp),
                    "airport": airport.upper(),
                    "issue": "High driver cancellation rate",
                    "value": row[
                        "driver_cancellation_rate"
                    ],
                    "severity": "HIGH"
                })

            # ------------------------------------------
            # High ETA
            # ------------------------------------------

            if row["average_eta_minutes"] > 20:

                issues.append({
                    "timestamp": str(timestamp),
                    "airport": airport.upper(),
                    "issue": "High average ETA",
                    "value": row[
                        "average_eta_minutes"
                    ],
                    "severity": "HIGH"
                })

            # ------------------------------------------
            # Large Queue
            # ------------------------------------------

            if row["queue_size"] > 100:

                issues.append({
                    "timestamp": str(timestamp),
                    "airport": airport.upper(),
                    "issue": "Large driver queue",
                    "value": row["queue_size"],
                    "severity": "MEDIUM"
                })

            # ------------------------------------------
            # High Passenger Wait Time
            # ------------------------------------------

            if row["passenger_wait_time_minutes"] > 12:

                issues.append({
                    "timestamp": str(timestamp),
                    "airport": airport.upper(),
                    "issue": "High passenger wait time",
                    "value": row[
                        "passenger_wait_time_minutes"
                    ],
                    "severity": "HIGH"
                })

        return issues

    # ==================================================
    # COMPLETE OPERATIONAL SUMMARY
    # ==================================================

    def generate_summary(self, airport):
        """
        Generate a complete operational summary
        for an airport.
        """

        kpis = self.calculate_kpis(airport)

        if not kpis:
            return {
                "airport": airport.upper(),
                "message": "No operational data found."
            }

        demand_pressure = (
            self.calculate_demand_pressure(airport)
        )

        issues = self.detect_issues(airport)

        return {
            "airport": airport.upper(),
            "kpis": kpis,
            "demand_pressure": demand_pressure,
            "issue_count": len(issues),
            "issues": issues
        }


# ======================================================
# DIRECT TEST
# ======================================================

if __name__ == "__main__":

    DATA_PATH = "data/airport_operations.csv"

    analyzer = OperationalAnalyzer(DATA_PATH)

    print("\nAIRPORT OPERATIONAL ANALYZER")
    print("=" * 60)

    print("\nDataset Summary")
    print("-" * 60)

    summary = analyzer.summary()

    print("Rows:", summary["rows"])
    print("Airports:", summary["airports"])

    for airport in summary["airports"]:

        print(f"\n{airport} KPIs")
        print("-" * 60)

        kpis = analyzer.calculate_kpis(airport)

        for key, value in kpis.items():
            print(f"{key}: {value}")

        print(
            "Demand Pressure:",
            analyzer.calculate_demand_pressure(airport)
        )

        issues = analyzer.detect_issues(airport)

        print(
            "Operational Issues:",
            len(issues)
        )