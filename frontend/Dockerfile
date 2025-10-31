# Frontend Dockerfile
FROM nginx:alpine

# Set working directory
WORKDIR /usr/share/nginx/html

# Copy all frontend files (like login.html, notes.html, js, css)
COPY . .

# By default nginx serves index.html, rename login.html to index.html
RUN mv login.html index.html

# Expose nginx port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
