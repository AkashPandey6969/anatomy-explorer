# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

# Stage 2: Production Python backend & static file server
FROM python:3.11-slim

WORKDIR /app

# Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application
COPY backend/ ./backend
COPY meshes.txt ./

# Copy built frontend assets to static serving directory
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
