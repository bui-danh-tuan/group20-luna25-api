FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN mkdir -p /app/luna25 && \
    wget -O /app/luna25/best_metric_cls_model.pth \
    https://github.com/bui-danh-tuan/group20-luna25-api/releases/download/V1/best_metric_cls_model.pth


EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
