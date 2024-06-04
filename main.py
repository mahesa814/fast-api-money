from fastapi import FastAPI,Response
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials,firestore
from datetime import datetime
cred = credentials.Certificate("firebase-config.json")
firebase_admin.initialize_app(cred)

app = FastAPI()
db = firestore.client()
money = db.collection('money')
class Item(BaseModel):
    name: str
    amount: int = None
    type: str
    created_at:str
    is_out_money :bool

@app.post("/money")
async def create_money(item: Item):
    data = {
        "name":item.name,
        "amount":item.amount,
        "type" : item.type,
        "created_at" :item.created_at,
        "is_out_money":item.is_out_money
     }
    print(data)
    doc = money.add(data)
    return {"message": "Successfully created"}
@app.get("/money")
async def get_money():
    docs = money.stream()
    data = [doc.to_dict() for doc in docs]
    return {"data": data}
