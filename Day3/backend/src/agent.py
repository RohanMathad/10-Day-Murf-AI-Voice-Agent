import logging
import json
import os
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    RoomInputOptions,
    WorkerOptions,
    cli,
    function_tool,
    metrics,
    MetricsCollectedEvent,
    tokenize,
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")
load_dotenv(".env.local")


WELLNESS_FILE = "wellness_log.json"


def load_previous_entries():
    """Load JSON file if present"""
    if not os.path.exists(WELLNESS_FILE):
        return []

    try:
        with open(WELLNESS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_entry(entry: dict):
    """Append new entry to the JSON log"""
    entries = load_previous_entries()
    entries.append(entry)

    with open(WELLNESS_FILE, "w") as f:
        json.dump(entries, f, indent=4)

@dataclass
class WellnessState:
    mood: Optional[str] = None
    energy: Optional[str] = None
    goals: List[str] = field(default_factory=list)
    summary: Optional[str] = None

    def is_complete(self):
        return (
            self.mood is not None
            and self.energy is not None
            and len(self.goals) > 0
        )


@dataclass
class Userdata:
    wellness: WellnessState
    previous_entries: list = field(default_factory=load_previous_entries)


@function_tool
async def set_mood(ctx: RunContext[Userdata], mood: str) -> str:
    ctx.userdata.wellness.mood = mood
    return f"Thanks for sharing. I’m noting that you’re feeling **{mood}** today."


@function_tool
async def set_energy(ctx: RunContext[Userdata], energy: str) -> str:
    ctx.userdata.wellness.energy = energy
    return f"Got it — your energy level is **{energy}**."


@function_tool
async def add_goal(ctx: RunContext[Userdata], goal: str) -> str:
    ctx.userdata.wellness.goals.append(goal)
    return f"Adding that goal: **{goal}**."


@function_tool
async def finalize_checkin(ctx: RunContext[Userdata]) -> str:
    """Called ONLY when all fields are complete."""
    wellness = ctx.userdata.wellness

    summary = (
        f"Today you're feeling {wellness.mood}, your energy is {wellness.energy}, "
        f"and your goals are: {', '.join(wellness.goals)}."
    )

    entry = {
        "timestamp": datetime.now().isoformat(),
        "mood": wellness.mood,
        "energy": wellness.energy,
        "goals": wellness.goals,
        "summary": summary,
    }

    save_entry(entry)

    return (
        f"Thanks for checking in! Here's your recap: {summary} "
        "I'll remember this for next time."
    )


@function_tool
async def get_previous_summary(ctx: RunContext[Userdata]) -> str:
    """Returns the last check-in summary if available."""
    prev = ctx.userdata.previous_entries
    if not prev:
        return "This is our first check-in together!"

    last = prev[-1]
    return (
        f"Last time you felt {last['mood']} with {last['energy']} energy. "
        f"Your goals were: {', '.join(last['goals'])}."
    )



class WellnessAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
                You are a warm, grounded, supportive wellness companion.

                👉 At the start of every session, always read the JSON history 
                and naturally mention at least one thing from the user's previous check-ins 
                before asking today’s questions.

                Your goal each day:
                1. Ask about mood
                2. Ask about energy
                3. Ask for 1–3 simple goals for today
                4. Offer realistic, small advice
                5. Create a short recap
                6. Save the recap via finalize_checkin()

                Rules:
                - No medical advice or diagnosis
                - Keep responses simple, human, and encouraging
                - Reference past logs using get_previous_summary() when helpful
                - Use the tools provided to store mood, energy, goals
                - Only call finalize_checkin() when all data is complete

                STRICTLY Dont forget to naturally reference **one or two** past entries in conversation.

            """,
            tools=[set_mood, set_energy, add_goal, finalize_checkin, get_previous_summary],
        )


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):

    userdata = Userdata(wellness=WellnessState())

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(),
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        userdata=userdata,
    )

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def collect(ev: MetricsCollectedEvent):
        usage_collector.collect(ev.metrics)

    await session.start(
        agent=WellnessAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))





