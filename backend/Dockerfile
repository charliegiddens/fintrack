# Use official Python image
FROM python:3.11-slim

# Set environment vars
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_ENV=production

# Create working directory
WORKDIR /app

# Install system dependencies
# Added:
#   - pkg-config: helps find compiler/linker flags for libraries
#   - default-libmysqlclient-dev: development files for MySQL client (needed by mysqlclient python package)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    pkg-config \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
# Using --no-cache-dir with pip can help reduce image size slightly
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8000

# Upgrade DB schema and start app
CMD ["sh", "-c", "flask db upgrade && waitress-serve --host=0.0.0.0 --port=8000 wsgi:app"]