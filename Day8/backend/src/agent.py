# IMPROVE THE AGENT AS PER YOUR NEED 1
"""
Day 8 – Voice Game Master (Sci-Fi Survival Adventure) - Voice-only GM agent

- Uses LiveKit agent plumbing similar to the provided food_agent_sqlite example.
- GM persona, universe, tone and rules are encoded in the agent instructions.
- Keeps STT/TTS/Turn detector/VAD integration untouched (murf, deepgram, silero, turn_detector).
- Tools:
    - start_adventure(): start a fresh session and introduce the scene
    - get_scene(): return the current scene description (GM text) ending with "What do you do?"
    - player_action(action_text): accept player's spoken action, update state, advance scene
    - show_journal(): list remembered facts, NPCs, named locations, choices
    - restart_adventure(): reset state and start over
- Userdata keeps continuity between turns: history, inventory, named NPCs/locations, choices, current_scene
"""

import json
import logging
import os
import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Optional, Annotated

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

from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# -------------------------
# Logging
# -------------------------
logger = logging.getLogger("voice_game_master")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)

load_dotenv(".env.local")

# -------------------------
# NEW WORLD: Sci-Fi Mini-Arc “Echoes of Titan-Prime”
# -------------------------
WORLD = {
    "intro": {
        "title": "Echoes of Titan-Prime",
        "desc": (
            "Your eyes open inside a half-crashed escape pod. Orange methane fog rolls across "
            "Titan-Prime’s frozen plain. The hull around you is cracked, sparking faintly. "
            "A dim beacon pulses from a ridge to the north, while strange footprints lead toward "
            "a metallic ruin in the west."
        ),
        "choices": {
            "check_pod": {
                "desc": "Inspect the damaged escape pod.",
                "result_scene": "pod",
            },
            "follow_footprints": {
                "desc": "Follow the unknown footprints toward the metallic ruin.",
                "result_scene": "ruin_approach",
            },
            "move_towards_beacon": {
                "desc": "Head north toward the pulsing ridge beacon.",
                "result_scene": "ridge",
            },
        },
    },
    "pod": {
        "title": "Damaged Escape Pod",
        "desc": (
            "Inside the pod you find a cracked datapad flickering with static and a portable "
            "oxygen cell. A message loops: 'Core unit missing… signal compromised… locate source.'"
        ),
        "choices": {
            "take_oxygen": {
                "desc": "Take the oxygen cell.",
                "result_scene": "pod_taken",
                "effects": {"add_inventory": "oxygen_cell", "add_journal": "Collected oxygen cell from pod."},
            },
            "inspect_datapad": {
                "desc": "Try to read the cracked datapad.",
                "result_scene": "datapad",
            },
            "leave_pod": {
                "desc": "Exit the pod and look around.",
                "result_scene": "intro",
            },
        },
    },
    "pod_taken": {
        "title": "Supplies Secured",
        "desc": (
            "You secure the oxygen cell to your suit. Automated vents hiss as pressure stabilizes. "
            "The datapad sparks again, pointing west—toward the metallic ruin."
        ),
        "choices": {
            "go_to_ruin": {
                "desc": "Head toward the metallic ruin.",
                "result_scene": "ruin_approach",
            },
            "check_datapad": {
                "desc": "Inspect the datapad more closely.",
                "result_scene": "datapad",
            },
        },
    },
    "datapad": {
        "title": "Glitched Datapad",
        "desc": (
            "The screen stabilizes long enough to show a single coordinate and a warning: "
            "'Power Core displaced. Entity detected.' A faint map overlay points west."
        ),
        "choices": {
            "follow_map": {
                "desc": "Follow the datapad map to the west.",
                "result_scene": "ruin_approach",
            },
            "return_outside": {
                "desc": "Return outside the escape pod.",
                "result_scene": "intro",
            },
        },
    },
    "ruin_approach": {
        "title": "Approaching the Metallic Ruin",
        "desc": (
            "The ruin hums with a soft vibration. A fractured door panel lies open, and strange "
            "claw-like marks run across the metal. Something inside emits a rhythmic signal."
        ),
        "choices": {
            "enter_ruin": {
                "desc": "Enter the metallic ruin.",
                "result_scene": "ruin_inside",
            },
            "scan_area": {
                "desc": "Scan the surroundings for movement.",
                "result_scene": "scan",
            },
            "retreat": {
                "desc": "Retreat back to the escape pod.",
                "result_scene": "intro",
            },
        },
    },
    "scan": {
        "title": "Brief Scan",
        "desc": (
            "Your suit scanner picks up a heat signature inside the ruin—small, fast-moving, "
            "possibly non-hostile. The rhythmic signal spikes momentarily."
        ),
        "choices": {
            "enter_ruin": {
                "desc": "Enter the metallic ruin cautiously.",
                "result_scene": "ruin_inside",
            },
            "wait_outside": {
                "desc": "Wait outside and observe.",
                "result_scene": "ridge",
            },
        },
    },
    "ridge": {
        "title": "Beacon Ridge",
        "desc": (
            "The ridge beacon emits short coded bursts. A metal crate lies half-buried nearby, "
            "and the atmosphere crackles with static."
        ),
        "choices": {
            "open_crate": {
                "desc": "Try to open the metal crate.",
                "result_scene": "crate",
            },
            "follow_signal": {
                "desc": "Follow the beacon signal pattern.",
                "result_scene": "ruin_approach",
            },
            "return_back": {
                "desc": "Return toward the crash site.",
                "result_scene": "intro",
            },
        },
    },
    "crate": {
        "title": "Supply Crate",
        "desc": (
            "Inside the crate you find a glowing tri-core module. Your suit identifies it as the "
            "missing Power Core mentioned by the datapad."
        ),
        "choices": {
            "take_core": {
                "desc": "Take the tri-core module.",
                "result_scene": "core_obtained",
                "effects": {"add_inventory": "tri_core_module", "add_journal": "Recovered main Power Core."},
            },
            "leave_crate": {
                "desc": "Leave the crate undisturbed.",
                "result_scene": "ridge",
            },
        },
    },
    "core_obtained": {
        "title": "Power Core Secured",
        "desc": (
            "With the Power Core secured, the beacon shifts tone—almost relieved. A debug message "
            "appears on your suit: 'Return Core to Ruin Chamber for extraction.'"
        ),
        "choices": {
            "go_to_ruin": {
                "desc": "Head to the ruin chamber.",
                "result_scene": "ruin_inside",
            },
            "return_pod": {
                "desc": "Take the core back to the escape pod.",
                "result_scene": "end_arc",
            },
        },
    },
    "ruin_inside": {
        "title": "Inside the Ruin",
        "desc": (
            "You enter a circular chamber filled with cracked machinery. At its center, a socket matches "
            "the shape of your tri-core module. A faint mechanical voice repeats: 'Restore… restore… restore…'"
        ),
        "choices": {
            "insert_core": {
                "desc": "Insert the tri-core module into the socket.",
                "result_scene": "end_arc",
                "effects": {"add_journal": "Core restored. System reboot initiated."},
            },
            "inspect_room": {
                "desc": "Look for other clues in the room.",
                "result_scene": "room_scan",
            },
            "retreat": {
                "desc": "Retreat back outside the ruin.",
                "result_scene": "ruin_approach",
            },
        },
    },
    "room_scan": {
        "title": "Room Scan",
        "desc": (
            "You find inscriptions describing an extinct research crew that once lived here. "
            "A symbol on the wall resembles the tri-core module."
        ),
        "choices": {
            "insert_core": {
                "desc": "Insert the tri-core module.",
                "result_scene": "end_arc",
            },
            "leave_room": {
                "desc": "Leave the room.",
                "result_scene": "ruin_approach",
            },
        },
    },
    "end_arc": {
        "title": "Mini-Arc Complete",
        "desc": (
            "As the Power Core activates, the ruin lights up. Your suit projects a safe extraction route. "
            "A calm hum spreads through the ground—this chapter of Titan-Prime’s mystery concludes… for now."
        ),
        "choices": {
            "restart": {
                "desc": "Restart the adventure.",
                "result_scene": "intro",
            },
            "explore_more": {
                "desc": "Continue exploring the world.",
                "result_scene": "intro",
            },
        },
    },
}

# -------------------------
# Per-session Userdata
# -------------------------
@dataclass
class Userdata:
    player_name: Optional[str] = None
    current_scene: str = "intro"
    history: List[Dict] = field(default_factory=list)
    journal: List[str] = field(default_factory=list)
    inventory: List[str] = field(default_factory=list)
    named_npcs: Dict[str, str] = field(default_factory=dict)
    choices_made: List[str] = field(default_factory=list)
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

# -------------------------
# Helper functions
# -------------------------
def scene_text(scene_key: str, userdata: Userdata) -> str:
    scene = WORLD.get(scene_key)
    if not scene:
        return "You are in a featureless void. What do you do?"

    desc = f"{scene['desc']}\n\nChoices:\n"
    for cid, cmeta in scene.get("choices", {}).items():
        desc += f"- {cmeta['desc']} (say: {cid})\n"

    desc += "\nWhat do you do?"
    return desc

def apply_effects(effects: dict, userdata: Userdata):
    if not effects:
        return
    if "add_journal" in effects:
        userdata.journal.append(effects["add_journal"])
    if "add_inventory" in effects:
        userdata.inventory.append(effects["add_inventory"])

def summarize_scene_transition(old_scene: str, action_key: str, result_scene: str, userdata: Userdata) -> str:
    entry = {
        "from": old_scene,
        "action": action_key,
        "to": result_scene,
        "time": datetime.utcnow().isoformat() + "Z",
    }
    userdata.history.append(entry)
    userdata.choices_made.append(action_key)
    return f"You chose '{action_key}'."

# -------------------------
# Tools
# -------------------------

@function_tool
async def start_adventure(
    ctx: RunContext[Userdata],
    player_name: Annotated[Optional[str], Field(description="Player name", default=None)] = None,
) -> str:
    userdata = ctx.userdata
    if player_name:
        userdata.player_name = player_name

    userdata.current_scene = "intro"
    userdata.history = []
    userdata.journal = []
    userdata.inventory = []
    userdata.named_npcs = {}
    userdata.choices_made = []
    userdata.session_id = str(uuid.uuid4())[:8]
    userdata.started_at = datetime.utcnow().isoformat() + "Z"

    opening = (
        f"Welcome {userdata.player_name or 'traveler'} to Titan-Prime.\n\n"
        + scene_text("intro", userdata)
    )
    if not opening.endswith("What do you do?"):
        opening += "\nWhat do you do?"
    return opening

@function_tool
async def get_scene(ctx: RunContext[Userdata]) -> str:
    userdata = ctx.userdata
    return scene_text(userdata.current_scene, userdata)

@function_tool
async def player_action(
    ctx: RunContext[Userdata],
    action: Annotated[str, Field(description="Player spoken action or action key")],
) -> str:
    userdata = ctx.userdata
    current = userdata.current_scene
    scene = WORLD.get(current)
    action_text = (action or "").strip().lower()

    chosen_key = None

    if action_text in (scene.get("choices") or {}):
        chosen_key = action_text
    if not chosen_key:
        for cid, cmeta in (scene.get("choices") or {}).items():
            desc = cmeta.get("desc", "").lower()
            if cid in action_text or any(w in action_text for w in desc.split()[:4]):
                chosen_key = cid
                break
    if not chosen_key:
        for cid, cmeta in (scene.get("choices") or {}).items():
            for keyword in cmeta.get("desc", "").lower().split():
                if keyword and keyword in action_text:
                    chosen_key = cid
                    break
            if chosen_key:
                break

    if not chosen_key:
        resp = (
            "I couldn't match that action. Try one of the listed choices.\n\n"
            + scene_text(current, userdata)
        )
        return resp

    choice_meta = scene["choices"][chosen_key]
    result_scene = choice_meta.get("result_scene", current)
    effects = choice_meta.get("effects", None)

    apply_effects(effects or {}, userdata)
    note = summarize_scene_transition(current, chosen_key, result_scene, userdata)

    userdata.current_scene = result_scene
    next_desc = scene_text(result_scene, userdata)

    persona = "Sigma-4 (your calm sci-fi Game Master) says:\n\n"
    reply = f"{persona}{note}\n\n{next_desc}"

    if not reply.endswith("What do you do?"):
        reply += "\nWhat do you do?"
    return reply

@function_tool
async def show_journal(ctx: RunContext[Userdata]) -> str:
    userdata = ctx.userdata
    lines = []
    lines.append(f"Session: {userdata.session_id} | Started at: {userdata.started_at}")
    if userdata.player_name:
        lines.append(f"Player: {userdata.player_name}")
    if userdata.journal:
        lines.append("\nJournal entries:")
        for j in userdata.journal:
            lines.append(f"- {j}")
    else:
        lines.append("\nJournal is empty.")
    if userdata.inventory:
        lines.append("\nInventory:")
        for it in userdata.inventory:
            lines.append(f"- {it}")
    else:
        lines.append("\nNo items in inventory.")
    lines.append("\nRecent choices:")
    for h in userdata.history[-6:]:
        lines.append(f"- {h['time']} | from {h['from']} -> {h['to']} via {h['action']}")
    lines.append("\nWhat do you do?")
    return "\n".join(lines)

@function_tool
async def restart_adventure(ctx: RunContext[Userdata]) -> str:
    userdata = ctx.userdata
    userdata.current_scene = "intro"
    userdata.history = []
    userdata.journal = []
    userdata.inventory = []
    userdata.named_npcs = {}
    userdata.choices_made = []
    userdata.session_id = str(uuid.uuid4())[:8]
    userdata.started_at = datetime.utcnow().isoformat() + "Z"

    greet = (
        "The simulation resets. The fog rolls anew. You stand at the beginning once more.\n\n"
        + scene_text("intro", userdata)
    )
    if not greet.endswith("What do you do?"):
        greet += "\nWhat do you do?"
    return greet

# -------------------------
# Agent
# -------------------------
class GameMasterAgent(Agent):
    def __init__(self):
        instructions = """
        You are 'Sigma-4', the AI Game Master for a voice-only sci-fi survival adventure.
        Universe: Titan-Prime — a frozen exoplanet with crashed pods, abandoned research ruins, and unknown signals.
        Tone: Calm, atmospheric, slightly mysterious.
        Role: You describe scenes vividly based on the WORLD map, remember choices, journal items, and always end with 'What do you do?'.

        Rules:
            - Use tools to start adventures, get scenes, process actions, show journals, or restart.
            - Maintain continuity using per-session userdata.
            - Voice-first responses: clear, short, immersive.
            - NEVER forget to end with: "What do you do?"
        """
        super().__init__(
            instructions=instructions,
            tools=[start_adventure, get_scene, player_action, show_journal, restart_adventure],
        )

# -------------------------
# Entrypoint
# -------------------------
def prewarm(proc: JobProcess):
    try:
        proc.userdata["vad"] = silero.VAD.load()
    except Exception:
        logger.warning("VAD prewarm failed; continuing without VAD.")

async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}
    logger.info("\n" + "🚀" * 4)
    logger.info("STARTING VOICE GAME MASTER – TITAN-PRIME EDITION")

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
        vad=ctx.proc.userdata.get("vad"),
        userdata=userdata,
    )

    await session.start(
        agent=GameMasterAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
    )

    await ctx.connect()

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
