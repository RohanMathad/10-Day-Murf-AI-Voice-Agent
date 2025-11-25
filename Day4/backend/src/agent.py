import logging
import json
import os
import asyncio
from typing import Annotated, Literal, Optional
from dataclasses import dataclass

print("\n" + "💻" * 50)
print("🚀 PROGRAMMING TUTOR - DAY 4")
print("📚 Knowledge base: Java & DSA topics")
print("💡 agent.py LOADED SUCCESSFULLY!")
print("💻" * 50 + "\n")

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

logger = logging.getLogger("agent")
load_dotenv(".env.local")


CONTENT_FILE = "cs_content.json"

DEFAULT_CONTENT = [
  {
    "id": "java_basics",
    "title": "Java Basics",
    "summary": "Java is an object-oriented, class-based programming language used for building cross-platform applications. Key elements include classes, objects, methods, and strong typing.",
    "sample_question": "What are the main features of Java and why is it called 'write once, run anywhere'?"
  },
  {
    "id": "oop",
    "title": "Object-Oriented Programming (Java)",
    "summary": "OOP in Java uses classes and objects to model real-world entities. Core concepts: encapsulation, inheritance, polymorphism, and abstraction.",
    "sample_question": "Explain encapsulation with an example in Java."
  },
  {
    "id": "java_collections",
    "title": "Java Collections",
    "summary": "The Java Collections Framework provides data structures like List, Set, Map and utilities to store and manipulate groups of objects efficiently.",
    "sample_question": "What is the difference between ArrayList and LinkedList in Java?"
  },
  {
    "id": "functions_and_methods",
    "title": "Functions / Methods",
    "summary": "Methods (functions) are reusable blocks of code that perform a task. In Java, methods are defined inside classes and can accept parameters and return values.",
    "sample_question": "What is method overloading and how does Java resolve overloaded methods?"
  },
  {
    "id": "arrays_and_strings",
    "title": "Arrays & Strings",
    "summary": "Arrays store fixed-size sequences of elements. Strings are immutable sequences of characters in Java, with many built-in utility methods.",
    "sample_question": "How is a String different from StringBuilder in Java?"
  },
  {
    "id": "dsa_intro",
    "title": "DSA: Basic Concepts",
    "summary": "Data Structures and Algorithms (DSA) deal with organizing data and performing operations efficiently. Core DS: arrays, linked lists, stacks, queues, trees, graphs; common algorithms: sorting, searching.",
    "sample_question": "What are the time/space trade-offs between arrays and linked lists?"
  },
  {
    "id": "sorting_searching",
    "title": "Sorting & Searching",
    "summary": "Important sorting algorithms include Bubble, Selection, Insertion, Merge, Quick, and Heap sort. Searching algorithms include linear and binary search (binary requires sorted data).",
    "sample_question": "Explain QuickSort and its average vs worst-case complexity."
  },
  {
    "id": "trees_graphs",
    "title": "Trees & Graphs",
    "summary": "Trees and graphs represent hierarchical and networked relationships respectively. Basic traversals: BFS (level order) and DFS (preorder/inorder/postorder for trees).",
    "sample_question": "What is the difference between BFS and DFS and when to use each?"
  },
  {
    "id": "dynamic_programming",
    "title": "Dynamic Programming",
    "summary": "Dynamic Programming (DP) optimizes recursive solutions by caching overlapping subproblems (memoization) or using tabulation. Useful for optimization problems.",
    "sample_question": "Describe memoization and tabulation with a Fibonacci example."
  }
]

def load_content():
    """
    Checks if CS JSON exists.
    If NO: Generates it from DEFAULT_CONTENT.
    If YES: Loads it.
    """
    try:
        path = os.path.join(os.path.dirname(__file__), CONTENT_FILE)
        
        if not os.path.exists(path):
            print(f"⚠️ {CONTENT_FILE} not found. Generating default CS content...")
            with open(path, "w", encoding='utf-8') as f:
                json.dump(DEFAULT_CONTENT, f, indent=4)
            print("✅ CS content file created successfully.")
            
        with open(path, "r", encoding='utf-8') as f:
            data = json.load(f)
            return data
            
    except Exception as e:
        print(f"⚠️ Error managing content file: {e}")
        return []

COURSE_CONTENT = load_content()

@dataclass
class TutorState:
    """Tracks the current learning context"""
    current_topic_id: str | None = None
    current_topic_data: dict | None = None
    mode: Literal["learn", "quiz", "teach_back"] = "learn"
    
    def set_topic(self, topic_id: str):
        topic = next((item for item in COURSE_CONTENT if item["id"] == topic_id), None)
        if topic:
            self.current_topic_id = topic_id
            self.current_topic_data = topic
            return True
        return False

@dataclass
class Userdata:
    tutor_state: TutorState
    agent_session: Optional[AgentSession] = None 

@function_tool
async def select_topic(
    ctx: RunContext[Userdata], 
    topic_id: Annotated[str, Field(description="The ID of the topic to study (e.g., 'java_basics', 'dsa_intro')")]
) -> str:
    """Selects a topic to study from the available list."""
    state = ctx.userdata.tutor_state
    success = state.set_topic(topic_id.lower())
    
    if success:
        return f"Topic set to {state.current_topic_data['title']}. Ask the user if they want to 'Learn', be 'Quizzed', or 'Teach it back'."
    else:
        available = ", ".join([t["id"] for t in COURSE_CONTENT])
        return f"Topic not found. Available topics are: {available}"

@function_tool
async def set_learning_mode(
    ctx: RunContext[Userdata], 
    mode: Annotated[str, Field(description="The mode to switch to: 'learn', 'quiz', or 'teach_back'")]
) -> str:
    """
    Switches the interaction mode and updates the agent's voice/persona.
    Added safety checks:
      - Ensures a topic is selected before attempting to explain or quiz.
      - Ensures the session exists before changing voice.
    Also injects a short introduction line from the chosen voice that states
    who they are and what they will do (teach / quiz / listen).
    """
    
    state = ctx.userdata.tutor_state
    state.mode = mode.lower()
    
    if not state.current_topic_data:
        return "No topic selected. Please select a topic first using select_topic(topic_id)."
    
    agent_session = ctx.userdata.agent_session 
    
    if not agent_session:
        return "Voice/session not available. Please ensure the agent session is active."

    summary = state.current_topic_data.get("summary", "")
    sample_question = state.current_topic_data.get("sample_question", "")

    if state.mode == "learn":
        agent_session.tts.update_options(voice="en-US-matthew", style="Promo")
        intro = "Hi, I'm Matthew. I’ll be teaching you this topic now."
        instruction = f"{intro} I will explain: {summary}"
        
    elif state.mode == "quiz":
        agent_session.tts.update_options(voice="en-US-alicia", style="Conversational")
        intro = "Hello, I’m Alicia. I’ll be taking your quiz now."
        instruction = f"{intro} Here is your question: {sample_question}"
        
    elif state.mode == "teach_back":
        agent_session.tts.update_options(voice="en-US-ken", style="Promo")
        intro = "Hey, I’m Ken. I’m here to listen to your explanation."
        instruction = f"{intro} Please explain the topic in your own words so I can evaluate it."
    else:
        return "Invalid mode. Use 'learn', 'quiz', or 'teach_back'."

    print(f"🔄 SWITCHING MODE -> {state.mode.upper()} (topic: {state.current_topic_id})")
    return f"Switched to {state.mode} mode. {instruction}"

@function_tool
async def evaluate_teaching(
    ctx: RunContext[Userdata],
    user_explanation: Annotated[str, Field(description="The explanation given by the user during teach-back")]
) -> str:
    """Call this when the user has finished explaining a concept in 'teach_back' mode."""
    print(f"📝 EVALUATING EXPLANATION: {user_explanation}")

    accuracy_hint = "Accuracy: check correctness against core points."
    clarity_hint = "Clarity: check structure, examples, and terminology usage."

    score_note = "Score guidance: 0-3 poor, 4-6 average, 7-8 good, 9-10 excellent."
    return (
        "Analyze the user's explanation. Provide:\n"
        "- A score out of 10 for accuracy and clarity.\n"
        f"- Corrections for any factual errors.\n"
        f"- Suggestions to improve explanation.\n\n{accuracy_hint}\n{clarity_hint}\n{score_note}"
    )

class TutorAgent(Agent):
    def __init__(self):
        topic_list = ", ".join([f"{t['id']} ({t['title']})" for t in COURSE_CONTENT])
        
        super().__init__(
            instructions=f"""
            You are a Programming Tutor designed to help users master Java and Data Structures topics.
            
            📚 **AVAILABLE TOPICS:** {topic_list}
            
            🔄 **YOU HAVE 3 MODES:**
            1. **LEARN Mode (Voice: Matthew):** Explain the concept clearly using the summary data.
            2. **QUIZ Mode (Voice: Alicia):** Ask the user a specific question to test knowledge.
            3. **TEACH_BACK Mode (Voice: Ken):** Pretend to be a student. Ask the user to explain the concept to you.
            
            ⚙️ **BEHAVIOR:**
            - Start by asking which topic the user wants to study.
            - Use the `set_learning_mode` tool immediately when the user asks to learn, take a quiz, or teach.
            - In 'teach_back' mode, listen to their explanation and then use `evaluate_teaching` to give feedback.
            """,
            tools=[select_topic, set_learning_mode, evaluate_teaching],
        )

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}

    print("\n" + "💻" * 25)
    print("🚀 STARTING PROGRAMMING TUTOR SESSION")
    print(f"📚 Loaded {len(COURSE_CONTENT)} topics from Knowledge Base")
    
    userdata = Userdata(tutor_state=TutorState())

    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-US-matthew", 
            style="Promo",        
            text_pacing=True,
        ),
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        userdata=userdata,
    )
    
    userdata.agent_session = session
    
    await session.start(
        agent=TutorAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    await ctx.connect()

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
