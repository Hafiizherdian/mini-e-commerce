# --- Build Stage ---
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the React application
RUN npm run build

# --- Serve Stage ---
FROM nginx:1.25-alpine 

# Copy built assets from the build stage
COPY --from=build /app/build /usr/share/nginx/html

# Optional: Copy a custom Nginx configuration for serving React app if needed
# For now, we'll rely on the default Nginx to serve static files from /usr/share/nginx/html
# And the main Nginx reverse proxy will handle routing.
# However, for client-side routing to work correctly when served directly by this Nginx,
# it would need a conf like:
# COPY nginx.conf /etc/nginx/conf.d/default.conf
# where nginx.conf would include:
# server {
#   listen 80;
#   location / {
#     root /usr/share/nginx/html;
#     index index.html;
#     try_files $uri $uri/ /index.html;
#   }
# }
# For this step, just copy the built assets. The main Nginx proxy will handle the SPA routing.

# Expose port 80 (Nginx default)
EXPOSE 80

# Default command to start Nginx
CMD ["nginx", "-g", "daemon off;"]
