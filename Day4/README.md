# 🎙️ Day 1 — Murf AI Voice Agents Challenge

This is my **Day 1 project** for the Murf AI Voice Agents Challenge.

## ⭐ What I Built Today
A complete **real-time voice agent** using:

- 🧠 **Google Gemini** — LLM for generating intelligent responses  
- 🎧 **Deepgram** — Speech-to-text  
- 🔊 **Murf Falcon** — Ultra-fast text-to-speech  
- 🔗 **LiveKit** — Real-time audio pipeline  
- 💻 **Next.js Frontend** — Voice UI with microphone streaming  

## 🚀 What It Can Do
- Listens to the user’s voice  
- Converts it to text  
- Processes with Gemini  
- Responds immediately using Murf Falcon  
- Works entirely in real-time  

## 🗂️ How To Run (Local)
1. Start LiveKit server: ten-days-of-voice-agents-2025-main file
   ```bash
   .\livekit-server.exe --dev
   ```
3. Run backend:
   ```bash
   uv run python src/agent.py dev
   ```
4. Run Frontend
   ```bash
   pnpm dev
   ```

<img width="1075" height="689" alt="1" src="https://github.com/user-attachments/assets/081b71cb-4853-4c75-a0ef-4870d202757a" />
<img width="1066" height="584" alt="2" src="https://github.com/user-attachments/assets/690c2aa4-125d-4b2b-86e5-70738131c79c" />
