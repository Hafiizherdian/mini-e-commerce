from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict, Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone

# Konfigurasi JWT
SECRET_KEY = "RAHASIA_SUPER_AMAN_ANDA"  # Harusnya dari environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="Layanan Otentikasi")

# Penyimpanan pengguna dalam memori (untuk MVP)
# Kunci: username, Nilai: dict {'hashed_password': '...', 'roles': ['user'], 'email': '...'}
fake_users_db: Dict[str, Dict] = {} 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login") # Diperbarui nanti jika Nginx path berbeda

class UserRegistration(BaseModel):
    username: str
    password: str
    email: Optional[str] = None # Email opsional saat registrasi

class UserInDB(BaseModel):
    username: str
    email: Optional[str] = None
    hashed_password: str
    roles: list[str] = ["user"] # Default role

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    roles: Optional[list[str]] = None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.post("/register", status_code=status.HTTP_201_CREATED, summary="Registrasi pengguna baru")
async def register_user(form_data: UserRegistration):
    if form_data.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username sudah terdaftar. Silakan gunakan username lain."
        )
    hashed_password = get_password_hash(form_data.password)
    user_data = UserInDB(
        username=form_data.username, 
        email=form_data.email, 
        hashed_password=hashed_password
    )
    fake_users_db[form_data.username] = user_data.model_dump() # Simpan sebagai dict
    return {"message": f"Pengguna {form_data.username} berhasil diregistrasi."}

@app.post("/login", response_model=Token, summary="Login pengguna untuk mendapatkan token JWT")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_data_dict = fake_users_db.get(form_data.username)
    if not user_data_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = UserInDB(**user_data_dict) # Konversi dict ke model Pydantic
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "roles": user.roles}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Endpoint contoh untuk menguji token (opsional)
# async def get_current_active_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Tidak dapat memvalidasi kredensial",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         roles: list = payload.get("roles", [])
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username, roles=roles)
#     except JWTError:
#         raise credentials_exception
#     user = fake_users_db.get(token_data.username)
#     if user is None:
#         raise credentials_exception
#     return UserInDB(**user)

# @app.get("/users/me", summary="Informasi pengguna saat ini (membutuhkan token)")
# async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
#    return current_user

# Untuk menjalankan layanan ini (dari direktori auth_service):
# uvicorn main:app --reload --port 8003
