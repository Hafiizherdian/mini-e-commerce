from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Dict, Optional
from jose import JWTError, jwt
import uuid

# Konfigurasi JWT - HARUS SAMA dengan di auth_service
SECRET_KEY = "RAHASIA_SUPER_AMAN_ANDA"  # Idealnya dari environment variable
ALGORITHM = "HS256"

app = FastAPI(title="Layanan Pesanan")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") # Path ke endpoint login di auth_service (via Nginx)

# Penyimpanan pesanan dalam memori
orders_db: Dict[str, Dict] = {}

# Data dummy untuk produk (pemeriksaan internal MVP placeholder)
# Dalam microservice sungguhan, ini akan melibatkan panggilan API ke Layanan Produk.
mock_products_db = {
    "product1_dummy_id": {"name": "Laptop", "price": 1200.00},
    "product2_dummy_id": {"name": "Mouse", "price": 25.00}
}

class OrderItem(BaseModel):
    product_id: str
    quantity: int

# Model Pydantic untuk data dalam token
class TokenData(BaseModel):
    username: Optional[str] = None # 'sub' claim dari JWT, akan digunakan sebagai user_id
    roles: Optional[list[str]] = None

# Model Pydantic untuk request body saat membuat pesanan
# user_id dihilangkan karena akan diambil dari token JWT
class OrderBase(BaseModel):
    items: List[OrderItem]

# Model Pydantic untuk respons pesanan
class OrderResponse(BaseModel): # Tidak lagi mewarisi OrderBase secara langsung jika user_id ditambahkan scr terpisah
    id: str
    user_id: str # Diambil dari token saat pembuatan
    items: List[OrderItem]
    total_price: float
    status: str # contoh: "pending", "completed", "cancelled"


async def get_current_user_token_data(token: str = Depends(oauth2_scheme)) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Tidak dapat memvalidasi kredensial",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        roles: Optional[list[str]] = payload.get("roles")
        if username is None:
            raise credentials_exception
        # Di sini kita bisa menambahkan validasi role jika diperlukan
        return TokenData(username=username, roles=roles)
    except JWTError:
        raise credentials_exception


@app.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, summary="Buat pesanan baru (membutuhkan token)")
async def create_order(order: OrderBase, current_user_data: TokenData = Depends(get_current_user_token_data)):
    order_id = str(uuid.uuid4())
    user_id_from_token = current_user_data.username # Menggunakan 'sub' (username) dari token sebagai user_id

    total_price = 0
    for item in order.items:
        if item.product_id not in mock_products_db: # Pemeriksaan produk placeholder
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Produk dengan id {item.product_id} tidak ditemukan.")
        product_price = mock_products_db[item.product_id]["price"]
        total_price += product_price * item.quantity

    new_order_data = {
        "user_id": user_id_from_token,
        "items": [item.model_dump() for item in order.items],
        "total_price": total_price,
        "status": "tertunda" 
    }
    orders_db[order_id] = new_order_data
    
    return OrderResponse(
        id=order_id,
        user_id=user_id_from_token,
        items=order.items,
        total_price=total_price,
        status="tertunda"
    )

@app.get("/orders", response_model=List[OrderResponse], summary="Dapatkan daftar semua pesanan (membutuhkan token, admin-only bisa ditambahkan)")
async def get_orders(current_user_data: TokenData = Depends(get_current_user_token_data)):
    # Logika tambahan bisa ditambahkan di sini, misalnya:
    # Jika bukan admin, hanya tampilkan pesanan milik pengguna yang sedang login (current_user_data.username)
    # Untuk MVP ini, kita tampilkan semua pesanan jika token valid.
    
    response_list = []
    for oid, data in orders_db.items():
        # if "admin" in current_user_data.roles or data["user_id"] == current_user_data.username: # Contoh filter
        items_model = [OrderItem(**item_data) for item_data in data["items"]]
        response_list.append(OrderResponse(
            id=oid,
            user_id=data["user_id"],
            items=items_model,
            total_price=data["total_price"],
            status=data["status"]
        ))
    return response_list

@app.get("/orders/{order_id}", response_model=OrderResponse, summary="Dapatkan pesanan spesifik (membutuhkan token)")
async def get_order(order_id: str, current_user_data: TokenData = Depends(get_current_user_token_data)):
    if order_id not in orders_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pesanan tidak ditemukan")
    
    order_data = orders_db[order_id]

    # Logika tambahan: pastikan pengguna hanya bisa mengambil pesanannya sendiri, kecuali admin
    # if "admin" not in current_user_data.roles and order_data["user_id"] != current_user_data.username:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak diizinkan mengambil pesanan ini.")

    items_model = [OrderItem(**item_data) for item_data in order_data["items"]]
    return OrderResponse(
        id=order_id,
        user_id=order_data["user_id"],
        items=items_model,
        total_price=order_data["total_price"],
        status=order_data["status"]
    )

# Untuk menjalankan layanan ini (dari direktori order_service):
# uvicorn main:app --reload --port 8002
