from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Order(BaseModel):
    drinkType: str
    size: str
    milk: str
    extras: list
    name: str

@app.post("/save")
def save_order(order: Order):
    import datetime, json, os

    filename = f"order_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(os.getcwd(), filename)

    with open(filepath, "w") as f:
        json.dump(order.dict(), f, indent=4)

    return {"status": "saved", "file": filename}
