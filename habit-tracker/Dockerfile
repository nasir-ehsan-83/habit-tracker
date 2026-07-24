FROM python:3.11-slim

WORKDIR /app

# Copy dependency requirements file
COPY requirements.txt .

# Install dependencies without storing pip cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY /app ./app

# Expose the application port
EXPOSE 8000

# Command to run the application using uvicorn
CMD ["python3", "run.py"]