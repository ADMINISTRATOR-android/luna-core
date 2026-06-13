# Use an official Python runtime
FROM python:3.12-slim

# Install system dependencies (espeak-ng)
RUN apt-get update && apt-get install -y \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 5000

# Run the app
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]

