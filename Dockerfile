# Dockerfile for containerizing UniBB AI Assistant application

# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables for production settings
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application into the container
COPY . .

# Command to run the application
CMD [ "python", "app.py" ]
