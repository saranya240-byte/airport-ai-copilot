import pandas as pd


class OperationalAnalyzer:

    def __init__(self, data_path):

        self.data_path = data_path

        self.df = pd.read_csv(
            data_path,
            parse_dates=["timestamp"]
        )

    # ------------------------------------------
    # Basic dataset information
    # ------------------------------------------

    def summary(self):

        return {
            "rows": len(self.df),
            "airports": self.df["airport"].unique().tolist(),
            "columns": self.df.columns.tolist()
        }

    # ------------------------------------------
    # Filter by airport
    # ------------------------------------------

    def get_airport_data(self, airport):

        return self.df[
            self.df["airport"] == airport
        ].copy()

    # ------------------------------------------
    # Calculate average KPIs
    # ------------------------------------------

    def calculate_kpis(self, airport):

        data = self.get_airport_data(airport)

        if data.empty:
            return {}

        return {
            "airport": airport,

            "average_queue_size":
                round(data["queue_size"].mean(), 2),

            "average_active_drivers":
                round(data["active_drivers"].mean(), 2),

            "average_request_volume":
                round(data["request_volume"].mean(), 2),

            "average_completion_rate":
                round(data["completion_rate"].mean(), 4),

            "average_eta":
                round(data["average_eta"].mean(), 2),

            "average_driver_cancellation_rate":
                round(
                    data[
                        "driver_cancellation_rate"
                    ].mean(),
                    4
                ),

            "maximum_surge_multiplier":
                data["surge_multiplier"].max()
        }

    # ------------------------------------------
    # Identify operational issues
    # ------------------------------------------

    def detect_issues(self, airport):

        data = self.get_airport_data(airport)

        issues = []

        for _, row in data.iterrows():

            if row["completion_rate"] < 0.80:

                issues.append({
                    "timestamp": row["timestamp"],
                    "airport": airport,
                    "issue": "Low completion rate",
                    "value": row["completion_rate"]
                })

            if row["driver_cancellation_rate"] > 0.15:

                issues.append({
                    "timestamp": row["timestamp"],
                    "airport": airport,
                    "issue": "High driver cancellation rate",
                    "value": row[
                        "driver_cancellation_rate"
                    ]
                })

            if row["average_eta"] > 20:

                issues.append({
                    "timestamp": row["timestamp"],
                    "airport": airport,
                    "issue": "High average ETA",
                    "value": row["average_eta"]
                })

            if row["queue_size"] > 100:

                issues.append({
                    "timestamp": row["timestamp"],
                    "airport": airport,
                    "issue": "Large driver queue",
                    "value": row["queue_size"]
                })

        return issues
