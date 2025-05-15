# Use an official Python runtime as a base image
FROM python:3.13-slim

# Set environment variables
ENV KEYBRIDGE_API_VERSION=1.0.7

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire app into the container
COPY . .

# Command to run the app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
