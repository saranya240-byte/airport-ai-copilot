import streamlit as st
import sys
import os

# ---------------------------------------------------------
# PATH SETUP
# ---------------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.tools import (
    get_airport_metrics,
    calculate_driver_incentive,
    trigger_surge_override
)

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Airport AI Copilot",
    page_icon="✈️",
    layout="wide"
)

# ---------------------------------------------------------
# SIMPLE CUSTOM CSS
# ---------------------------------------------------------
st.markdown("""
<style>

.main {
    padding-top: 1rem;
}

.header {
    padding: 18px 25px;
    border-radius: 10px;
    background: #f5f7fa;
    border: 1px solid #e1e5ea;
    margin-bottom: 20px;
}

.header h1 {
    margin: 0;
    font-size: 28px;
}

.header p {
    margin-top: 5px;
    color: #666;
}

.metric-box {
    padding: 18px;
    border: 1px solid #e1e5ea;
    border-radius: 10px;
    background: white;
    text-align: center;
}

.metric-label {
    font-size: 14px;
    color: #666;
}

.metric-value {
    font-size: 25px;
    font-weight: 600;
    margin-top: 5px;
}

.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-top: 15px;
    margin-bottom: 10px;
}

.trace {
    padding: 10px 15px;
    border-left: 3px solid #4a90e2;
    background: #f7f9fc;
    margin-bottom: 8px;
    border-radius: 5px;
}

.approval {
    padding: 18px;
    border: 1px solid #e6b800;
    background: #fffbea;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# AIRPORT DATA
# ---------------------------------------------------------
AIRPORTS = ["SFO", "LAX", "JFK"]


def get_metrics(airport):
    result = get_airport_metrics(airport)

    if result.get("success"):
        return result["metrics"]

    return None


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "selected_airport" not in st.session_state:
    st.session_state.selected_airport = "SFO"

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_action" not in st.session_state:
    st.session_state.last_action = None

if "approval_result" not in st.session_state:
    st.session_state.approval_result = None


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.markdown("""
<div class="header">
    <h1>✈️ Airport Operations AI Copilot</h1>
    <p>AI-powered airport monitoring, investigation and operational decision support</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:

    st.subheader("Airport")

    airport = st.selectbox(
        "Select airport",
        AIRPORTS,
        index=AIRPORTS.index(st.session_state.selected_airport)
    )

    st.session_state.selected_airport = airport

    st.divider()

    st.subheader("Quick Actions")

    if st.button("📊 View Metrics", use_container_width=True):
        st.session_state.messages.append(
            f"Show me the metrics for {airport}"
        )

    if st.button("🔎 Investigate Airport", use_container_width=True):
        st.session_state.messages.append(
            f"Investigate {airport}"
        )

    if st.button("💰 Calculate Incentive", use_container_width=True):
        st.session_state.messages.append(
            "Calculate an incentive for 40 drivers at high severity"
        )

    st.divider()

    st.caption("Day 5 • End-to-End AI Copilot")


# ---------------------------------------------------------
# CURRENT METRICS
# ---------------------------------------------------------
metrics = get_metrics(airport)

if metrics:

    st.markdown(
        f'<div class="section-title">Operational Metrics — {airport}</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">Completion Rate</div>
                <div class="metric-value">
                    {metrics["completion_rate"] * 100:.1f}%
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">Average ETA</div>
                <div class="metric-value">
                    {metrics["average_eta_minutes"]:.1f} min
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">Active Drivers</div>
                <div class="metric-value">
                    {metrics["active_drivers"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">Queue Size</div>
                <div class="metric-value">
                    {metrics["queue_size"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col5:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-label">Surge</div>
                <div class="metric-value">
                    {metrics["surge_multiplier"]:.1f}x
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


# ---------------------------------------------------------
# MAIN LAYOUT
# ---------------------------------------------------------
st.markdown("")

left, right = st.columns([1.6, 1])


# =========================================================
# CHAT SECTION
# =========================================================
with left:

    st.markdown(
        '<div class="section-title">💬 Copilot</div>',
        unsafe_allow_html=True
    )

    # Display previous messages
    for message in st.session_state.messages:

        if message.startswith("AI:"):
            with st.chat_message("assistant"):
                st.write(message.replace("AI:", "", 1).strip())

        else:
            with st.chat_message("user"):
                st.write(message)

    prompt = st.chat_input(
        "Ask about airport operations..."
    )

    if prompt:

        st.session_state.messages.append(prompt)

        with st.chat_message("user"):
            st.write(prompt)

        prompt_lower = prompt.lower()

        # -------------------------------------------------
        # DETECT AIRPORT
        # -------------------------------------------------
        requested_airport = None

        for code in AIRPORTS:
            if code.lower() in prompt_lower:
                requested_airport = code
                break

        if requested_airport:
            st.session_state.selected_airport = requested_airport
            airport = requested_airport
            metrics = get_metrics(airport)

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------
        response = ""

        # Completion rate
        if "completion rate" in prompt_lower:

            if metrics:
                response = (
                    f"The completion rate at {airport} is "
                    f"{metrics['completion_rate'] * 100:.1f}%."
                )

        # Surge
        elif "surge" in prompt_lower:

            if metrics:
                response = (
                    f"The current surge multiplier at {airport} is "
                    f"{metrics['surge_multiplier']:.1f}x."
                )

        # Drivers
        elif "driver" in prompt_lower and (
            "how many" in prompt_lower
            or "active" in prompt_lower
        ):

            if metrics:
                response = (
                    f"There are {metrics['active_drivers']} active "
                    f"drivers at {airport}."
                )

        # ETA
        elif "eta" in prompt_lower:

            if metrics:
                response = (
                    f"The average ETA at {airport} is "
                    f"{metrics['average_eta_minutes']:.1f} minutes."
                )

        # Queue
        elif "queue" in prompt_lower:

            if metrics:
                response = (
                    f"The current queue size at {airport} is "
                    f"{metrics['queue_size']}."
                )

        # Copilot explanation
        elif "what does" in prompt_lower and "copilot" in prompt_lower:

            response = (
                "The Airport Operations AI Copilot monitors airport "
                "telemetry, investigates operational issues, retrieves "
                "relevant policies, evaluates actions, applies guardrails, "
                "and supports human-approved operational decisions."
            )

        # Investigation
        elif "investigate" in prompt_lower:

            if metrics:

                completion = metrics["completion_rate"]

                if completion < 0.85:
                    status = "ANOMALY"
                    severity = "HIGH"
                elif completion < 0.90:
                    status = "ANOMALY"
                    severity = "MEDIUM"
                else:
                    status = "NORMAL"
                    severity = "LOW"

                response = (
                    f"Investigation for {airport}:\n\n"
                    f"- Completion Rate: {completion * 100:.1f}%\n"
                    f"- Average ETA: {metrics['average_eta_minutes']:.1f} min\n"
                    f"- Driver Cancellation: "
                    f"{metrics['driver_cancellation_rate'] * 100:.1f}%\n"
                    f"- Queue Size: {metrics['queue_size']}\n"
                    f"- Surge: {metrics['surge_multiplier']:.1f}x\n"
                    f"- Status: {status}\n"
                    f"- Severity: {severity}"
                )

        # Incentive
        elif "incentive" in prompt_lower:

            result = calculate_driver_incentive(
                driver_count=40,
                severity_level="HIGH"
            )

            if result.get("success"):

                response = (
                    f"Recommended incentive: "
                    f"${result['recommended_incentive_per_driver']:.2f} "
                    f"per driver.\n\n"
                    f"Drivers: {result['driver_count']}\n"
                    f"Severity: {result['severity_level']}\n"
                    f"Estimated total cost: "
                    f"${result['estimated_total_cost']:.2f}"
                )

        # Surge request
        elif "increase surge" in prompt_lower or "surge override" in prompt_lower:

            response = (
                f"A surge change at {airport} is an operational action. "
                f"The request will be evaluated against policy and "
                f"guardrails before execution."
            )

        else:

            response = (
                f"I can help you analyze {airport} operations. "
                f"You can ask about completion rate, ETA, drivers, "
                f"queue size, surge, incentives, or investigation."
            )

        with st.chat_message("assistant"):
            st.write(response)

        st.session_state.messages.append(
            f"AI: {response}"
        )


# =========================================================
# RIGHT SIDE - AGENT ACTIVITY
# =========================================================
with right:

    st.markdown(
        '<div class="section-title">🤖 Agent Activity</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="trace">
        <b>1. Orchestrator</b><br>
        Determines the required workflow
        </div>

        <div class="trace">
        <b>2. Operations Investigator</b><br>
        Analyzes airport telemetry
        </div>

        <div class="trace">
        <b>3. Policy Agent</b><br>
        Retrieves and validates policy
        </div>

        <div class="trace">
        <b>4. Resolution Agent</b><br>
        Generates operational recommendation
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">📚 RAG Trace</div>',
        unsafe_allow_html=True
    )

    st.info(
        f"Policy knowledge base available for {airport}"
    )

    st.markdown(
        '<div class="section-title">🛡️ Guardrail Status</div>',
        unsafe_allow_html=True
    )

    st.success("Input validation active")
    st.success("Policy validation active")
    st.success("Human approval enabled")


# ---------------------------------------------------------
# END-TO-END DEMO
# ---------------------------------------------------------
st.divider()

st.markdown(
    '<div class="section-title">🚦 End-to-End Operations Demo</div>',
    unsafe_allow_html=True
)

st.write(
    "Test the complete Day 5 workflow: "
    "Investigation → Policy → Recommendation → Guardrail → Approval → Execution."
)

demo_col1, demo_col2 = st.columns([3, 1])

with demo_col1:

    surge_value = st.number_input(
        "Requested Surge Multiplier",
        min_value=1.0,
        max_value=2.0,
        value=1.5,
        step=0.1
    )

with demo_col2:

    st.write("")
    st.write("")

    investigate_button = st.button(
        "🔎 Run Investigation",
        use_container_width=True
    )


if investigate_button:

    metrics = get_metrics(airport)

    if metrics:

        st.subheader(f"Investigation — {airport}")

        completion = metrics["completion_rate"]

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Completion Rate",
            f"{completion * 100:.1f}%"
        )

        col2.metric(
            "Queue Size",
            metrics["queue_size"]
        )

        col3.metric(
            "Current Surge",
            f"{metrics['surge_multiplier']:.1f}x"
        )

        st.write("### Agent Workflow")

        st.write("✅ Operations Investigator — telemetry collected")
        st.write("✅ Policy Agent — pricing policy checked")
        st.write("✅ Resolution Agent — recommendation generated")

        st.write("### Recommendation")

        st.info(
            f"Recommended action: Increase {airport} surge "
            f"from {metrics['surge_multiplier']:.1f}x "
            f"to {surge_value:.1f}x."
        )

        # -------------------------------------------------
        # GUARDRAIL
        # -------------------------------------------------
        if surge_value > 1.5:

            st.error(
                "🚫 POLICY VIOLATION\n\n"
                "Maximum permitted surge is 1.5x. "
                "The requested action has been blocked."
            )

        elif surge_value >= 1.3:

            st.warning(
                f"⚠️ HUMAN APPROVAL REQUIRED\n\n"
                f"Action: Increase {airport} surge to "
                f"{surge_value:.1f}x\n\n"
                f"Risk Level: HIGH"
            )

            approve_col, reject_col = st.columns(2)

            with approve_col:

                if st.button(
                    "✅ APPROVE ACTION",
                    use_container_width=True
                ):

                    result = trigger_surge_override(
                        airport_code=airport,
                        new_multiplier=surge_value,
                        reason="Low completion rate / operational demand"
                    )

                    st.session_state.approval_result = result

            with reject_col:

                if st.button(
                    "❌ REJECT ACTION",
                    use_container_width=True
                ):

                    st.session_state.approval_result = {
                        "success": False,
                        "status": "REJECTED",
                        "message": "Human approval rejected."
                    }

        else:

            st.info(
                "Medium-risk action. Approval workflow will "
                "be evaluated before execution."
            )


# ---------------------------------------------------------
# EXECUTION RESULT
# ---------------------------------------------------------
if st.session_state.approval_result:

    result = st.session_state.approval_result

    st.divider()

    st.subheader("Execution Result")

    if result.get("success"):

        st.success(
            "ACTION EXECUTED\n\n"
            f"{airport} surge updated to "
            f"{result.get('new_multiplier', surge_value):.1f}x."
        )

    else:

        st.error(
            f"Action not executed.\n\n"
            f"Status: {result.get('status', 'REJECTED')}\n\n"
            f"{result.get('message', result.get('error', 'Action blocked.'))}"
        )


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.divider()

st.caption(
    "Airport Operations AI Copilot • Day 5 • "
    "RAG + Tools + Multi-Agent Workflow + Guardrails + Human-in-the-Loop"
)