# Gunakan image Nginx resmi sebagai basis
FROM nginx:latest

# Hapus konfigurasi default Nginx
RUN rm /etc/nginx/conf.d/default.conf

# Salin file konfigurasi kustom Nginx Anda
COPY nginx.conf /etc/nginx/nginx.conf

# Port yang akan diekspos oleh Nginx (opsional, karena docker-compose akan menanganinya)
# EXPOSE 80
