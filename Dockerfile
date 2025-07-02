# Use official Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy requirements (create requirements.txt if not present)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

# Expose port
EXPOSE 8000

# Run the app with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "1"]