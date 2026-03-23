FROM python:3.12-slim

# Install ffmpeg + nodejs (yt-dlp needs a JS runtime for YouTube extraction)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Create directory for SQLite database (use Railway volume in production)
RUN mkdir -p /data

ENV DB_PATH=/data/transcriptx.db
ENV FLASK_ENV=production

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--timeout", "180", "--preload", "app:app"]
