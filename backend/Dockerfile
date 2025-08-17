FROM python:3.11-slim

# environment vars
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

# Create working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    netcat-traditional \
    libpq-dev \
    curl \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Upgrade DB schema and start app
CMD ["sh", "-c", "until nc -z postgres 5432; do echo 'Waiting for DB...'; sleep 3; done && flask db upgrade && waitress-serve --host=0.0.0.0 --port=8000 wsgi:app"]
