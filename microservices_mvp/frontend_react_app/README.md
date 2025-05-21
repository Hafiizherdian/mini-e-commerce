# Aplikasi Frontend React (frontend_react_app)

Aplikasi ini adalah antarmuka pengguna (UI) yang dibangun dengan React untuk berinteraksi dengan layanan backend microservices MVP.

## Fitur Utama (MVP)
- Registrasi Pengguna
- Login Pengguna (menggunakan JWT)
- Menampilkan Daftar Produk
- Membuat Pesanan Sederhana

## Struktur Direktori Penting
- `src/components/`: Berisi komponen-komponen React yang digunakan (misalnya `LoginPage.js`, `RegisterPage.js`, `ProductsPage.js`).
- `src/App.js`: Komponen utama yang mengatur routing dan layout dasar.
- `public/index.html`: File HTML utama.
- `package.json`: Daftar dependensi dan skrip proyek.

## Menjalankan untuk Pengembangan Lokal
Meskipun aplikasi ini dijalankan sebagai bagian dari `docker-compose.yml` keseluruhan, Anda dapat menjalankannya secara terpisah untuk pengembangan frontend:

1.  **Pastikan Anda berada di direktori `microservices_mvp/frontend_react_app`**.
2.  **Install dependensi (jika belum):**
    ```bash
    npm install
    ```
3.  **Jalankan server pengembangan React:**
    ```bash
    npm start
    ```
    Ini akan menjalankan aplikasi frontend (biasanya di `http://localhost:3000`) dan akan mencoba terhubung ke layanan backend yang diharapkan berjalan (misalnya, melalui Nginx di `http://localhost`). Anda mungkin perlu mengonfigurasi proxy di `package.json` jika backend tidak di-proxy oleh Nginx saat pengembangan lokal terpisah, atau jika Anda menjalankan backend tidak melalui Docker.
    Contoh proxy di `package.json` (jika Nginx berjalan di port 80):
    ```json
    "proxy": "http://localhost" 
    ```
    (Tambahkan baris di atas ke objek JSON utama di `package.json` jika diperlukan).

## Build untuk Produksi
Skrip `npm run build` akan membuat build statis dari aplikasi di direktori `build/`. Dockerfile yang ada di direktori ini menggunakan proses build ini untuk membuat image kontainer yang menyajikan file statis tersebut.
