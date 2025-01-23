# Use Python 3.11 slim image as base
FROM python:3.13-slim

# Set working directory in container
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY backend/src/ ./src/

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]