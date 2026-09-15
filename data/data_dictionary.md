# Airport Operations Policy Data Dictionary

## Purpose

This document describes the synthetic airport policy knowledge base
used by the Airport Operations AI Copilot.

## Airports

| Airport Code | Airport Name |
|---|---|
| SFO | San Francisco International Airport |
| LAX | Los Angeles International Airport |
| JFK | John F. Kennedy International Airport |

## Policy Documents

| File | Airport | Category |
|---|---|---|
| sfo_operations.md | SFO | Operations |
| sfo_pricing.md | SFO | Pricing / Surge |
| sfo_driver_policy.md | SFO | Driver |
| lax_operations.md | LAX | Operations |
| lax_pricing.md | LAX | Pricing / Surge |
| jfk_operations.md | JFK | Operations |
| jfk_pricing.md | JFK | Pricing / Surge |

## Important Policy Fields

### completion_rate

Percentage of airport ride requests successfully completed.

Expected operational threshold:

> 85%

### average_eta

Average estimated pickup time in minutes.

Normal target:

< 15 minutes

### driver_cancellation_rate

Percentage of requests cancelled by drivers.

SFO investigation threshold:

> 15%

### queue_size

Number of drivers currently waiting in the airport staging queue.

### active_drivers

Number of drivers currently available for airport requests.

### request_volume

Number of passenger ride requests during the relevant monitoring period.

### surge_multiplier

Current or proposed pricing multiplier.

Examples:

1.0x
1.2x
1.3x
1.5x

## Policy Source

All policy documents in this directory are synthetic documents
created for the Airport Operations AI Copilot case study.

They are used only for demonstration and RAG evaluation.

## RAG Metadata

Each document should retain:

- source
- airport
- policy_id
- category

These metadata fields will allow the application to identify
the source document used to answer a question.