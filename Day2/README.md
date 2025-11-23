# Day 2 – Coffee Shop Barista Voice Agent

(10-Day Murf AI Voice Agent Challenge)

Today’s task was to extend the voice agent into a fully functional **Coffee Shop Barista** that can:
✔ listen to the user
✔ understand the coffee order
✔ store each detail using tool calls
✔ and finally **save the completed order as a JSON file** using a FastAPI backend.

---

## **✔ What I Built Today**

### **1️⃣ Voice Agent Improvements**

* Added a new tool: `send_order_to_server()`
* After the agent collects **drink type, size, milk, extras, and customer name**, it automatically sends the order to the backend.
* Removed old file-writing logic from `agent.py` (since backend handles saving now).

---

## **2️⃣ FastAPI Backend for Saving Orders**

Created a new backend service:

```
Day2/backend/src/save_order.py
```

### **API Endpoint**

`POST http://localhost:5000/save`

### **What it does**

* Receives order data from the agent
* Stores it as a **JSON file** inside the backend folder
* Files are saved as:

```
order_YYYYMMDD_HHMMSS.json
```

---

## **3️⃣ Technologies Used Today**

### **🟣 Murf Falcon (Fastest TTS API)**

* Using **Murf Falcon** for ultra-fast text-to-speech responses
* Makes the barista feel instant and natural

### **⚡ LiveKit**

* Handles real-time voice
* Turn detection
* Preemptive generation
* Smooth user-agent interaction

### **🎧 Deepgram STT**

* For accurate live speech-to-text

### **🧠 Gemini 2.5 Flash**

* For fast and smart LLM responses

### **🟦 FastAPI**

* Lightweight backend to store orders

---

## **4️⃣ Folder Structure for Day 2**

```
Day2/
├── backend/
│   ├── src/
│   │   ├── agent.py        ← Main voice agent
│   │   └── save_order.py   ← FastAPI order-saving service
│   └── ...
├── frontend/
└── ...
```

---

## **5️⃣ How to Run**

### **Start Backend Server**

```
cd Day2/backend
uvicorn src.save_order:app --port 5000
```

### **Start Voice Agent**

```
uv run python src/agent.py dev
```

---

## **6️⃣ Demo Flow**

User speaks their order:

> “I want a medium latte with oat milk and whipped cream.
> My name is Ram.”

Agent fills the order step-by-step and finally says:

> “Your order is complete! Sending it to the kitchen now.”

JSON file gets created in backend folder:

```
order_20251123_114102.json
```

---

## **⭐ Day 2 Completed!**

Core achievements:

* Fully automated data flow
* Tool-enabled agent memory
* Backend integration
* Real JSON file output
* Ultra-fast Murf Falcon TTS responses

Excited for Day 3! 🚀

---
