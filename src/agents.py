import json
import re
from pathlib import Path

import requests

from src.tools import (
    get_airport_metrics,
    calculate_driver_incentive,
    trigger_surge_override,
)

from src.memory import ConversationMemory


# ============================================================
# CONFIGURATION
# ============================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:3b"

MAX_ITERATIONS = 5

VALID_AIRPORTS = {"SFO", "LAX", "JFK"}

COMPLETION_THRESHOLD = 0.85


# ============================================================
# OLLAMA HELPER
# ============================================================

def ask_llm(prompt):
    """
    Send a prompt to the local Ollama model.
    """

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data.get("response", "").strip()

    except Exception as e:
        return f"LLM_ERROR: {str(e)}"


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def extract_airport(text):
    """
    Detect an airport code from user text.
    """

    if not text:
        return None

    upper_text = text.upper()

    for airport in VALID_AIRPORTS:
        pattern = rf"\b{airport}\b"

        if re.search(pattern, upper_text):
            return airport

    return None


def extract_multiplier(text):
    """
    Extract a surge multiplier such as 1.3x or 1.5.
    """

    if not text:
        return None

    patterns = [
        r"\b(\d+(?:\.\d+)?)\s*x\b",
        r"\bmultiplier\s+(?:of\s+)?(\d+(?:\.\d+)?)\b",
        r"\bsurge\s+(?:to|at)\s+(\d+(?:\.\d+)?)\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text.lower(),
        )

        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass

    return None


def extract_driver_count(text):
    """
    Extract driver count from a request.
    """

    if not text:
        return None

    patterns = [
        r"(\d+)\s+drivers?",
        r"for\s+(\d+)",
        r"(\d+)\s+driver",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text.lower(),
        )

        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass

    return None


def extract_severity(text):
    """
    Detect severity level.
    """

    if not text:
        return None

    upper_text = text.upper()

    for level in ["HIGH", "MEDIUM", "LOW"]:

        if re.search(
            rf"\b{level}\b",
            upper_text,
        ):
            return level

    return None


def is_greeting(text):
    """
    Detect simple greetings so they never trigger an operational tool.
    """

    if not text:
        return False

    cleaned = text.lower().strip()

    greetings = {
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening",
        "hiya",
    }

    return cleaned in greetings


def is_general_copilot_question(text):
    """
    Detect questions about the copilot itself.
    """

    if not text:
        return False

    lower = text.lower()

    keywords = [
        "what does an airport operations ai copilot do",
        "what is an airport operations ai copilot",
        "what can you do",
        "what does this copilot do",
        "what is this copilot",
    ]

    return any(
        keyword in lower
        for keyword in keywords
    )


# ============================================================
# POLICY RETRIEVAL
# ============================================================

def search_policy(query, airport_code=None):
    """
    Day 3 policy retrieval.

    First attempts to use the existing Day 1/Day 2 RAG
    search_policy implementation if available.

    If it is unavailable, performs a lightweight local
    policy-document search so the multi-agent workflow
    remains executable.
    """

    # --------------------------------------------------------
    # Try existing vector-store implementation
    # --------------------------------------------------------

    try:

        from src.vector_store import search_policy as rag_search

        try:
            result = rag_search(
                query,
                top_k=3,
            )

            if result:
                return {
                    "success": True,
                    "source": "vector_store",
                    "results": result,
                }

        except TypeError:

            result = rag_search(query)

            if result:
                return {
                    "success": True,
                    "source": "vector_store",
                    "results": result,
                }

    except Exception:
        pass

    # --------------------------------------------------------
    # Local policy fallback
    # --------------------------------------------------------

    policy_dir = Path("data/airport_policies")

    if not policy_dir.exists():

        return {
            "success": False,
            "error": "Policy knowledge base was not found.",
            "results": [],
        }

    files = list(
        policy_dir.glob("*.md")
    )

    if airport_code:
        airport_code = airport_code.lower()

        airport_files = [
            file
            for file in files
            if file.name.startswith(airport_code)
        ]

        if airport_files:
            files = airport_files

    query_words = {
        word.lower()
        for word in re.findall(
            r"[a-zA-Z0-9]+",
            query,
        )
        if len(word) > 2
    }

    scored = []

    for file in files:

        try:
            content = file.read_text(
                encoding="utf-8"
            )

        except Exception:
            continue

        lower_content = content.lower()

        score = sum(
            1
            for word in query_words
            if word in lower_content
        )

        scored.append(
            (
                score,
                file.name,
                content,
            )
        )

    scored.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    results = []

    for score, filename, content in scored[:3]:

        results.append(
            {
                "source": filename,
                "score": score,
                "content": content[:5000],
            }
        )

    return {
        "success": True,
        "source": "local_policy_search",
        "results": results,
    }


# ============================================================
# AGENT 1 — OPERATIONS INVESTIGATOR
# ============================================================

class OperationsInvestigator:

    name = "Operations Investigator"

    def run(self, user_query, airport_code=None):

        print("\n[INVESTIGATOR AGENT]")
        print("Analyzing operational telemetry...")

        if not airport_code:

            return {
                "success": False,
                "agent": self.name,
                "error": "Airport code is required for operational investigation.",
            }

        metrics_result = get_airport_metrics(
            airport_code
        )

        if not metrics_result.get("success"):

            return {
                "success": False,
                "agent": self.name,
                "error": metrics_result.get(
                    "error",
                    "Unable to retrieve airport metrics.",
                ),
            }

        metrics = metrics_result["metrics"]

        completion_rate = metrics[
            "completion_rate"
        ]

        cancellation_rate = metrics[
            "driver_cancellation_rate"
        ]

        queue_size = metrics[
            "queue_size"
        ]

        eta = metrics[
            "average_eta_minutes"
        ]

        anomalies = []

        if completion_rate < COMPLETION_THRESHOLD:
            anomalies.append(
                "Completion rate is below the 85% operational threshold."
            )

        if cancellation_rate >= 0.06:
            anomalies.append(
                "Driver cancellation rate is elevated."
            )

        if queue_size >= 40:
            anomalies.append(
                "Airport queue size is elevated."
            )

        if eta >= 9:
            anomalies.append(
                "Average ETA is elevated."
            )

        if (
            completion_rate < 0.75
            or cancellation_rate >= 0.10
            or queue_size >= 100
        ):
            severity = "HIGH"

        elif (
            completion_rate < COMPLETION_THRESHOLD
            or cancellation_rate >= 0.05
            or queue_size >= 40
            or eta >= 9
        ):
            severity = "MEDIUM"

        else:
            severity = "LOW"

        if anomalies:
            status = "ANOMALY"
        else:
            status = "NORMAL"

        result = {
            "success": True,
            "agent": self.name,
            "airport_code": airport_code,
            "status": status,
            "severity": severity,
            "metrics": metrics,
            "anomalies": anomalies,
            "potential_factors": [
                "Driver cancellation rate",
                "Queue size",
                "Average ETA",
                "Request volume",
            ],
        }

        print(
            f"Airport: {airport_code}"
        )

        print(
            f"Status: {status}"
        )

        print(
            f"Severity: {severity}"
        )

        print(
            f"Completion rate: "
            f"{completion_rate * 100:.1f}%"
        )

        return result


# ============================================================
# AGENT 2 — POLICY & COMPLIANCE
# ============================================================

class PolicyComplianceAgent:

    name = "Policy & Compliance Agent"

    def run(
        self,
        user_query,
        airport_code,
        investigation,
    ):

        print("\n[POLICY & COMPLIANCE AGENT]")
        print("Searching policy knowledge base...")

        query = user_query

        if investigation:
            query += " " + " ".join(
                investigation.get(
                    "anomalies",
                    [],
                )
            )

        policy_result = search_policy(
            query,
            airport_code,
        )

        if not policy_result.get(
            "success"
        ):

            return {
                "success": False,
                "agent": self.name,
                "error": policy_result.get(
                    "error",
                    "Policy retrieval failed.",
                ),
                "results": [],
            }

        results = policy_result.get(
            "results",
            [],
        )

        sources = []

        for item in results:

            if isinstance(item, dict):

                source = (
                    item.get("source")
                    or item.get("metadata", {}).get(
                        "source"
                    )
                )

                if source:
                    sources.append(
                        source
                    )

        # ----------------------------------------------------
        # Extract policy text for compliance analysis
        # ----------------------------------------------------

        policy_text = ""

        for item in results:

            if isinstance(item, dict):

                content = (
                    item.get("content")
                    or item.get("text")
                    or item.get("document")
                    or ""
                )

                policy_text += (
                    "\n" + str(content)
                )

            else:
                policy_text += (
                    "\n" + str(item)
                )

        multiplier = extract_multiplier(
            user_query
        )

        policy_max_multiplier = None

        max_patterns = [
            r"maximum.*?(\d+(?:\.\d+)?)x",
            r"max(?:imum)?.*?(\d+(?:\.\d+)?)x",
            r"up to.*?(\d+(?:\.\d+)?)x",
        ]

        for pattern in max_patterns:

            match = re.search(
                pattern,
                policy_text.lower(),
                re.DOTALL,
            )

            if match:

                try:
                    policy_max_multiplier = float(
                        match.group(1)
                    )

                    break

                except ValueError:
                    pass

        action_allowed = True
        approval_required = False
        restriction = None

        # ----------------------------------------------------
        # Day 3 policy validation
        # ----------------------------------------------------

        if multiplier is not None:

            if (
                policy_max_multiplier is not None
                and multiplier > policy_max_multiplier
            ):

                action_allowed = False

                restriction = (
                    f"Requested multiplier "
                    f"{multiplier}x exceeds the "
                    f"policy maximum of "
                    f"{policy_max_multiplier}x."
                )

            elif multiplier >= 1.3:

                approval_required = True

        result = {
            "success": True,
            "agent": self.name,
            "airport_code": airport_code,
            "sources": sources,
            "retrieved_policies": results,
            "requested_multiplier": multiplier,
            "policy_max_multiplier": policy_max_multiplier,
            "action_allowed": action_allowed,
            "approval_required": approval_required,
            "restriction": restriction,
        }

        print(
            "Retrieved sources:",
            sources if sources else "None",
        )

        if restriction:
            print(
                "Policy restriction:",
                restriction,
            )

        elif approval_required:
            print(
                "Policy result: ACTION REQUIRES APPROVAL"
            )

        else:
            print(
                "Policy result: ACTION ALLOWED"
            )

        return result


# ============================================================
# AGENT 3 — RESOLUTION AGENT
# ============================================================

class ResolutionAgent:

    name = "Resolution Agent"

    def run(
        self,
        user_query,
        investigation,
        policy,
    ):

        print("\n[RESOLUTION AGENT]")
        print("Evaluating possible interventions...")

        if not investigation.get(
            "success"
        ):

            return {
                "success": False,
                "agent": self.name,
                "error": "Investigation is incomplete.",
            }

        airport_code = investigation[
            "airport_code"
        ]

        severity = investigation[
            "severity"
        ]

        metrics = investigation[
            "metrics"
        ]

        completion_rate = metrics[
            "completion_rate"
        ]

        cancellation_rate = metrics[
            "driver_cancellation_rate"
        ]

        queue_size = metrics[
            "queue_size"
        ]

        current_surge = metrics[
            "surge_multiplier"
        ]

        actions = []

        if completion_rate < COMPLETION_THRESHOLD:

            actions.append(
                "Increase driver supply using an appropriate incentive."
            )

        if queue_size >= 40:

            actions.append(
                "Monitor and reduce airport queue pressure."
            )

        if cancellation_rate >= 0.05:

            actions.append(
                "Investigate elevated driver cancellations."
            )

        requested_multiplier = extract_multiplier(
            user_query
        )

        if requested_multiplier is not None:

            if policy.get(
                "action_allowed",
                True,
            ):

                if policy.get(
                    "approval_required",
                    False,
                ):

                    actions.append(
                        f"Request approval to increase "
                        f"surge from {current_surge}x "
                        f"to {requested_multiplier}x."
                    )

                else:

                    actions.append(
                        f"Increase surge from "
                        f"{current_surge}x to "
                        f"{requested_multiplier}x."
                    )

            else:

                actions.append(
                    "Do not execute the requested surge "
                    "because it violates policy."
                )

        if not actions:

            actions.append(
                "Continue monitoring airport operations."
            )

        recommended_action = actions[0]

        result = {
            "success": True,
            "agent": self.name,
            "airport_code": airport_code,
            "severity": severity,
            "current_surge": current_surge,
            "possible_actions": actions,
            "recommended_action": recommended_action,
        }

        print(
            "Recommended action:",
            recommended_action,
        )

        return result


# ============================================================
# ORCHESTRATOR AGENT
# ============================================================

class OrchestratorAgent:

    name = "Orchestrator"

    def __init__(self):

        self.investigator = (
            OperationsInvestigator()
        )

        self.policy_agent = (
            PolicyComplianceAgent()
        )

        self.resolution_agent = (
            ResolutionAgent()
        )

        self.memory = ConversationMemory()

    # --------------------------------------------------------
    # Resolve airport from current query + memory
    # --------------------------------------------------------

    def resolve_airport(self, user_query):

        airport = extract_airport(
            user_query
        )

        if airport:

            self.memory.set_airport(
                airport
            )

            return airport

        return self.memory.get_airport()

    # --------------------------------------------------------
    # Determine whether request is operational
    # --------------------------------------------------------

    def classify_request(self, user_query):

        lower = user_query.lower()

        operational_keywords = [
            "completion",
            "queue",
            "drivers",
            "driver",
            "eta",
            "cancellation",
            "surge",
            "demand",
            "airport",
            "metrics",
            "incentive",
            "severity",
            "investigate",
            "operations",
            "operational",
        ]

        return any(
            keyword in lower
            for keyword in operational_keywords
        )

    # --------------------------------------------------------
    # Final LLM explanation
    # --------------------------------------------------------

    def generate_final_answer(
        self,
        user_query,
        investigation=None,
        policy=None,
        resolution=None,
    ):

        context = {
            "user_query": user_query,
            "investigation": investigation,
            "policy": policy,
            "resolution": resolution,
        }

        prompt = f"""
You are an Airport Operations AI Copilot.

Answer the user's request using ONLY the operational
information supplied in the context.

Do not invent metrics.
Do not invent policies.
Do not claim that an action was executed unless the
tool result says it was executed.

Be concise and operationally useful.

Context:
{json.dumps(context, indent=2, default=str)}

User request:
{user_query}

Provide a clear final response.
"""

        answer = ask_llm(
            prompt
        )

        if answer.startswith(
            "LLM_ERROR:"
        ):

            # Deterministic fallback
            if resolution:

                return (
                    f"At {resolution['airport_code']}, "
                    f"the recommended action is: "
                    f"{resolution['recommended_action']}"
                )

            if investigation:

                metrics = investigation[
                    "metrics"
                ]

                return (
                    f"At {investigation['airport_code']}, "
                    f"completion rate is "
                    f"{metrics['completion_rate'] * 100:.1f}% "
                    f"with {metrics['active_drivers']} "
                    f"active drivers."
                )

            return answer

        return answer

    # --------------------------------------------------------
    # MAIN AGENTIC WORKFLOW
    # --------------------------------------------------------

    def run(self, user_query):

        user_query = user_query.strip()

        if not user_query:

            return {
                "success": False,
                "answer": "Please enter a question.",
                "trace": [],
            }

        # ----------------------------------------------------
        # Greeting
        # ----------------------------------------------------

        if is_greeting(
            user_query
        ):

            answer = (
                "Hello! How can I help you with "
                "airport operations today?"
            )

            self.memory.add_turn(
                user_query,
                answer,
            )

            return {
                "success": True,
                "answer": answer,
                "trace": [
                    {
                        "iteration": 1,
                        "agent": "Orchestrator",
                        "action": "HANDLE_GREETING",
                    }
                ],
            }

        # ----------------------------------------------------
        # General copilot question
        # ----------------------------------------------------

        if is_general_copilot_question(
            user_query
        ):

            answer = (
                "An Airport Operations AI Copilot "
                "helps operations teams investigate "
                "airport performance, retrieve relevant "
                "policies, identify operational issues, "
                "and recommend appropriate actions. "
                "This Day 3 system uses an Orchestrator, "
                "Operations Investigator, Policy & "
                "Compliance Agent, and Resolution Agent."
            )

            self.memory.add_turn(
                user_query,
                answer,
            )

            return {
                "success": True,
                "answer": answer,
                "trace": [
                    {
                        "iteration": 1,
                        "agent": "Orchestrator",
                        "action": "GENERAL_QUESTION",
                    }
                ],
            }

        # ----------------------------------------------------
        # Resolve airport
        # ----------------------------------------------------

        airport_code = self.resolve_airport(
            user_query
        )

        # ----------------------------------------------------
        # If user only supplies an airport code
        # ----------------------------------------------------

        if (
            user_query.upper()
            in VALID_AIRPORTS
        ):

            answer = (
                f"I'll use {user_query.upper()} "
                "as the active airport for your "
                "next operational request."
            )

            self.memory.add_turn(
                user_query,
                answer,
            )

            return {
                "success": True,
                "answer": answer,
                "trace": [
                    {
                        "iteration": 1,
                        "agent": "Orchestrator",
                        "action": "UPDATE_MEMORY",
                        "airport": user_query.upper(),
                    }
                ],
            }

        # ----------------------------------------------------
        # Non-operational request
        # ----------------------------------------------------

        if not self.classify_request(
            user_query
        ):

            answer = ask_llm(
                f"""
You are an Airport Operations AI Copilot.

Answer this general user question concisely.

Question:
{user_query}
"""
            )

            if answer.startswith(
                "LLM_ERROR:"
            ):

                answer = (
                    "I can help with airport "
                    "operations, metrics, policies, "
                    "driver incentives, and operational "
                    "recommendations."
                )

            self.memory.add_turn(
                user_query,
                answer,
            )

            return {
                "success": True,
                "answer": answer,
                "trace": [
                    {
                        "iteration": 1,
                        "agent": "Orchestrator",
                        "action": "GENERAL_REQUEST",
                    }
                ],
            }

        # ----------------------------------------------------
        # Missing airport
        # ----------------------------------------------------

        if not airport_code:

            answer = (
                "Which airport should I investigate? "
                "Please provide SFO, LAX, or JFK."
            )

            self.memory.add_turn(
                user_query,
                answer,
            )

            return {
                "success": True,
                "answer": answer,
                "trace": [
                    {
                        "iteration": 1,
                        "agent": "Orchestrator",
                        "action": "REQUEST_AIRPORT",
                    }
                ],
            }

        # ----------------------------------------------------
        # REACT LOOP
        # ----------------------------------------------------

        trace = []

        investigation = None
        policy = None
        resolution = None

        for iteration in range(
            1,
            MAX_ITERATIONS + 1,
        ):

            print(
                f"\n========== ITERATION {iteration} =========="
            )

            # THINK
            trace.append(
                {
                    "iteration": iteration,
                    "phase": "THINK",
                    "agent": self.name,
                    "message": (
                        "Determine which specialist "
                        "should act next."
                    ),
                }
            )

            # ------------------------------------------------
            # ACT — Investigator
            # ------------------------------------------------

            if investigation is None:

                print(
                    "[ORCHESTRATOR] "
                    "Handoff -> Operations Investigator"
                )

                investigation = (
                    self.investigator.run(
                        user_query,
                        airport_code,
                    )
                )

                trace.append(
                    {
                        "iteration": iteration,
                        "phase": "ACT",
                        "agent": self.investigator.name,
                        "result": investigation,
                    }
                )

                if not investigation.get(
                    "success"
                ):

                    break

                # OBSERVE
                trace.append(
                    {
                        "iteration": iteration,
                        "phase": "OBSERVE",
                        "agent": self.name,
                        "message": (
                            "Operational telemetry "
                            "has been collected."
                        ),
                    }
                )

                continue

            # ------------------------------------------------
            # ACT — Policy Agent
            # ------------------------------------------------

            if policy is None:

                print(
                    "[ORCHESTRATOR] "
                    "Handoff -> Policy & Compliance Agent"
                )

                policy = (
                    self.policy_agent.run(
                        user_query,
                        airport_code,
                        investigation,
                    )
                )

                trace.append(
                    {
                        "iteration": iteration,
                        "phase": "ACT",
                        "agent": self.policy_agent.name,
                        "result": policy,
                    }
                )

                # OBSERVE
                trace.append(
                    {
                        "iteration": iteration,
                        "phase": "OBSERVE",
                        "agent": self.name,
                        "message": (
                            "Relevant policy has been "
                            "retrieved and checked."
                        ),
                    }
                )

                continue

            # ------------------------------------------------
            # ACT — Resolution Agent
            # ------------------------------------------------

            if resolution is None:

                print(
                    "[ORCHESTRATOR] "
                    "Handoff -> Resolution Agent"
                )

                resolution = (
                    self.resolution_agent.run(
                        user_query,
                        investigation,
                        policy,
                    )
                )

                trace.append(
                    {
                        "iteration": iteration,
                        "phase": "ACT",
                        "agent": self.resolution_agent.name,
                        "result": resolution,
                    }
                )

                # OBSERVE
                trace.append(
                    {
                        "iteration": iteration,
                        "phase": "OBSERVE",
                        "agent": self.name,
                        "message": (
                            "A resolution recommendation "
                            "has been generated."
                        ),
                    }
                )

                break

        # ----------------------------------------------------
        # FINAL RESPONSE
        # ----------------------------------------------------

        answer = self.generate_final_answer(
            user_query,
            investigation,
            policy,
            resolution,
        )

        self.memory.add_turn(
            user_query,
            answer,
        )

        return {
            "success": True,
            "answer": answer,
            "airport_code": airport_code,
            "investigation": investigation,
            "policy": policy,
            "resolution": resolution,
            "iterations": min(
                len(
                    [
                        item
                        for item in trace
                        if item.get("phase") == "THINK"
                    ]
                ),
                MAX_ITERATIONS,
            ),
            "trace": trace,
        }


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def run_agent(user_query, orchestrator=None):

    if orchestrator is None:

        orchestrator = OrchestratorAgent()

    return orchestrator.run(
        user_query
    )
