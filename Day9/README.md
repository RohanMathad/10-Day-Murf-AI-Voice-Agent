# **🛍️ Day 9 – Voice Commerce Agent (ACP-Inspired)**

This project implements a **voice-driven shopping assistant** powered by a lightweight version of the **Agentic Commerce Protocol (ACP)**.
The goal for Day 9 was to build a **fully interactive e-commerce agent** that understands voice commands, browses a product catalog, manages a cart, and creates persistent orders.

---

## **🎯 Primary Features**

### **1. Voice-Powered Catalog Search**

The user can ask:

* “Show me coffee mugs.”
* “Any earphones?”
* “Do you have table lamp under 300?”

The agent:

* Interprets intent using Gemini
* Calls backend merchant functions (`list_products`)
* Returns a short, voice-friendly product summary

---

### **2. Smart Cart System**

Supports:

* Adding items by ID or spoken reference
  (“Add the second hoodie”, “Add mug-001, quantity 2”)
* Viewing cart contents
* Clearing the cart

All cart data is stored per session.

---

### **3. Order Creation & Persistence**

Backend generates structured order objects:

* `order_id`
* Product line items
* Quantity & unit prices
* Total cost
* Currency (INR)
* Timestamp

Orders are saved to **orders.json** automatically.

Example voice prompt:

> “Place my order.”

---

### **4. Order History Lookup**

The user can ask:

* “What did I just buy?”
* “Show my latest order.”

Agent reads the most recent order from disk.

---

## **📁 Key Backend Components**

**`agent.py`** includes:

* Product catalog (structured ACP-style)
* Catalog filtering logic
* Cart functions
* Order creation + persistence
* Recent order lookup
* Full Ramu Kaka voice agent (shopkeeper persona)
* LiveKit session entrypoint

---

## **📽️ Demo Flow Shown in Video**

1. Start the agent
2. Ask to explore catalog
3. Add items using natural language
4. Show cart
5. Place the order
6. Confirm by checking `orders.json`
7. Ask “What did I just buy?”

---

## **🏁 Day 9 Completed**

This day introduced a real commerce workflow with:

* Natural conversation
* Structured backend logic
* Persistent order storage
* ACP-inspired separation between conversation and merchant logic

All powered by ultra-fast **Murf Falcon** TTS for real-time voice experiences.
