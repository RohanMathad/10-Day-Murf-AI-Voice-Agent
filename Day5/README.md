# 📄 **Day 5: AI SDR Voice Agent (Murf AI Voice Agent Challenge)**

## ⭐ Overview

Day 5 focuses on building a **voice-based Sales Development Representative (SDR)** that can answer product FAQs, qualify leads, and automatically generate a structured lead summary.
The agent is powered by **Murf Falcon (fastest TTS API)**, LiveKit turns, STT, LLM prompting, and a simple JSON database.

For this task, I created an SDR agent for **Lenskart**, using a real FAQ dataset and natural qualification flow.

---

## 🎯 **Primary Goal Completed**

### ✔️ Voice SDR for a real Indian startup

Startup chosen: **Lenskart**
The agent acts as a professional SDR named **Asha**, representing Lenskart.

### ✔️ FAQ Retrieval

* Loaded Lenskart FAQs from a local JSON file (`lenskart_faq.json`)
* Agent answers questions based strictly on FAQ content
* No hallucination; fallback line: *“I’ll check with the Lenskart team and follow up by email.”*

### ✔️ Lead Capture

The agent naturally collects the following fields:

* Name
* Company
* Email
* Role
* Use-case / requirement
* Team size
* Purchase timeline

Each field is captured using the internal function tool `update_lead_profile`.

### ✔️ Lead Storage

* Saved in `lenskart_leads.json`
* Appended with timestamp
* Auto-generated end-of-call summary


## 🧩 **Key Features**

* Natural SDR persona
* FAQ-driven responses
* Keyword-based retrieval
* Smart qualification
* JSON lead database
* Smooth handoff + clean summary
* Fully voice interactive

---

## 📂 **Repository Structure**

```
/day5
  ├── agent.py               # Day 5 SDR logic
  ├── lenskart_faq.json      # FAQ knowledge base
  ├── lenskart_leads.json    # Auto-generated leads
  ├── README.md              # Documentation
  └── .env.local             # API keys (not committed)
```

## 🏁 **Completion for Day 5**

* 🟢 FAQ retrieval pipeline built
* 🟢 SDR persona created
* 🟢 Lead qualification completed
* 🟢 Lead JSON saved
* 🟢 Clean summary generated
* 🟢 Video recorded and posted on LinkedIn
* 🟢 Murf Falcon mention added
* 🟢 Submission link completed
