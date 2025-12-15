# LUNA25 Inference API (Docker)

## Chạy nhanh

docker run -p 8000:8000 ghcr.io/bui-danh-tuan/luna25-api:latest

API: http://localhost:8000  
Swagger UI: http://localhost:8000/docs  

Header xác thực (bắt buộc):  
Authorization: Bearer group20-token

---

## Ví dụ gọi API (curl)

curl --location 'http://localhost:8000/api/v1/predict/lesion' \
--header 'Authorization: Bearer group20-token' \
--form 'file=@"/E:/Code/VDHD/Data/1.2.840.113654.2.55.10001915497607871704679012670488177360.mha"' \
--form 'seriesInstanceUID="1.2.840.113654.2.55.10001915497607871704679012670488177360"' \
--form 'lesionID="1"' \
--form 'coordX="87.13"' \
--form 'coordY="-70.04"' \
--form 'coordZ="-191.68"' \
--form 'gender="Female"'

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
