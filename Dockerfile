FROM python:3.11-slim

WORKDIR /app

# Cài wget
RUN apt-get update && apt-get install -y wget \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# TẢI MODEL TỪ GITHUB RELEASE (TAG ĐÚNG)
RUN mkdir -p /app/luna25 && \
    wget -O /app/luna25/best_metric_cls_model.pth \
    https://github.com/bui-danh-tuan/group20-luna25-api/releases/download/v1/best_metric_cls_model.pth

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
