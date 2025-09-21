# Use an official lightweight Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first (better for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of code into the container
COPY . .

# Set environment variable for Cloud Run
ENV PORT=8080

# Expose port (Cloud Run expects your app to listen on $PORT)
EXPOSE 8080

# Start the bot
CMD ["python", "bot.py"]
