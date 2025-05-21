from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import uuid

app = FastAPI()

# Penyimpanan produk dalam memori
products_db: Dict[str, Dict] = {}

class Product(BaseModel):
    name: str
    price: float

class ProductResponse(Product):
    id: str

@app.post("/products", response_model=ProductResponse, status_code=201)
async def create_product(product: Product):
    product_id = str(uuid.uuid4())
    products_db[product_id] = product.model_dump()
    return ProductResponse(id=product_id, **product.model_dump())

@app.get("/products", response_model=List[ProductResponse])
async def get_products():
    return [ProductResponse(id=pid, **data) for pid, data in products_db.items()]

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    return ProductResponse(id=product_id, **products_db[product_id])

# Untuk menjalankan layanan ini (dari direktori product_service):
# uvicorn main:app --reload --port 8001
