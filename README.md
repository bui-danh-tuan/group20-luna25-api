# LUNA25 Mock Inference API

## Run with Docker (no login required)

```bash
docker run -d -p 8000:8000 \
  -e API_TOKEN=mock-token \
  ghcr.io/bui-danh-tuan/luna25-api:latest
