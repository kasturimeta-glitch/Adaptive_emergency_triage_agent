# 🚑 Adaptive Emergency Triage Agent

### Ask Less. Detect Earlier. Route Safer.

An agentic AI prototype for adaptive emergency triage that dynamically decides what information to ask next based on the patient's current state, risk, and newly emerging information.

> ⚠️ **Important:** This is a synthetic hackathon decision-support simulation. It is NOT a medical diagnosis system, and the risk rules are not clinically validated.

---

## 🎯 Problem

Emergency triage often begins with incomplete patient information. A fixed questionnaire may ask unnecessary questions while missing information that could change the urgency of a case.

The key question is:

**"What information should the agent ask for NEXT?"**

---

## 💡 Our Solution

The **Adaptive Emergency Triage Agent** uses a closed-loop agentic workflow:

**Observe → Decide → Act → Reassess → Adapt**

The agent:

- Maintains an explicit patient state
- Identifies missing and important information
- Selects the next useful question
- Updates the patient state after every response
- Recalculates synthetic risk
- Detects new or contradictory information
- Changes its questioning strategy when the situation changes
- Routes the case to a predefined outcome
- Escalates unresolved high-risk situations instead of guessing

---

## 🧠 Agent Architecture

```text
Patient Input
     ↓
Patient State Manager
     ↓
Risk Assessment
     ↓
Question Planner
     ↓
Ask Next Question
     ↓
Patient Response
     ↓
Update State
     ↓
Reassess Risk
     ↓
Adapt
     ↓
Routing Decision
