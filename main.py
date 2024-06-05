from fastapi import FastAPI,Response,Query,HTTPException
from pydantic import BaseModel
import firebase_admin
from firebase_admin import credentials,firestore
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
cred = credentials.Certificate("firebase-config.json")
firebase_admin.initialize_app(cred)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
db = firestore.client()
money = db.collection('money')
categories = db.collection('categories')
class Item(BaseModel):
    name: str
    amount: int = None
    type: str
    created_at:str
    is_out_money :bool

class ItemCategory(BaseModel):
    name: str

@app.post("/money/save")
async def create_money(item: Item):
    data = {
        "name":item.name,
        "amount":item.amount,
        "type" : item.type,
        "created_at" :item.created_at,
        "is_out_money": 1 if item.is_out_money else 0
     }
    print(data)
    doc = money.add(data)
    return {"message": "Successfully created"}

@app.get("/money/get")
async def get_money(created_at: str = Query(...)):
    
    try:
        query = money.where('created_at', '==', created_at)
        
        # Fetch documents
        docs = query.get()
        
        in_money_query = money.where('is_out_money', '==', 1)
        in_money_docs = in_money_query.stream()
        in_money_sum = tuple(doc.get('amount') for doc in in_money_docs)
        
        out_money_query = query.where('is_out_money', '==', 0)
        out_money_docs = out_money_query.stream()
        out_money_sum = tuple(doc.get('amount') for doc in out_money_docs)
        
        # Prepare data
        data = [{'id': doc.id, **doc.to_dict()} for doc in docs]
        for item in data:
            item["is_out_money"] = bool(item["is_out_money"]) 
        
        return {"data": data, "in_money": sum(in_money_sum), "out_money": sum(out_money_sum)}
        # return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/money/delete/{id}")
async def delete_money(id: str):
    print(id)
    money.document(id).delete()
    return {"message": "successfully delete"}

@app.post("/categories/save")
async def create_categories(item: ItemCategory):
    data = {
        "name":item.name,
     }
    print(data)
    doc = categories.add(data)
    return {"message": "Successfully created"}
@app.get("/categories/get")
async def get_categories():
    docs = categories.stream()
    data = [{'id': doc.id, **doc.to_dict()} for doc in docs]
    return {"data": data}

@app.delete("/categories/delete/{id}")
async def delete_categories(id:str):
    categories.document(id).delete()
    return {"message": "successfully delete"}
