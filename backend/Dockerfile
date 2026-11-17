# Multi-stage / lightweight Python container for Backend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (needed for psycopg2 compilation if required)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code, database, and mesh data
COPY . .

ENV PORT=8000
ENV HOST=0.0.0.0

EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
