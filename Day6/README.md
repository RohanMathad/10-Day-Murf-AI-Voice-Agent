# Day 6 – HDFC Bank Fraud Alert Voice Agent

AI Voice Agent Challenge – Murf AI (10 Days of Voice Agents)

This project implements a **Fraud Alert Voice Agent** for **HDFC Bank**, built using **LiveKit Voice Agents**, **Google Gemini**, **Deepgram STT**, and the **fastest TTS API — Murf Falcon**.

The agent automatically calls a customer (browser-based for MVP), verifies their identity via a safe field (Security Identifier), reads a suspicious transaction from a database, and updates the status based on the user's response.

---

## 🎯 Primary Goal (MVP) — Completed

This implementation fully achieves the primary goal:

### ✔ Fake fraud cases stored in JSON database

Each record contains:

* User name
* Security Identifier
* Card ending
* Transaction details (amount, merchant, location, time)
* Current status (`pending_review`)
* Notes

### ✔ Agent loads user case dynamically

When the call starts:

* The agent asks for the name
* Uses `lookup_customer` (tool) to fetch the fraud record
* Saves it in session state

### ✔ Secure identity verification

The agent:

* Asks for Security Identifier
* Verifies against DB
* Continues or ends the call safely

### ✔ Suspicious transaction review

The agent reads:

* Amount
* Merchant
* Time
* Transaction source
* Card ending

### ✔ User confirmation (YES/NO)

The agent asks:

> “Did you authorize this transaction?”

### ✔ DB Update

Based on the answer:

* YES → `confirmed_safe`
* NO → `confirmed_fraud`

Database file updates automatically with outcome notes.

### ✔ Full working video demo completed

Showing:

* Conversation
* Tool calls
* Updated fraud database

---

## 🧩 Tools Implemented

### 1️⃣ `lookup_customer`

* Searches database by username
* Loads fraud case into session
* Returns verification details

### 2️⃣ `resolve_fraud_case`

* Accepts status: `confirmed_safe` / `confirmed_fraud`
* Updates DB
* Returns agent instructions (e.g., “card blocked”)

---

## 🏦 HDFC-Themed Frontend

The Day 6 UI includes:

* HDFC logo
* HDFC blue gradient background
* Red/blue buttons
* Tailwind global theme mapped to banking colors

---