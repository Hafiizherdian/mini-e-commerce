# Layanan Otentikasi (Auth Service)

Layanan ini bertanggung jawab untuk registrasi pengguna baru dan proses login untuk mendapatkan token JWT (JSON Web Token).

## Endpoint API

Semua endpoint diakses melalui Nginx reverse proxy (misalnya, `http://localhost/auth/...`).

-   **`POST /auth/register`**
    -   Registrasi pengguna baru.
    -   **Request Body:**
        ```json
        {
            "username": "userbaru",
            "password": "passwordkuat",
            "email": "user@example.com" 
        }
        ```
    -   **Response Sukses (201 Created):**
        ```json
        {
            "message": "Pengguna userbaru berhasil diregistrasi."
        }
        ```
    -   **Response Gagal (400 Bad Request):** Jika username sudah ada.

-   **`POST /auth/login`**
    -   Login untuk mendapatkan token JWT.
    -   **Request Body (form-data):**
        -   `username`: username_anda
        -   `password`: password_anda
    -   **Response Sukses (200 OK):**
        ```json
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
        ```
    -   **Response Gagal (401 Unauthorized):** Jika username atau password salah.

## Cara Menjalankan
Layanan ini dijalankan sebagai bagian dari `docker-compose.yml` utama. Lihat `README.md` di direktori root proyek untuk instruksi menjalankan semua layanan. Secara internal, layanan ini berjalan di port 8003.
