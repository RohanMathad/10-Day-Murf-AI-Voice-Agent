# ======================================================
# DAY 5 – LENSKART SDR (NATURAL CONVERSATION + LEAD CAPTURE)
# ======================================================

import logging
import json
import os
from datetime import datetime
from typing import Annotated, Optional
from dataclasses import dataclass, asdict

from dotenv import load_dotenv
from pydantic import Field
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    function_tool,
    RunContext,
)

# Plugins
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lenskart_sdr")

load_dotenv(".env.local")

# ======================================================
# FAQ
# ======================================================

FAQ_FILE = "lenskart_faq.json"
LEADS_FILE = "lenskart_leads.json"

DEFAULT_FAQ = [
    {
        "question": "What does Lenskart offer?",
        "answer": "Lenskart provides prescription eyeglasses, sunglasses, contact lenses, frames, and free in-store eye tests."
    },
    {
        "question": "Do you have home eye tests?",
        "answer": "Yes, Lenskart offers home eye tests with a small convenience fee."
    },
    {
        "question": "Can I try frames at home?",
        "answer": "Yes, Lenskart allows you to try up to 5 frames at home for free."
    },
    {
        "question": "What is the price range for glasses?",
        "answer": "Frames start from a few hundred rupees and premium models go higher."
    },
    {
        "question": "How much do contact lenses cost?",
        "answer": "Contact lenses start from around ₹100–₹200 depending on brand."
    }
]


def load_faq():
    path = os.path.join(os.path.dirname(__file__), FAQ_FILE)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_FAQ, f, indent=4)
    with open(path, "r", encoding="utf-8") as f:
        return json.dumps(json.load(f))


FAQ_TEXT = load_faq()

# ======================================================
# LEAD MODEL
# ======================================================

@dataclass
class LeadProfile:
    name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    use_case: Optional[str] = None
    team_size: Optional[str] = None
    timeline: Optional[str] = None


@dataclass
class Userdata:
    lead_profile: LeadProfile


# ======================================================
# TOOLS
# ======================================================

@function_tool
async def update_lead_profile(
    ctx: RunContext[Userdata],
    name: Annotated[Optional[str], Field(description="Customer name")] = None,
    company: Annotated[Optional[str], Field(description="Company name")] = None,
    email: Annotated[Optional[str], Field(description="Email address")] = None,
    role: Annotated[Optional[str], Field(description="Job role")] = None,
    use_case: Annotated[Optional[str], Field(description="Use-case or interest")] = None,
    team_size: Annotated[Optional[str], Field(description="Team size")] = None,
    timeline: Annotated[Optional[str], Field(description="Timeline")] = None,
) -> str:

    p = ctx.userdata.lead_profile

    if name: p.name = name
    if company: p.company = company
    if email: p.email = email
    if role: p.role = role
    if use_case: p.use_case = use_case
    if team_size: p.team_size = team_size
    if timeline: p.timeline = timeline

    logger.info("LEAD UPDATED: %s", p)
    return "Lead info updated."


@function_tool
async def submit_lead_and_end(ctx: RunContext[Userdata]) -> str:

    p = ctx.userdata.lead_profile
    db_path = os.path.join(os.path.dirname(__file__), LEADS_FILE)

    entry = asdict(p)
    entry["timestamp"] = datetime.utcnow().isoformat() + "Z"

    if os.path.exists(db_path):
        with open(db_path, "r") as f:
            db = json.load(f)
    else:
        db = []

    db.append(entry)

    with open(db_path, "w") as f:
        json.dump(db, f, indent=4)

    logger.info("LEAD SAVED: %s", entry)

    return (
        f"Thanks {p.name}. I’ve saved your details. "
        f"We will reach out to you at {p.email}. Have a great day!"
    )


# ======================================================
# SDR AGENT — NATURAL + STRICT LEAD COLLECTION
# ======================================================

class LenskartSDRAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions=f"""
You are **Asha**, a warm and friendly SDR for Lenskart.

### YOUR GOALS:
1. Answer user questions ONLY from this FAQ:
{FAQ_TEXT}

2. Collect these lead fields NATURALLY during the conversation:
   - Name
   - Company
   - Email (must record exactly as spoken)
   - Role
   - Use-case
   - Team size
   - Timeline

3. IMPORTANT:
   ✔ Do NOT ask all questions at the start  
   ✔ Ask naturally during the conversation  
   ✔ After answering ANY question, gently collect the next missing lead detail  
   ✔ If the user gives a detail, IMMEDIATELY call update_lead_profile()  
   ✔ Do NOT guess information  
   ✔ Do NOT hallucinate anything outside FAQ  

4. ENDING:
   When the user says phrases like:
   - “that's all”
   - “I'm done”
   - “thank you”
   - “you can save this”
   You MUST call submit_lead_and_end()

5. EMAIL HANDLING:
   If the user speaks email like “sam at gmail dot com”, convert it properly to:
   sam@gmail.com

   If the user says “at rate”, “dot”, etc. — convert them to @ and . correctly.

6. CONVERSATION STYLE:
   - Friendly
   - Helpful
   - Natural SDR behavior
   - Never interrogate
   - Never force rapid-fire questions
   - But ensure ALL 7 fields are eventually collected before ending

""",
            tools=[update_lead_profile, submit_lead_and_end],
        )


# ======================================================
# ENTRYPOINT
# ======================================================

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    userdata = Userdata(lead_profile=LeadProfile())

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-natalie",
            style="Friendly",
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        userdata=userdata,
    )

    await session.start(
        agent=LenskartSDRAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm)
    )
