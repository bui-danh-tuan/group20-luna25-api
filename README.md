# LUNA25 Inference API (Docker)

## Chạy nhanh

docker run -p 8000:8000 ghcr.io/bui-danh-tuan/luna25-api:latest

API: http://localhost:8000  
Swagger UI: http://localhost:8000/docs  

Header xác thực (bắt buộc):  
Authorization: Bearer group20-token

---

## Ví dụ gọi API (curl)

curl -X POST "http://localhost:8000/api/v1/predict/lesion" \
  -H "Authorization: Bearer mock-token" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.mha" \
  -F "seriesInstanceUID=1.2.840.113619.2.55.3.604688435.123" \
  -F "lesionID=1" \
  -F "coordX=120.5" \
  -F "coordY=85.2" \
  -F "coordZ=42.0"

---

## Mô tả

API phục vụ bài toán **dự đoán xác suất ác tính của tổn thương phổi** trong bộ dữ liệu **LUNA25**,  
sử dụng ảnh CT ngực định dạng `.mha` hoặc `.mhd` cùng với thông tin vị trí tổn thương (tọa độ X, Y, Z).  

API nhận dữ liệu ảnh và metadata liên quan, sau đó trả về:
- Xác suất tổn thương ác tính
- Nhãn dự đoán (0: lành tính, 1: ác tính)
- Thời gian xử lý của mô hình

API được thiết kế để tích hợp vào pipeline suy luận, đánh giá mô hình và triển khai hệ thống hỗ trợ chẩn đoán.

---

## Docker Image

ghcr.io/bui-danh-tuan/luna25-api:latest
