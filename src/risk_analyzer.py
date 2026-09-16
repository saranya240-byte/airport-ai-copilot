import pandas as pd


class RiskAnalyzer:

    def __init__(self, data_path):
        """
        Load airport operational data.
        """

        self.data_path = data_path

        self.df = pd.read_csv(
            data_path,
            parse_dates=["timestamp"]
        )

    # ==================================================
    # GET AIRPORT DATA
    # ==================================================

    def get_airport_data(self, airport):
        """
        Return records for the selected airport.
        """

        return self.df[
            self.df["airport"].str.upper()
            == airport.upper()
        ].copy()

    # ==================================================
    # CALCULATE RISK FOR ONE RECORD
    # ==================================================

    def calculate_record_risk(self, row):
        """
        Calculate operational risk score
        for one airport observation.
        """

        score = 0
        reasons = []

        # ----------------------------------------------
        # Completion Rate
        # ----------------------------------------------

        if row["completion_rate"] < 0.80:

            score += 3

            reasons.append(
                "Low completion rate"
            )

        # ----------------------------------------------
        # Driver Cancellation Rate
        # ----------------------------------------------

        if row["driver_cancellation_rate"] > 0.15:

            score += 3

            reasons.append(
                "High driver cancellation rate"
            )

        # ----------------------------------------------
        # Average ETA
        # ----------------------------------------------

        if row["average_eta_minutes"] > 20:

            score += 2

            reasons.append(
                "High average ETA"
            )

        # ----------------------------------------------
        # Passenger Wait Time
        # ----------------------------------------------

        if row["passenger_wait_time_minutes"] > 12:

            score += 2

            reasons.append(
                "High passenger wait time"
            )

        # ----------------------------------------------
        # Queue Size
        # ----------------------------------------------

        if row["queue_size"] > 100:

            score += 1

            reasons.append(
                "Large driver queue"
            )

        # ----------------------------------------------
        # Risk Level
        # ----------------------------------------------

        if score >= 6:

            risk_level = "HIGH"

        elif score >= 3:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"

        return {
            "timestamp": str(row["timestamp"]),
            "airport": row["airport"],
            "risk_score": score,
            "risk_level": risk_level,
            "reasons": reasons
        }

    # ==================================================
    # CALCULATE RISK FOR AIRPORT
    # ==================================================

    def calculate_airport_risk(self, airport):
        """
        Calculate risk for every observation
        belonging to an airport.
        """

        data = self.get_airport_data(airport)

        if data.empty:
            return []

        results = []

        for _, row in data.iterrows():

            result = self.calculate_record_risk(row)

            results.append(result)

        return results

    # ==================================================
    # OVERALL AIRPORT RISK
    # ==================================================

    def overall_risk(self, airport):
        """
        Calculate the overall operational risk
        for an airport using average risk score.
        """

        results = self.calculate_airport_risk(airport)

        if not results:
            return {
                "airport": airport.upper(),
                "risk_score": 0,
                "risk_level": "UNKNOWN",
                "reasons": []
            }

        average_score = sum(
            result["risk_score"]
            for result in results
        ) / len(results)

        average_score = round(
            average_score,
            2
        )

        if average_score >= 6:

            risk_level = "HIGH"

        elif average_score >= 3:

            risk_level = "MEDIUM"

        else:

            risk_level = "LOW"

        # Collect all detected reasons
        all_reasons = []

        for result in results:

            all_reasons.extend(
                result["reasons"]
            )

        # Count frequency of each issue
        reason_counts = {}

        for reason in all_reasons:

            reason_counts[reason] = (
                reason_counts.get(reason, 0) + 1
            )

        # Sort most frequent issues first
        sorted_reasons = sorted(
            reason_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )

        top_reasons = [
            reason
            for reason, count
            in sorted_reasons[:5]
        ]

        return {
            "airport": airport.upper(),
            "risk_score": average_score,
            "risk_level": risk_level,
            "reasons": top_reasons
        }

    # ==================================================
    # COMPARE AIRPORTS
    # ==================================================

    def compare_airports(self):
        """
        Compare overall operational risk
        across all airports.
        """

        airports = sorted(
            self.df["airport"].unique()
        )

        results = []

        for airport in airports:

            result = self.overall_risk(airport)

            results.append(result)

        return results
