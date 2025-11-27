# ======================================================
# 🏦 DAY 6: HDFC BANK FRAUD ALERT AGENT
# 🛡️ "HDFC Bank" - Fraud Detection & Resolution
# 🚀 Features: Identity Verification, Database Lookup, Status Updates
# ======================================================

import logging
import json
import os
from datetime import datetime
from typing import Annotated, Optional, List
from dataclasses import dataclass, asdict

print("\n" + "🛡️" * 50)
print("🚀 HDFC BANK FRAUD AGENT - INITIALIZED")
print("📚 TASKS: Verify Identity -> Check Transaction -> Update DB")
print("🛡️" * 50 + "\n")

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

# 🔌 PLUGINS
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")
load_dotenv(".env.local")

# ======================================================
# 💾 1. DATABASE SETUP (Mock Data)
# ======================================================

DB_FILE = "fraud_db.json"

# Schema
@dataclass
class FraudCase:
    userName: str
    securityIdentifier: str
    cardEnding: str
    transactionName: str
    transactionAmount: str
    transactionTime: str
    transactionSource: str
    case_status: str = "pending_review"
    notes: str = ""

def seed_database():
    """Creates HDFC sample fraud cases if DB doesn't exist."""
    path = os.path.join(os.path.dirname(__file__), DB_FILE)
    if not os.path.exists(path):
        sample_data = [
            {
                "userName": "Rohan",
                "securityIdentifier": "88321",
                "cardEnding": "5521",
                "transactionName": "Ecom Traders India",
                "transactionAmount": "₹18,499",
                "transactionTime": "11:45 PM IST",
                "transactionSource": "flipkart.com",
                "case_status": "pending_review",
                "notes": "Auto-flagged: Late-night high-value transaction."
            },
            {
                "userName": "Meera",
                "securityIdentifier": "77291",
                "cardEnding": "9910",
                "transactionName": "CryptoFast Exchange",
                "transactionAmount": "₹82,000",
                "transactionTime": "2:10 AM IST",
                "transactionSource": "online_transfer",
                "case_status": "pending_review",
                "notes": "Auto-flagged: Unusual activity detected."
            }
        ]
        with open(path, "w", encoding='utf-8') as f:
            json.dump(sample_data, f, indent=4)
        print(f"✅ Database seeded at {DB_FILE}")

# Seed fake cases
seed_database()

# ======================================================
# 🧠 2. STATE MANAGEMENT
# ======================================================

@dataclass
class Userdata:
    active_case: Optional[FraudCase] = None

# ======================================================
# 🛠️ 3. FRAUD AGENT TOOLS
# ======================================================

@function_tool
async def lookup_customer(
    ctx: RunContext[Userdata],
    name: Annotated[str, Field(description="Customer name provided by the user")]
) -> str:
    """Looks up a customer in the HDFC fraud DB."""
    print(f"🔎 LOOKING UP: {name}")
    path = os.path.join(os.path.dirname(__file__), DB_FILE)
    
    try:
        with open(path, "r") as f:
            data = json.load(f)
            
        found_record = next((item for item in data if item["userName"].lower() == name.lower()), None)
        
        if found_record:
            ctx.userdata.active_case = FraudCase(**found_record)
            
            return (
                f"Record Found.\n"
                f"HDFC Customer: {found_record['userName']}\n"
                f"Security Identifier (Expected): {found_record['securityIdentifier']}\n"
                f"Suspicious Transaction: {found_record['transactionAmount']} at "
                f"{found_record['transactionName']} ({found_record['transactionSource']})\n"
                f"Instructions: Ask for their Security Identifier to verify identity."
            )
        else:
            return "Customer not found in HDFC fraud records. Ask them to repeat their name."

    except Exception as e:
        return f"Database error: {str(e)}"


@function_tool
async def resolve_fraud_case(
    ctx: RunContext[Userdata],
    status: Annotated[str, Field(description="'confirmed_safe' or 'confirmed_fraud'")],
    notes: Annotated[str, Field(description="Outcome summary")]
) -> str:
    """Saves HDFC case status after user verification."""
    
    if not ctx.userdata.active_case:
        return "Error: No active HDFC fraud case loaded."

    case = ctx.userdata.active_case
    case.case_status = status
    case.notes = notes
    
    path = os.path.join(os.path.dirname(__file__), DB_FILE)

    try:
        with open(path, "r") as f:
            data = json.load(f)
        
        for i, item in enumerate(data):
            if item["userName"] == case.userName:
                data[i] = asdict(case)
                break
        
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
            
        print(f"✅ HDFC CASE UPDATED: {case.userName} -> {status}")
        
        if status == "confirmed_fraud":
            return (
                "Fraud confirmed. Inform the user: "
                f"The HDFC card ending with {case.cardEnding} has been blocked. "
                "A replacement card will be dispatched."
            )
        else:
            return (
                "Marked as SAFE. Inform the user: "
                "The transaction has been approved and restrictions lifted."
            )

    except Exception as e:
        return f"Error saving to DB: {e}"

# ======================================================
# 🤖 4. AGENT DEFINITION
# ======================================================

class FraudAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            You are 'Aarav', a Fraud Prevention Specialist at **HDFC Bank**.
            Your job is to verify a suspicious transaction professionally.
            (Give slow and clear introduction)

            🛡️ HDFC SECURITY CALL FLOW (STRICT):

            1. **GREETING:**
               - Say you are calling from *HDFC Bank Fraud Detection Department*.
               - Ask: "Am I speaking with the account holder? May I know your first name?"

            2. **IMMEDIATE LOOKUP:**
               - Use tool `lookup_customer` as soon as the customer provides their name.

            3. **IDENTITY VERIFICATION:**
               - Ask for their Security Identifier.
               - Compare with the expected identifier.
               - If mismatch → apologize and end call.

            4. **TRANSACTION ALERT:**
               - Read the suspicious HDFC transaction:
                 amount, merchant, time, and source.

            5. **ASK CONFIRMATION:**
               - “Did you authorize this transaction?”

            6. **RESOLUTION:**
               - If YES → call `resolve_fraud_case('confirmed_safe')`
               - If NO → call `resolve_fraud_case('confirmed_fraud')`

            7. **CLOSING:**
               - Confirm outcome and close politely, and say thank you for reaching out to hdfc bank.

            ⚠️ NEVER ask for full card number, OTP, PIN, CVV, or passwords.
            Tone must be calm, secure, professional.
            """,
            tools=[lookup_customer, resolve_fraud_case],
        )

# ======================================================
# 🎬 ENTRYPOINT
# ======================================================

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    print("\n" + "💼" * 25)
    print("🚀 STARTING HDFC FRAUD ALERT SESSION")
    
    userdata = Userdata()

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-marcus",
            style="Conversational",
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        userdata=userdata,
    )
    
    await session.start(
        agent=FraudAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    await ctx.connect()

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
