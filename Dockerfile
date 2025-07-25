# Single stage build
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p app/static/uploads && \
    chmod -R 755 app/static/uploads

# Set environment variables
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0
ENV PYTHONPATH=/app

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--pythonpath", "/app", "app.app:app"]
