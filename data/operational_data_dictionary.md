# Airport Operations Data Dictionary

## Purpose

This dataset contains synthetic hourly operational metrics for
SFO, LAX, and JFK airports.

The data is designed to simulate ride-hailing airport operations
and support KPI analysis, anomaly detection, policy-based
decision making, and AI recommendations.

---

## Dataset Details

| Attribute | Description |
|---|---|
| Dataset | Airport Operations Dataset |
| Data Type | Synthetic operational data |
| Granularity | Hourly |
| Airports | SFO, LAX, JFK |
| Records | 51 |
| Time Period | 2026-09-01 |
| Primary Use | Airport Operations AI Copilot |

---

## Column Definitions

### 1. timestamp

**Type:** DateTime

The date and hour at which the operational metrics were recorded.

**Example:**

2026-09-01 08:00

---

### 2. airport

**Type:** String

Three-letter airport code identifying the airport.

**Possible values:**

- SFO — San Francisco International Airport
- LAX — Los Angeles International Airport
- JFK — John F. Kennedy International Airport

---

### 3. queue_size

**Type:** Integer

Number of drivers currently waiting in the airport staging
or pickup queue.

A higher value may indicate driver accumulation or an
imbalance between driver supply and trip assignments.

**Example:**

95

---

### 4. active_drivers

**Type:** Integer

Number of drivers currently active and available for airport
ride requests.

A lower number of active drivers combined with high demand
can create operational pressure.

**Example:**

105

---

### 5. request_volume

**Type:** Integer

Number of passenger ride requests received during the
observation period.

Higher request volume indicates increased passenger demand.

**Example:**

220

---

### 6. completed_trips

**Type:** Integer

Number of passenger trips successfully completed during
the observation period.

This metric can be compared with request volume to understand
service completion performance.

**Example:**

185

---

### 7. completion_rate

**Type:** Float

Percentage of passenger requests that were successfully
completed.

The value is represented as a decimal.

**Example:**

0.82 = 82%

**Formula:**

completion_rate =
completed_trips / request_volume

---

### 8. average_eta_minutes

**Type:** Float

Average estimated time for a driver to reach the passenger,
measured in minutes.

Higher ETA can indicate increased congestion, driver shortage,
or operational pressure.

**Example:**

21.5 minutes

---

### 9. passenger_wait_time_minutes

**Type:** Float

Average amount of time passengers wait for their assigned
driver.

Higher passenger wait time indicates poorer service
performance.

**Example:**

12.5 minutes

---

### 10. driver_cancellation_rate

**Type:** Float

Percentage of ride requests cancelled by drivers.

The value is represented as a decimal.

**Example:**

0.18 = 18%

A high cancellation rate can indicate operational problems,
poor driver conditions, or excessive passenger wait times.

---

### 11. surge_multiplier

**Type:** Float

Current dynamic pricing multiplier applied to passenger
requests.

**Examples:**

- 1.0x = standard pricing
- 1.2x = 20% increase
- 1.5x = 50% increase

The maximum permitted value depends on the airport's policy.

For the current policy knowledge base:

- SFO maximum = 1.5x
- JFK maximum = 1.4x
- LAX policy value should be obtained from the retrieved
  policy context before making a decision.

---

# KPI Calculations

## Completion Rate

Measures the percentage of requests that result in completed
trips.

```text
Completion Rate =
Completed Trips / Request Volume
