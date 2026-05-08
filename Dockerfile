# Utilize the slim variant of Python 3.11 to minimize container footprint and attack surface
FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr to ensure logs emit immediately to the daemon
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Isolate dependency installation to maximize Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy microservice source code
COPY . .

# Expose the ASGI server port
EXPOSE 8000

# Execute the application via Uvicorn bound universally to 0.0.0.0 for container networking
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
