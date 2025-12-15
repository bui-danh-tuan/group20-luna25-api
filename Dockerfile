# =========================
# Base image
# =========================
FROM python:3.10-slim

# =========================
# Environment
# =========================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# =========================
# Working directory
# =========================
WORKDIR /app

# =========================
# Install dependencies
# =========================
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# =========================
# Copy source code
# =========================
COPY main.py .

# =========================
# Expose port
# =========================
EXPOSE 8000

# =========================
# Run app
# =========================
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
