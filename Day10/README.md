# 🎭 **Day 10 – Voice Improv Battle**

A high-energy, voice-first improv game built using **LiveKit Agents**, **Murf TTS**, **Gemini LLM**, and **Deepgram STT**.

This experience lets a user join from the browser, speak with an AI host, and perform short improv scenes. The host reacts dynamically, moves through multiple rounds, and finally gives a summary of the player’s improv style.

---

## 🚀 **Primary Goal**

Build a **single-player improv game show** where:

* The user joins from a web browser
* They enter their stage name
* The AI becomes a TV show host
* The host gives improv scenarios
* The player performs
* The host reacts (supportive, neutral, mildly critical)
* The game runs for 3–5 rounds
* The host ends with a closing summary

This completes the required Day 10 challenge.

---

# 🧩 **Core Features Implemented**

### ✅ **1. Full Improv Host Persona**

The agent follows a strong persona:

* High-energy
* Witty
* Slightly teasing
* Gives rules clearly
* Moves the game forward
* Generates dynamic reactions

---

### ✅ **2. Full Game State Management**

Each session tracks:

* Player name
* Current round
* Total rounds
* Scenarios used
* Player performances
* Host reactions
* Game phases: `intro → awaiting_improv → reacting → done`

Everything resets cleanly when the show ends.

---

### ✅ **3. Scenario Engine**

A curated set of improv prompts, each including:

* Role
* Situation
* Tension / hook

Scenarios are randomized and no repeats occur until all scenarios are used.

---

### ✅ **4. Scene Recording & Reactions**

When the user finishes (saying *“End scene”*), the agent:

* Records performance
* Generates reaction text with varied tone
* Preps next round
* Ends the show automatically on last round

Reaction tone is dynamic:

* Supportive
* Neutral
* Mildly critical
* Always safe & constructive

---

### ✅ **5. Closing Summary**

When rounds end, the host:

* Summarizes performance
* Highlights specific moments
* Builds a profile of the player’s style
* Delivers a show-style outro

---

### ✅ **6. Polished UI**

We customized the UI:

* Left-aligned hero title (**Improv Battle**)
* Neon-themed purple card on the right
* Smooth motion transitions
* Floating icons and glow effects
* Animated pre-connect message
* Updated **PlayerBadge** showing stage name

---

### ✅ **7. Full Voice Pipeline**

Under the hood, the entire voice stack is running:

* **Deepgram STT** – real-time speech-to-text
* **Murf TTS** – natural voice output
* **Gemini 2.5 Flash** – the brain of the improv host
* **Silero VAD** – voice activity detection
* **LiveKit Turn Detector** – detects scene completion
* **Noise cancellation** – BVC for clean audio

---

# 🎮 **How the Gameplay Works**

### **Round Flow**

1. Host introduces rules
2. Host gives scenario
3. Player performs
4. Player says **“End scene”**
5. Host reacts
6. Host moves to next scenario
7. After final round → summary

### **Early Exit**

Player can say:

**“Stop show”**
AI confirms → ends session

---

# 🔧 **Files Updated Today**

We modified multiple files for Day 10:

### **Backend (Agent)**

* `agent.py` → full improv logic
* State management
* Tools for LLM control

### **Frontend**

* `welcome-view.tsx` → hero left + card right
* `session-view.tsx` → UI theme & badge
* `tile-layout.tsx` → visuals & animations
* `preconnect-message.tsx` → custom text
* `view-controller.tsx` → correct transitions
* `player-badge.tsx` → stage name support
* `session-provider` & `useRoom` → minor flow fixes

Everything works smoothly with no breaking changes.

---

# 🧪 **How to Test**

### **Script to follow**

1. “Start the Improv Battle. My name is ___.”
2. Act → “End scene.”
3. “Next round.”
4. Act → “End scene.”
5. “Next round.”
6. Final act → “End scene.”
7. “End the show.”

This tests all game phases.

---

# 🏁 **Day 10 Complete**

We now have a fully functional **single-player improv battle game** with:

* Voice agent host
* Dynamic improv scenarios
* Real-time reactions
* Animated visual UI
* Clean round flow
* Full summary output

This completes **Day 10’s primary goal**.