# Day 6 – HDFC Bank Fraud Alert Voice Agent (SQLite)

This project implements a **Fraud Alert Voice Agent** for **HDFC Bank** using **LiveKit Voice Agents**, **SQLite**, **Deepgram STT**, **Google Gemini**, and the **fastest TTS API — Murf Falcon**.

The agent loads suspicious transactions from a SQLite database, verifies the customer, explains the flagged transaction, and updates the fraud status based on the user’s voice response.

---

## ✅ Features

* Loads fraud cases from **SQLite database**
* Safe identity verification using Security Identifier
* Reads suspicious transaction details
* Asks user to confirm if the transaction is legitimate
* Updates case in DB as:

  * `confirmed_safe`
  * `confirmed_fraud`
* Fully voice-driven using LiveKit
* Uses Murf Falcon TTS for fast, natural responses

---

## 🔧 Tech Stack

* **Python 3**
* **SQLite**
* **LiveKit Agents SDK**
* **Murf Falcon (TTS)**
* **Deepgram Nova-3 (STT)**
* **Google Gemini 2.5 Flash (LLM)**

---

## ▶️ Running the Project

### Backend

```bash
cd Day6/backend
uv run src/agent.py
```

### Frontend

```bash
cd Day6/frontend
pnpm install
pnpm dev
```

Open:

```
http://localhost:3000
```

---

## 📦 Database

Fraud cases are stored in:

```
fraud_db.sqlite
```

Sample entries include:

* Customer name
* Security Identifier
* Card ending
* Merchant
* Amount
* Timestamp
* Transaction source
* Current status

---

## 🎥 Demo Includes

* Voice conversation with the agent
* Verification flow
* Fraud/safe confirmation
* Updated SQLite records

---

---

## 🏦 HDFC-Themed Frontend

The Day 6 UI includes:

* HDFC logo
* HDFC blue gradient background
* Red/blue buttons
* Tailwind global theme mapped to banking colors

---