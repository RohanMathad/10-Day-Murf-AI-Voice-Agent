"""
Day 7 – Food & Grocery Ordering Voice Agent (SQLite)
- Uses SQLite DB 'order_db.sqlite'
- Seeds a GENERAL English catalog (Milk, Eggs, Bread, Pasta, Tomato Sauce, Chips, Coffee, etc.)
- Tools:
    - find_item
    - add_to_cart / remove_from_cart / update_cart / show_cart
    - add_recipe / ingredients_for
    - place_order
    - cancel_order
    - get_order_status / order_history
- Auto-simulation: Status updates every 5 seconds (received → confirmed → shipped → out_for_delivery → delivered)
"""

import json
import logging
import os
import sqlite3
import uuid
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Annotated

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
logger = logging.getLogger("food_agent_sqlite")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(handler)

load_dotenv(".env.local")

# -------------------------
# DB CONFIG
# -------------------------
DB_FILE = "order_db.sqlite"


def get_db_path() -> str:
    try:
        base = os.path.abspath(os.path.dirname(__file__))
    except NameError:
        base = os.getcwd()
    if not os.path.isdir(base):
        os.makedirs(base, exist_ok=True)
    return os.path.join(base, DB_FILE)


def get_conn():
    path = get_db_path()
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def seed_database():
    """Create tables and seed a GENERAL English catalog."""
    try:
        conn = get_conn()
        cur = conn.cursor()

        # Catalog table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS catalog (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                price REAL NOT NULL,
                brand TEXT,
                size TEXT,
                units TEXT,
                tags TEXT
            )
        """)

        # Orders
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                timestamp TEXT,
                total REAL,
                customer_name TEXT,
                address TEXT,
                status TEXT DEFAULT 'received',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)

        # Order items
        cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT,
                item_id TEXT,
                name TEXT,
                unit_price REAL,
                quantity INTEGER,
                notes TEXT,
                FOREIGN KEY(order_id) REFERENCES orders(order_id) ON DELETE CASCADE
            )
        """)

        # Seed general items
        cur.execute("SELECT COUNT(1) FROM catalog")
        if cur.fetchone()[0] == 0:
            catalog = [
                # Dairy & Basics
                ("milk-1l", "Fresh Milk", "Dairy", 2.50, "Generic", "1L", "bottle", json.dumps(["dairy"])),
                ("eggs-12", "Eggs Pack", "Dairy", 3.00, "Generic", "12 pcs", "box", json.dumps(["protein"])),
                ("bread-loaf", "White Bread Loaf", "Bakery", 1.80, "Generic", "1 loaf", "pack", json.dumps(["bread"])),
                ("butter-200g", "Salted Butter", "Dairy", 2.00, "Generic", "200g", "pack", json.dumps(["butter"])),
                ("cheese-200g", "Cheddar Cheese", "Dairy", 3.75, "Generic", "200g", "pack", json.dumps(["cheese"])),

                # Pantry
                ("pasta-500g", "Pasta", "Pantry", 1.50, "Generic", "500g", "pack", json.dumps(["pasta"])),
                ("sauce-jar", "Tomato Pasta Sauce", "Pantry", 2.20, "Generic", "1 jar", "jar", json.dumps(["sauce"])),
                ("rice-1kg", "Long Grain Rice", "Pantry", 2.40, "Generic", "1kg", "bag", json.dumps(["rice"])),
                ("flour-1kg", "All Purpose Flour", "Pantry", 1.20, "Generic", "1kg", "bag", json.dumps(["flour"])),
                ("sugar-1kg", "White Sugar", "Pantry", 1.10, "Generic", "1kg", "bag", json.dumps(["sugar"])),

                # Snacks
                ("chips-small", "Potato Chips", "Snacks", 1.00, "Generic", "50g", "pack", json.dumps(["snack"])),
                ("cookies-200g", "Chocolate Chip Cookies", "Snacks", 2.50, "Generic", "200g", "pack", json.dumps(["cookies"])),

                # Beverages
                ("coffee-200g", "Ground Coffee", "Beverages", 4.50, "Generic", "200g", "pack", json.dumps(["coffee"])),
                ("tea-100g", "Black Tea", "Beverages", 2.00, "Generic", "100g", "pack", json.dumps(["tea"])),

                # Fresh Produce
                ("apple-1kg", "Fresh Apples", "Fruits", 3.20, "Generic", "1kg", "kg", json.dumps(["fruit"])),
                ("banana-6", "Bananas", "Fruits", 1.80, "Generic", "6 pcs", "bunch", json.dumps(["fruit"])),
                ("tomato-1kg", "Fresh Tomatoes", "Vegetables", 2.10, "Generic", "1kg", "kg", json.dumps(["veg"])),
                ("onion-1kg", "Fresh Onions", "Vegetables", 1.70, "Generic", "1kg", "kg", json.dumps(["veg"])),
            ]

            cur.executemany("""
                INSERT INTO catalog (id,name,category,price,brand,size,units,tags)
                VALUES (?,?,?,?,?,?,?,?)
            """, catalog)
            conn.commit()

        conn.close()
    except Exception as e:
        logger.exception("FAILED DB SEED: %s", e)


seed_database()

# -------------------------
# CART + USER
# -------------------------
@dataclass
class CartItem:
    item_id: str
    name: str
    unit_price: float
    quantity: int = 1
    notes: str = ""

@dataclass
class Userdata:
    cart: List[CartItem] = field(default_factory=list)
    customer_name: Optional[str] = None

# -------------------------
# DB HELPERS (UNCHANGED)
# -------------------------
def find_catalog_item_by_id_db(item_id: str) -> Optional[dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM catalog WHERE LOWER(id)=LOWER(?) LIMIT 1", (item_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    r = dict(row)
    try:
        r["tags"] = json.loads(r.get("tags") or "[]")
    except:
        r["tags"] = []
    return r


def search_catalog_by_name_db(query: str) -> List[dict]:
    q = f"%{query.lower()}%"
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM catalog
        WHERE LOWER(name) LIKE ? OR LOWER(tags) LIKE ?
        LIMIT 50
    """, (q, q))
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        rr = dict(r)
        try:
            rr["tags"] = json.loads(rr.get("tags") or "[]")
        except:
            rr["tags"] = []
        out.append(rr)
    return out


def insert_order_db(order_id, timestamp, total, customer_name, address, status, items):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (order_id, timestamp, total, customer_name, address, status, created_at, updated_at)
        VALUES (?,?,?,?,?,?,datetime('now'),datetime('now'))
    """, (order_id, timestamp, total, customer_name, address, status))
    for ci in items:
        cur.execute("""
            INSERT INTO order_items (order_id,item_id,name,unit_price,quantity,notes)
            VALUES (?,?,?,?,?,?)
        """, (order_id, ci.item_id, ci.name, ci.unit_price, ci.quantity, ci.notes))
    conn.commit()
    conn.close()


def get_order_db(order_id: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders WHERE order_id=? LIMIT 1", (order_id,))
    o = cur.fetchone()
    if not o:
        conn.close()
        return None
    order = dict(o)
    cur.execute("SELECT * FROM order_items WHERE order_id=?", (order_id,))
    order["items"] = [dict(r) for r in cur.fetchall()]
    conn.close()
    return order


def list_orders_db(limit=10, customer_name=None):
    conn = get_conn()
    cur = conn.cursor()
    if customer_name:
        cur.execute("""
            SELECT * FROM orders WHERE LOWER(customer_name)=LOWER(?) 
            ORDER BY created_at DESC LIMIT ?
        """, (customer_name, limit))
    else:
        cur.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def update_order_status_db(order_id, new_status):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE orders SET status=?, updated_at=datetime('now') WHERE order_id=?
    """, (new_status, order_id))
    changed = cur.rowcount
    conn.commit()
    conn.close()
    return changed > 0

# -------------------------
# INGREDIENT MAP + HELPERS
# -------------------------

RECIPE_MAP = {
    "pasta": ["pasta-500g", "sauce-jar"],
    "sandwich": ["bread-loaf", "cheese-200g", "butter-200g"],
    "coffee": ["coffee-200g", "milk-1l"],
    "tea": ["tea-100g", "milk-1l", "sugar-1kg"],
}

import re

_NUMBER_WORDS = {
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
}


def _parse_servings_from_text(text):
    text = (text or "").lower()
    m = re.search(r"for\s+(\d+)", text)
    if m:
        return max(1, int(m.group(1)))
    for w, n in _NUMBER_WORDS.items():
        if f"for {w}" in text:
            return n
    return 1


def _infer_items_from_tags(query, max_results=6):
    words = re.findall(r"\w+", (query or "").lower())
    found = []
    conn = get_conn()
    cur = conn.cursor()
    for w in words:
        if len(found) >= max_results:
            break
        q = f"%\"{w}\"%"
        cur.execute("""
            SELECT * FROM catalog 
            WHERE LOWER(tags) LIKE ? OR LOWER(name) LIKE ?
            LIMIT 10
        """, (q, f"%{w}%"))
        rows = cur.fetchall()
        for r in rows:
            rid = r["id"]
            if rid not in found:
                found.append(rid)
    conn.close()
    return found

# Status flow
STATUS_FLOW = ["received", "confirmed", "shipped", "out_for_delivery", "delivered"]

async def simulate_delivery_flow(order_id: str):
    logger.info(f"🚚 SIM: tracking order {order_id}")
    await asyncio.sleep(5)
    for s in STATUS_FLOW[1:]:
        o = get_order_db(order_id)
        if o and o.get("status") == "cancelled":
            return
        update_order_status_db(order_id, s)
        logger.info(f"STATUS UPDATE — {order_id}: {s}")
        await asyncio.sleep(5)

# -------------------------
# CART UTILITY
# -------------------------
def cart_total(cart):
    return round(sum(ci.unit_price * ci.quantity for ci in cart), 2)

# -------------------------
# TOOLS (UNCHANGED)
# -------------------------
@function_tool
async def find_item(ctx: RunContext[Userdata], query: Annotated[str, Field(description="Item name")]):
    matches = search_catalog_by_name_db(query)
    if not matches:
        return f"No items found for '{query}'."
    lines = []
    for it in matches[:10]:
        lines.append(f"- {it['name']} (id: {it['id']}) — ${it['price']:.2f}")
    return "Found:\n" + "\n".join(lines)


@function_tool
async def add_to_cart(ctx: RunContext[Userdata], item_id: Annotated[str, Field(description="ID")], quantity: Annotated[int, Field(description="Qty", default=1)] = 1, notes: Annotated[str, Field(description="Notes")] = ""):
    item = find_catalog_item_by_id_db(item_id)
    if not item:
        return f"Item '{item_id}' not found."
    for ci in ctx.userdata.cart:
        if ci.item_id.lower() == item_id.lower():
            ci.quantity += quantity
            return f"Updated '{ci.name}' to {ci.quantity}. Total: ${cart_total(ctx.userdata.cart):.2f}"
    ctx.userdata.cart.append(CartItem(item_id=item["id"], name=item["name"], unit_price=item["price"], quantity=quantity))
    return f"Added {quantity} × {item['name']}. Total: ${cart_total(ctx.userdata.cart):.2f}"


@function_tool
async def remove_from_cart(ctx: RunContext[Userdata], item_id: Annotated[str, Field(description="ID")]):
    before = len(ctx.userdata.cart)
    ctx.userdata.cart = [ci for ci in ctx.userdata.cart if ci.item_id.lower() != item_id.lower()]
    if before == len(ctx.userdata.cart):
        return f"Item '{item_id}' not in cart."
    return f"Removed '{item_id}'. Total: ${cart_total(ctx.userdata.cart):.2f}"


@function_tool
async def update_cart_quantity(ctx: RunContext[Userdata], item_id: Annotated[str, Field(description="ID")], quantity: Annotated[int, Field(description="Qty")]):
    if quantity < 1:
        return await remove_from_cart(ctx, item_id)
    for ci in ctx.userdata.cart:
        if ci.item_id.lower() == item_id.lower():
            ci.quantity = quantity
            return f"Updated '{ci.name}' to {ci.quantity}. Total: ${cart_total(ctx.userdata.cart):.2f}"
    return f"Item '{item_id}' not found."


@function_tool
async def show_cart(ctx: RunContext[Userdata]):
    if not ctx.userdata.cart:
        return "Your cart is empty."
    lines = []
    for ci in ctx.userdata.cart:
        lines.append(f"- {ci.quantity} x {ci.name} = ${ci.unit_price * ci.quantity:.2f}")
    return "Your Cart:\n" + "\n".join(lines) + f"\nTotal: ${cart_total(ctx.userdata.cart):.2f}"


@function_tool
async def add_recipe(ctx: RunContext[Userdata], dish_name: Annotated[str, Field(description="Dish")]):
    key = dish_name.lower().strip()
    if key not in RECIPE_MAP:
        return f"No recipe found for '{dish_name}'."
    added = []
    for iid in RECIPE_MAP[key]:
        item = find_catalog_item_by_id_db(iid)
        if not item:
            continue
        found = False
        for ci in ctx.userdata.cart:
            if ci.item_id == iid:
                ci.quantity += 1
                found = True
                break
        if not found:
            ctx.userdata.cart.append(CartItem(item_id=item["id"], name=item["name"], unit_price=item["price"], quantity=1))
        added.append(item["name"])
    return f"Added ingredients for {dish_name}: {', '.join(added)}. Total: ${cart_total(ctx.userdata.cart):.2f}"


@function_tool
async def ingredients_for(ctx: RunContext[Userdata], request: Annotated[str, Field(description="Request")]):
    text = request.strip()
    servings = _parse_servings_from_text(request)
    m = re.search(r"ingredients? for (.+)", text, re.I)
    dish = m.group(1) if m else text
    dish = re.sub(r"for\s+\w+(?: people| person)?", "", dish, flags=re.I).strip()
    key = dish.lower()
    item_ids = RECIPE_MAP.get(key) or _infer_items_from_tags(key)
    if not item_ids:
        return f"Couldn't determine ingredients for '{request}'."
    added = []
    for iid in item_ids:
        item = find_catalog_item_by_id_db(iid)
        if not item:
            continue
        found = False
        for ci in ctx.userdata.cart:
            if ci.item_id == iid:
                ci.quantity += servings
                found = True
                break
        if not found:
            ctx.userdata.cart.append(CartItem(item_id=item["id"], name=item["name"], unit_price=item["price"], quantity=servings))
        added.append(item["name"])
    return f"Added {', '.join(added)} for '{dish}'. Servings: {servings}. Total: ${cart_total(ctx.userdata.cart):.2f}"


@function_tool
async def place_order(ctx: RunContext[Userdata], customer_name: Annotated[str, Field(description="Name")], address: Annotated[str, Field(description="Address")]):
    if not ctx.userdata.cart:
        return "Your cart is empty."
    order_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow().isoformat() + "Z"
    total = cart_total(ctx.userdata.cart)
    insert_order_db(order_id, now, total, customer_name, address, "received", ctx.userdata.cart)
    ctx.userdata.cart = []
    ctx.userdata.customer_name = customer_name
    try:
        asyncio.create_task(simulate_delivery_flow(order_id))
    except RuntimeError:
        pass
    return f"Order placed! Order ID: {order_id}. Total: ${total:.2f}. Delivery tracking is active."


@function_tool
async def cancel_order(ctx: RunContext[Userdata], order_id: Annotated[str, Field(description="Order ID")]):
    o = get_order_db(order_id)
    if not o:
        return f"No order found with ID {order_id}."
    if o["status"] == "delivered":
        return f"Order {order_id} already delivered."
    if o["status"] == "cancelled":
        return f"Order {order_id} is already cancelled."
    update_order_status_db(order_id, "cancelled")
    return f"Order {order_id} cancelled."


@function_tool
async def get_order_status(ctx: RunContext[Userdata], order_id: Annotated[str, Field(description="Order ID")]):
    o = get_order_db(order_id)
    if not o:
        return f"No order found with ID {order_id}."
    return f"Order {order_id} status: {o['status']} (updated: {o['updated_at']})"


@function_tool
async def order_history(ctx: RunContext[Userdata], customer_name: Annotated[Optional[str], Field(description="Name", default=None)] = None):
    rows = list_orders_db(limit=5, customer_name=customer_name)
    if not rows:
        return "No previous orders found."
    lines = []
    for o in rows:
        lines.append(f"- {o['order_id']} | ${o['total']:.2f} | {o['status']}")
    return "\n".join(lines)

# -------------------------
# AGENT – GENERAL ITEMS VERSION
# -------------------------
class FoodAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            You are Bob, a friendly food and grocery ordering assistant.
            You can search items, add them to the cart, remove them, update quantities,
            provide ingredients for common dishes (pasta, sandwiches, tea, coffee),
            show the cart, place orders, cancel orders, check status, and show order history.
            Speak clearly and helpfully.
            """,
            tools=[
                find_item, add_to_cart, remove_from_cart, update_cart_quantity,
                show_cart, add_recipe, ingredients_for,
                place_order, cancel_order, get_order_status, order_history
            ],
        )

# -------------------------
# ENTRYPOINT
# -------------------------
def prewarm(proc: JobProcess):
    try:
        proc.userdata["vad"] = silero.VAD.load()
    except Exception:
        pass


async def entrypoint(ctx: JobContext):
    ctx.log_context_fields = {"room": ctx.room.name}
    logger.info("🚀 STARTING GENERAL FOOD & GROCERY ORDERING AGENT")

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
        agent=FoodAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVC()),
    )

    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
