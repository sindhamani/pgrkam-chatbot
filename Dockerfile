# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libasound2-dev \
    portaudio19-dev \
    espeak \
    espeak-data \
    libespeak1 \
    libespeak-dev \
    festival \
    festival-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirement.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirement.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/documents /app/logs

# Set permissions
RUN chmod +x /app/setup.py

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--timeout", "120", "web_app:app"]
