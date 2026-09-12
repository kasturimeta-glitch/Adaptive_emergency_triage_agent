
import streamlit as st
import ollama

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Adaptive Emergency Triage Agent",
    page_icon="🚑",
    layout="wide"
)

# -----------------------------
# SYNTHETIC PATIENT
# -----------------------------
patient = {
    "age": 67,
    "chest_pain": True,
    "shortness_of_breath": None,
    "dizziness": None,
    "fainting": None,
    "heart_rate": 118,
    "oxygen_saturation": None,
    "systolic_bp": None
}

# -----------------------------
# RISK ENGINE
# -----------------------------
def calculate_risk(p):
    score = 0
    reasons = []

    if p.get("oxygen_saturation") is not None:
        if p["oxygen_saturation"] < 90:
            score += 5
            reasons.append("very low simulated oxygen saturation")
        elif p["oxygen_saturation"] < 94:
            score += 3
            reasons.append("low simulated oxygen saturation")

    if p.get("systolic_bp") is not None and p["systolic_bp"] < 90:
        score += 5
        reasons.append("low simulated blood pressure")

    if p.get("heart_rate") is not None and p["heart_rate"] > 120:
        score += 4
        reasons.append("high simulated heart rate")

    if p.get("chest_pain") is True:
        score += 4
        reasons.append("chest pain")

    if p.get("shortness_of_breath") is True:
        score += 4
        reasons.append("shortness of breath")

    if score >= 8:
        level = "HIGH"
    elif score >= 4:
        level = "MODERATE"
    else:
        level = "LOW"

    return score, level, reasons


# -----------------------------
# AI QUESTION PLANNER
# -----------------------------
def get_next_question(p):
    score, level, reasons = calculate_risk(p)

    prompt = f"""
You are the adaptive question planner of a SYNTHETIC
emergency triage decision-support simulation.

Patient state:
{p}

Current simulated risk:
{level}
Score:
{score}

Choose the SINGLE most useful next question.

Rules:
- Do not diagnose.
- Do not invent information.
- Do not repeat information that is already known.
- Prioritize information that could change routing.
- Keep the question short.
- If risk is HIGH, return STOP.

Return only the question.
"""

    try:
        response = ollama.chat(
            model="qwen3:4b",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        question = response["message"]["content"].strip()

        if question:
            return question

    except Exception:
        pass

    # Safe fallback if Ollama is unavailable
    if p["shortness_of_breath"] is None:
        return "Are you experiencing difficulty breathing?"

    if p["oxygen_saturation"] is None:
        return "What is your oxygen saturation reading?"

    if p["systolic_bp"] is None:
        return "What is your blood pressure reading?"

    if p["dizziness"] is None:
        return "Are you experiencing dizziness?"

    if p["fainting"] is None:
        return "Have you experienced fainting?"

    return "STOP"


# -----------------------------
# SESSION STATE
# -----------------------------
if "patient" not in st.session_state:
    st.session_state.patient = patient.copy()

if "history" not in st.session_state:
    st.session_state.history = []

if "question" not in st.session_state:
    st.session_state.question = None

if "contradiction" not in st.session_state:
    st.session_state.contradiction = False


p = st.session_state.patient

# -----------------------------
# HEADER
# -----------------------------
st.title("🚑 Adaptive Emergency Triage Agent")
st.subheader("Ask Less. Detect Earlier. Route Safer.")

st.caption(
    "Agentic AI Hackathon • Synthetic Decision-Support Simulation"
)

st.warning(
    "⚠️ This is a synthetic hackathon simulation, NOT a medical diagnosis system."
)

# -----------------------------
# PATIENT DASHBOARD
# -----------------------------
st.markdown("## 🧑‍⚕️ Agent Control Center")

c1, c2, c3 = st.columns(3)

c1.metric("Patient Age", p["age"])
c2.metric("Heart Rate", p["heart_rate"])
c3.metric(
    "SpO₂",
    f'{p["oxygen_saturation"]}%'
    if p["oxygen_saturation"] is not None
    else "Unknown"
)

# -----------------------------
# RISK
# -----------------------------
score, level, reasons = calculate_risk(p)

st.markdown("## 📊 Agent Assessment")

if level == "HIGH":
    st.error(f"🔴 HIGH RISK — Score {score}")
elif level == "MODERATE":
    st.warning(f"🟠 MODERATE RISK — Score {score}")
else:
    st.success(f"🟢 LOW RISK — Score {score}")

if reasons:
    st.write("Risk factors:", ", ".join(reasons))

# -----------------------------
# CONTRADICTION
# -----------------------------
if st.session_state.contradiction:
    st.error(
        "⚠️ CONTRADICTION DETECTED — Agent must reassess."
    )

# -----------------------------
# AGENT DECISION
# -----------------------------
st.markdown("## 🤖 Agent Decision")

if st.button("🧠 Ask Next Question", use_container_width=True):

    if level == "HIGH":
        st.session_state.question = "STOP"
    else:
        st.session_state.question = get_next_question(p)

if st.session_state.question:

    if st.session_state.question == "STOP":
        st.error("🛑 Agent stopped questioning because risk is high.")
    else:
        st.info(
            f"🤖 AGENT ASKS:\n\n"
            f"**{st.session_state.question}**"
        )

# -----------------------------
# PATIENT RESPONSE
# -----------------------------
st.markdown("## 👤 Patient Response")

answer = st.text_input(
    "Enter the patient's answer:",
    placeholder="Example: Yes / No / 96 / 120"
)

if st.button("➡️ Submit Answer", use_container_width=True):

    if answer.strip():

        old_question = st.session_state.question

        # Interpret common answers
        if old_question:

            q = old_question.lower()

            if "breathing" in q:
                field = "shortness_of_breath"
            elif "oxygen" in q or "spo2" in q:
                field = "oxygen_saturation"
            elif "blood pressure" in q:
                field = "systolic_bp"
            elif "dizziness" in q:
                field = "dizziness"
            elif "fainting" in q:
                field = "fainting"
            else:
                field = None

            if field:

                if answer.lower() in ["yes", "y"]:
                    value = True
                elif answer.lower() in ["no", "n"]:
                    value = False
                else:
                    try:
                        value = float(answer)
                    except:
                        value = answer

                # Detect contradiction
                if (
                    p.get(field) is not None
                    and p.get(field) != value
                ):
                    st.session_state.contradiction = True

                p[field] = value

                st.session_state.history.append({
                    "question": old_question,
                    "answer": answer
                })

        st.session_state.question = None
        st.rerun()

# -----------------------------
# NEW INFORMATION / ADAPTATION
# -----------------------------
st.markdown("## 🔄 New Information")

st.write(
    "Demonstrate the agent adapting when the patient's condition changes."
)

if st.button(
    "⚠️ Patient is NOW becoming short of breath",
    use_container_width=True
):

    old_value = p["shortness_of_breath"]

    if old_value is not None and old_value is not True:
        st.session_state.contradiction = True

    p["shortness_of_breath"] = True

    st.session_state.history.append({
        "question": "New information",
        "answer": "Patient is now becoming short of breath."
    })

    st.rerun()

# -----------------------------
# ROUTING
# -----------------------------
st.markdown("## 🚑 Final Routing")

score, level, reasons = calculate_risk(p)

if st.session_state.contradiction:
    st.error("🟣 ESCALATE — Conflicting information requires reassessment.")

elif level == "HIGH":
    st.error("🔴 EMERGENCY")

elif level == "MODERATE":
    st.warning("🟠 URGENT")

else:
    st.success("🟢 ROUTINE")

# -----------------------------
# AGENT TRACE
# -----------------------------
st.markdown("## 🧠 Agent Trace")

if not st.session_state.history:
    st.caption("No actions yet. The agent is waiting for input.")

for item in st.session_state.history:
    st.write(f"🤖 {item['question']}")
    st.write(f"👤 {item['answer']}")
    st.divider()
