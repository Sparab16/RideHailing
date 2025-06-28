# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend code
COPY backend/ ./

# Expose the port (adjust if your app uses a different port)
EXPOSE 5000

# Set environment variables (optional)
ENV FLASK_APP=app.py

# Run the backend
CMD ["python", "app.py"]
