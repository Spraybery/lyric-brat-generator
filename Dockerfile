FROM python:3.9-slim

# Install system dependencies (ffmpeg is required for Whisper)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir r -r requirements.txt || pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variable for Flask
ENV FLASK_APP=app.py

# Run with Gunicorn on Render's automatic port binding
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
