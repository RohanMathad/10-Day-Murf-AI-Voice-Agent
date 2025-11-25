
# Day 3: Health & Wellness Voice Companion

### *10-Day Murf AI Voice Agent Challenge*

## 📌 Overview

**Day 3** introduces a **Health & Wellness Voice Companion**—a supportive, grounded daily check-in agent.
It talks to the user about their mood, energy, and goals, then saves the results into a JSON file.
Next time the agent runs, it reads past entries and mentions previous days naturally.

This entire logic is implemented inside **`backend/src/agent.py`** using LiveKit Agents + Murf Falcon TTS.

---

## 🎯 **Features Completed (Day 3 Requirements)**

### ✔ 1. Daily Voice Check-In Flow

The agent:

* Asks about mood, energy, and stress level
* Asks for 1–3 goals or intentions for today
* Summarizes the day back to the user
* Stores each session’s data persistently

All conversations are fully voice-based using **Murf Falcon (the fastest TTS API)**.

---

### ✔ 2. JSON-Based Persistence

Every session is saved as a structured entry inside:

```
wellness_log.json
```

Each entry contains:

* `timestamp`
* `mood`
* `energy`
* `intentions`
* `summary`

The JSON structure is clean and readable.

---

### ✔ 3. Uses Past Data

At the start of a new day, the agent automatically reads `wellness_log.json` and says things like:

* *“Last time you mentioned low energy. How are you today?”*
* *“Yesterday you planned to focus on rest. Were you able to do that?”*

No diagnosis. No medical claims. Just supportive reference to previous check-ins.

---

### ✔ 4. Realistic Guidance (Non-Medical)

Advice is always:

* small
* practical
* grounded
* non-clinical

Examples:

* *“Break the task into smaller steps.”*
* *“Try taking a 5-minute reset before starting.”*

---

### ✔ 5. Updated Agent Instructions

The `agent.py` contains a carefully designed system prompt to keep the tone warm, supportive, and stable.

---

## 🧠 **Tech Stack**

* **LiveKit Agents** (STT, event loop, session handling)
* **Google Gemini 2.5 Flash** (LLM)
* **Murf Falcon** (TTS – fastest voice engine)
* **Deepgram / Silero** (STT / VAD depending on config)
* **Next.js Frontend** (UI for the voice session)
* **Python (FastAPI + file persistence)**

---

## 📂 Folder Structure (Day 3)

```
Day3/
  ├── backend/
  │   ├── src/
  │   │   └── agent.py   ← Day 3 logic here
  │   └── wellness_log.json (auto created)
  └── frontend/
      └── (UI, voice interface)
```

---

## ▶️ How It Works (Flow)

1. User starts a voice session
2. Agent introduces itself and begins a wellness check-in
3. Collects:

   * Mood
   * Energy level
   * Stress
   * Daily goals
4. Summarizes the day
5. Saves the data in **wellness_log.json**
6. On next session, reads older entries and follows up

---

## 🚀 Running Day 3

### Backend

```bash
cd Day3/backend
uvicorn src.agent:app --reload
```

### Frontend

```bash
cd Day3/frontend
npm install
npm run dev
```

