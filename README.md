# ✈️ Airport Operations AI Copilot

An AI-powered Airport Operations Copilot that helps airport operations teams monitor airport performance, investigate operational issues, retrieve relevant policies, recommend actions, and safely execute high-risk operational changes through human approval.

The project was developed incrementally over **5 days**, progressing from a basic RAG-based policy assistant to a complete agentic AI application with tools, multi-agent orchestration, guardrails, human-in-the-loop approval, conversational memory, and a Streamlit interface.

---

# 📌 Project Overview

Airport operations involve monitoring multiple operational metrics such as:

- Completion Rate
- Average ETA
- Driver Cancellation Rate
- Active Drivers
- Queue Size
- Surge Multiplier
- Request Volume

Operations teams may need to investigate issues and decide whether an operational intervention is required.

The Airport Operations AI Copilot provides an AI-assisted workflow:

```text
User Request
     ↓
Orchestrator
     ↓
Operations Investigator
     ↓
Operational Tools
     ↓
Policy & Compliance Agent
     ↓
RAG / Policy Retrieval
     ↓
Resolution Agent
     ↓
Guardrails
     ↓
Risk Classification
     ↓
Human Approval
     ↓
Action Execution
     ↓
Audit / Execution Trace
     ↓
Final Explanation
