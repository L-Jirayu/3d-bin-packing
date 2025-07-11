from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from workconcept import do_packing

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Dimension(BaseModel):
    width: float
    depth: float
    height: float

class SKUItem(BaseModel):
    dimension: Dimension
    name: str = None

class SKURequest(BaseModel):
    skus: List[SKUItem]

@app.post("/pack")
async def pack_items(request: SKURequest):
    # แปลงเป็น dict เพื่อส่งให้ do_packing
    skus = [sku.dict() for sku in request.skus]
    result = do_packing(skus)
    return result
