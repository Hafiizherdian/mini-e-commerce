# MVP Microservices dengan Python

Proyek ini adalah Produk Minimum yang Layak (MVP) yang mendemonstrasikan arsitektur microservices sederhana menggunakan Python dan FastAPI, dengan fitur otentikasi JWT, Nginx sebagai reverse proxy, pembatasan akses (rate limiting), dan antarmuka pengguna berbasis React.

## Struktur Proyek

- `/auth_service`: Mengelola registrasi dan login pengguna (JWT).
- `/user_service`: Mengelola data pengguna (dilindungi oleh JWT).
- `/product_service`: Mengelola data produk.
- `/order_service`: Mengelola pesanan (dilindungi oleh JWT).
- `/nginx`: Berisi konfigurasi Nginx untuk reverse proxy, rate limiting, dan penyajian frontend.
- `/frontend_react_app`: Aplikasi frontend React untuk interaksi pengguna.

Setiap direktori layanan backend (`auth_service`, `user_service`, `product_service`, `order_service`) berisi:
- `main.py`: Aplikasi FastAPI untuk layanan tersebut.
- `requirements.txt`: Dependensi Python untuk layanan tersebut.
- `Dockerfile`: Instruksi untuk membangun image Docker layanan.
Direktori `frontend_react_app` juga berisi `Dockerfile` sendiri untuk membangun dan menyajikan UI.

## Prasyarat

- Python 3.7+ (untuk pengembangan lokal backend tanpa Docker)
- Node.js & npm (untuk pengembangan lokal frontend tanpa Docker)
- `pip` (untuk pengembangan lokal backend tanpa Docker)
- Docker Engine: [Instal Docker](https://docs.docker.com/engine/install/)
- Docker Compose: Biasanya disertakan dengan Docker Desktop untuk Windows dan Mac. Untuk Linux, [instal secara terpisah](https://docs.docker.com/compose/install/).

## Pengaturan dan Menjalankan Layanan (Cara Utama: Docker Compose)

Cara yang direkomendasikan untuk menjalankan proyek ini adalah dengan Docker Compose, karena sudah termasuk Nginx dan semua layanan yang terkonfigurasi.

### Membangun dan Menjalankan dengan Docker Compose
1.  **Pastikan Anda berada di direktori root proyek** (`microservices_mvp`).
2.  **Bangun image dan jalankan kontainer:**
    ```bash
    docker-compose up --build
    ```
    Perintah ini akan membangun image untuk setiap layanan (termasuk Nginx, Auth Service, dan Frontend) dan memulai kontainer. Nginx akan menjadi satu-satunya entry point ke aplikasi, menyajikan antarmuka pengguna (UI) di `http://localhost/` dan meneruskan permintaan API ke layanan backend yang sesuai.
3.  **Menghentikan layanan:**
    Untuk menghentikan semua layanan yang berjalan:
    ```bash
    docker-compose down
    ```
    Jika Anda menjalankan dalam mode detached, atau untuk membersihkan volume (jika ada yang didefinisikan untuk persistensi data di masa depan):
    ```bash
    docker-compose down -v
    ```

## Titik Akhir API (API Endpoints)

Semua permintaan ke layanan API sekarang melalui Nginx reverse proxy pada port 80 (misalnya, `http://localhost/api/...` jika Anda mengkonfigurasi Nginx untuk prefix API, atau langsung seperti `http://localhost/users/` jika tidak ada prefix API global). Untuk proyek ini, kita menggunakan path langsung tanpa prefix `/api` global.

Antarmuka pengguna grafis (UI) yang dapat diakses di `http://localhost/` setelah menjalankan `docker-compose up` menyediakan cara yang lebih ramah untuk berinteraksi dengan sebagian besar fungsionalitas sistem.

Dokumentasi API interaktif (Swagger UI) untuk masing-masing layanan backend dapat diakses melalui path `/docs` masing-masing layanan yang dirutekan oleh Nginx (misalnya, `http://localhost/auth/docs`, `http://localhost/users/docs`, `http://localhost/products/docs`, `http://localhost/orders/docs`).

Perubahan penting pada layanan backend:
- **Layanan Pengguna (User Service) - via `/users` (Dilindungi JWT):**
    - `GET /users`: Mendapatkan semua pengguna. Membutuhkan token JWT.
    - `GET /users/{user_id}`: Mendapatkan pengguna spesifik. Membutuhkan token JWT.
    - Endpoint baru `GET /users/me`: Mengembalikan detail pengguna yang sedang login (berdasarkan token JWT).
    - *Catatan: Pembuatan pengguna sekarang melalui `/auth/register`.*
- **Layanan Produk (Product Service) - via `/products`:**
    - `POST /products`: Membuat produk baru. (Saat ini tidak diimplementasikan di UI)
    - `GET /products`: Mendapatkan semua produk.
    - `GET /products/{product_id}`: Mendapatkan produk spesifik.
- **Layanan Pesanan (Order Service) - via `/orders` (Dilindungi JWT):**
    - Semua endpoint (`POST /orders`, `GET /orders`, `GET /orders/{order_id}`) sekarang dilindungi dan memerlukan token JWT untuk akses.
- **Layanan Otentikasi (Auth Service) - via `/auth`:**
    - `POST /auth/register`: Registrasi pengguna baru.
    - `POST /auth/login`: Login untuk mendapatkan token JWT.


### Menggunakan Token JWT (Untuk Layanan yang Dilindungi)
1.  Dapatkan token JWT dengan melakukan registrasi dan login melalui UI atau `POST` request ke `/auth/login`.
2.  Sertakan token tersebut dalam header `Authorization` pada setiap permintaan ke endpoint yang dilindungi:
    `Authorization: Bearer <token_anda>`

## Antarmuka Pengguna (Frontend)

Aplikasi ini menyertakan antarmuka pengguna (UI) berbasis web yang dibangun menggunakan React. UI ini dapat diakses melalui `http://localhost/` setelah semua layanan dijalankan menggunakan `docker-compose up`.

Fitur UI saat ini (MVP):
- **Registrasi Pengguna:** Membuat akun pengguna baru.
- **Login Pengguna:** Masuk ke sistem untuk mendapatkan token JWT.
- **Daftar Produk:** Menampilkan produk yang tersedia dari Product Service.
- **Pembuatan Pesanan Dasar:** Memungkinkan pengguna yang sudah login untuk membuat pesanan sederhana untuk produk.

Untuk pengembangan frontend secara lokal (di luar Docker), lihat `frontend_react_app/README.md`.

## Kebijakan Pembatasan Akses (Rate Limiting)

Untuk menjaga stabilitas dan keamanan layanan, diterapkan kebijakan pembatasan akses (rate limiting) pada semua permintaan API yang masuk melalui Nginx.
- **Batas Umum:** Setiap alamat IP dibatasi hingga **10 permintaan per detik** untuk endpoint API.
- **Burst:** Sistem mengizinkan lonjakan singkat hingga **20 permintaan** sebelum pembatasan aktif.
- **Status Code saat Terkena Limit:** Jika batas terlampaui, server akan merespons dengan status HTTP `429 Too Many Requests`.
(Frontend yang disajikan melalui `location /` saat ini tidak memiliki rate limit terpisah yang aktif di Nginx, namun bisa ditambahkan jika perlu).

## Pengaturan dan Menjalankan Layanan (Lokal, Tanpa Docker - untuk pengembangan individual)

Jika Anda ingin menjalankan layanan secara individual tanpa Docker (misalnya, untuk pengembangan atau debugging satu layanan):

1.  **Navigasi ke direktori layanan terkait** (misalnya, `cd user_service` atau `cd frontend_react_app`).
2.  **Buat lingkungan virtual (disarankan untuk backend Python):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Di Windows: venv\Scripts\activate
    ```
3.  **Instal dependensi:**
    - Backend: `pip install -r requirements.txt`
    - Frontend: `npm install` (di direktori `frontend_react_app`)
4.  **Jalankan layanan:**
    -   **Layanan Otentikasi:** `uvicorn main:app --reload --port 8003`
    -   **Layanan Pengguna:** `uvicorn main:app --reload --port 8000`
    -   **Layanan Produk:** `uvicorn main:app --reload --port 8001`
    -   **Layanan Pesanan:** `uvicorn main:app --reload --port 8002`
    -   **Frontend React App:** `npm start` (biasanya di port 3000)
    *Catatan: Tanpa Nginx di depan, Anda perlu mengakses layanan ini melalui port masing-masing dan otentikasi JWT serta interaksi antar layanan mungkin perlu diuji dengan alat seperti Postman atau dengan konfigurasi proxy di frontend.*

## Catatan tentang MVP
Ini adalah MVP. Data disimpan dalam memori dan akan hilang saat layanan dimulai ulang. Komunikasi antar-layanan di Layanan Pesanan (misalnya validasi produk) saat ini masih berupa tiruan (mocked). Keamanan token JWT (`SECRET_KEY`) juga hardcoded dan seharusnya menggunakan variabel lingkungan di produksi. Error handling dan validasi input bisa lebih komprehensif. Fitur seperti pengelolaan peran pengguna lebih lanjut dan otorisasi berbasis peran yang lebih detail belum diimplementasikan sepenuhnya.
