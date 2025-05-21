# Gunakan image Python resmi sebagai basis
FROM python:3.9-slim

# Atur direktori kerja di dalam kontainer
WORKDIR /app

# Salin file dependensi ke direktori kerja
COPY requirements.txt .

# Instal paket yang dibutuhkan dari requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Salin isi direktori src lokal ke direktori kerja
COPY main.py .

# Tentukan port yang akan digunakan oleh aplikasi
EXPOSE 8003

# Perintah untuk menjalankan aplikasi
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
