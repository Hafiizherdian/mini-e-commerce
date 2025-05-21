from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Dict, Optional
from jose import JWTError, jwt
# import uuid # uuid tidak lagi digunakan secara langsung untuk pembuatan ID pengguna

# Konfigurasi JWT - HARUS SAMA dengan di auth_service
SECRET_KEY = "RAHASIA_SUPER_AMAN_ANDA"  # Idealnya dari environment variable
ALGORITHM = "HS256"

app = FastAPI(title="Layanan Pengguna")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") # Path ke endpoint login di auth_service (mungkin perlu disesuaikan jika via Nginx)

# Model Pydantic untuk data pengguna
class User(BaseModel):
    id: str
    name: str
    email: str

# Model Pydantic untuk data dalam token
class TokenData(BaseModel):
    username: Optional[str] = None
    roles: Optional[list[str]] = None

# Penyimpanan pengguna dalam memori (dummy, karena pembuatan pengguna dihilangkan)
# Di aplikasi nyata, ini akan berasal dari database yang sama dengan auth_service atau sinkronisasi.
users_db_dummy: Dict[str, User] = {
    "pengguna_tes1": User(id="pengguna_tes1", name="Pengguna Tes Satu", email="tes1@example.com"),
    "pengguna_tes2": User(id="pengguna_tes2", name="Pengguna Tes Dua", email="tes2@example.com")
}


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
        # Di sini kita bisa menambahkan validasi role jika diperlukan, misalnya:
        # if "user_admin" not in roles:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak memiliki hak akses yang cukup")
        return TokenData(username=username, roles=roles)
    except JWTError:
        raise credentials_exception


# Endpoint POST /users (pembuatan pengguna) DIHAPUS
# @app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
# async def create_user(user_payload: UserCreatePayload): # UserCreatePayload perlu didefinisikan jika endpoint ini ada
#     user_id = str(uuid.uuid4())
#     # Logika untuk membuat pengguna baru, mungkin dengan validasi email unik, dll.
#     # Untuk MVP ini, endpoint pembuatan pengguna ada di auth_service (/register)
#     # Di sini, kita hanya akan memiliki data dummy atau mengambil dari sumber data yang sama.
#     # users_db[user_id] = User(id=user_id, name=user_payload.name, email=user_payload.email)
#     # return users_db[user_id]
#     raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Pembuatan pengguna dilakukan melalui Layanan Otentikasi (/register)")


@app.get("/users", response_model=List[User], summary="Dapatkan daftar semua pengguna (membutuhkan token)")
async def get_users(current_user_data: TokenData = Depends(get_current_user_token_data)):
    # current_user_data bisa digunakan untuk logging atau pemeriksaan role tambahan jika perlu
    # print(f"Pengguna {current_user_data.username} dengan peran {current_user_data.roles} mengakses daftar pengguna.")
    return list(users_db_dummy.values())

@app.get("/users/{user_id}", response_model=User, summary="Dapatkan pengguna spesifik berdasarkan ID (membutuhkan token)")
async def get_user(user_id: str, current_user_data: TokenData = Depends(get_current_user_token_data)):
    # Logika tambahan: mungkin hanya admin atau pengguna itu sendiri yang bisa melihat detailnya.
    # if "admin" not in current_user_data.roles and current_user_data.username != user_id:
    #     # Jika user_id di sini merujuk ke username, maka perbandingan di atas valid.
    #     # Jika user_id adalah UUID unik, maka perlu mekanisme lain untuk otorisasi level objek.
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tidak diizinkan mengambil data pengguna ini.")

    user_info = users_db_dummy.get(user_id) # Menggunakan user_id sebagai kunci di dummy DB
    if user_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pengguna tidak ditemukan")
    return user_info


@app.get("/me", response_model=User, summary="Dapatkan detail pengguna saat ini (membutuhkan token)")
async def read_users_me(current_user_data: TokenData = Depends(get_current_user_token_data)):
    # current_user_data.username didapatkan dari 'sub' claim di JWT
    user_info = users_db_dummy.get(current_user_data.username) 
    if user_info is None:
        # Ini seharusnya tidak terjadi jika token valid dan user ada di db
        # Mungkin username di token tidak cocok dengan key di users_db_dummy
        # atau users_db_dummy tidak sinkron.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pengguna tidak ditemukan dalam database dummy." 
        )
    # Karena users_db_dummy menyimpan instance User, kita bisa langsung mengembalikannya.
    # Jika users_db_dummy menyimpan dict, maka User(**user_info) akan diperlukan.
    return user_info

# Untuk menjalankan layanan ini (dari direktori user_service):
# uvicorn main:app --reload --port 8000
