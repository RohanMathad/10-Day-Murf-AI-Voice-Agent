# **Day 7 – Food & Grocery Voice Ordering Agent (Zomato Style)**

This project implements a **voice-controlled food & grocery ordering assistant** inspired by Zomato. The agent understands natural speech, manages a shopping cart, and stores orders using a **SQLite database**.

## **✨ Features Implemented**

* **Interactive Voice Ordering**

  * Add items, update quantities, and remove items from the cart.
  * Search items from the catalog using natural language.

* **Smart “Ingredients for X” Handling**

  * Auto-detects items required for common dishes (e.g., sandwich, pasta, chai).
  * Adds all ingredients instantly to the cart.

* **Cart Management**

  * Add, update, remove, and display items.
  * Real-time cart totals.

* **Order Placement**

  * Saves final orders in `order_db.sqlite` with:

    * Items
    * Quantity
    * Total price
    * Timestamp
    * Status

* **Order Tracking (Mock Simulation)**

  * Status updates over time: *received → confirmed → shipped → out_for_delivery → delivered*.
  * User can ask: “Where is my order?”

* **Order History**

  * Retrieve previous orders stored in the SQLite database.

## **🛠 Tech Stack**

* **LiveKit Agents**
* **Murf Falcon TTS**
* **Deepgram STT**
* **Gemini 2.5 (Google LLM)**
* **SQLite (order_db.sqlite)**
* **Next.js Frontend (Zomato-themed UI)**

---