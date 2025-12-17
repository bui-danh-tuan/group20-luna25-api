import time
import tempfile
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import SimpleITK


# =========================
# IMPORT ĐÚNG THEO CẤU TRÚC THƯ MỤC
# =========================
import time

from luna25.processor import MalignancyProcessor
from luna25.inference import itk_image_to_numpy_image


# =========================
# HÀM CHẠY MODEL (BASELINE SAFE)
# =========================

async def run_model_inference(
    *,
    file,                     # UploadFile
    seriesInstanceUID: str,
    lesionID: int,
    coordX: float,
    coordY: float,
    coordZ: float,
    timeout_sec: int = 600
):
    """
    Run LUNA25 inference directly from API request inputs.

    Returns:
        dict {
            seriesInstanceUID,
            lesionID,
            probability,
            predictionLabel,
            processingTimeMs
        }
    """

    from luna25.inference import itk_image_to_numpy_image

    start_time = time.time()

    # =========================
    # 1. Save uploaded file
    # =========================
    suffix = ".mha" if file.filename.endswith(".mha") else ".mhd"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        ct_path = tmpdir / f"{seriesInstanceUID}{suffix}"

        with open(ct_path, "wb") as f:
            f.write(await file.read())

        # =========================
        # 2. Read CT + convert
        # =========================
        image_itk = SimpleITK.ReadImage(str(ct_path))
        image_np, header = itk_image_to_numpy_image(image_itk)

        # =========================
        # 3. Timeout check (pre)
        # =========================
        if time.time() - start_time > timeout_sec:
            raise TimeoutError("Inference timeout exceeded")

        # =========================
        # 4. Run model
        # =========================\
        processor = MalignancyProcessor()
        processor.define_inputs(
            image=image_np,
            header=header,
            coords=[(coordX, coordY, coordZ)]
        )

        probability, x = processor.predict()
        prediction_label = 1 if probability >= 0.5 else 0
        print("="*100)
        print(header)
        print(probability)
        print([(coordX, coordY, coordZ)])

    # =========================
    # 5. Return result
    # =========================
    return probability, prediction_label


app = FastAPI(
    title="LUNA25 Model Inference API",
    version="5.0",
    description="API for LUNA25 lesion prediction"
)

security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token != "group20-token":
        raise HTTPException(
            status_code=401,
            detail={
                "errorCode": "UNAUTHORIZED",
                "message": "Invalid or missing Bearer token"
            }
        )
    return token


@app.post(
    "/api/v1/predict/lesion",
    responses={
        200: {
            "description": "Success – Model inference completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "data": {
                            "seriesInstanceUID": "1.2.840.113619.2.55.3.604688435.781.1596533431.467",
                            "lesionID": 1,
                            "probability": 0.742,
                            "predictionLabel": 1,
                            "processingTimeMs": 1280
                        }
                    }
                }
            }
        },
        400: {
            "description": "Bad Request – Invalid input, file format, or field value",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_file_format": {
                            "summary": "Invalid file format",
                            "value": {
                                "errorCode": "INVALID_FILE_FORMAT",
                                "message": "Only .mha or .mhd files are supported"
                            }
                        },
                        "missing_series_uid": {
                            "summary": "Missing seriesInstanceUID",
                            "value": {
                                "errorCode": "INVALID_FILE_FORMAT",
                                "message": "seriesInstanceUID is required"
                            }
                        },
                        "invalid_field": {
                            "summary": "Invalid field value",
                            "value": {
                                "errorCode": "INVALID_FIELD",
                                "message": "gender must be 'Male' or 'Female'"
                            }
                        }
                    }
                }
            }
        },
        401: {
            "description": "Unauthorized – Missing or invalid Bearer token",
            "content": {
                "application/json": {
                    "example": {
                        "errorCode": "UNAUTHORIZED",
                        "message": "Invalid or missing Bearer token"
                    }
                }
            }
        },
        403: {
            "description": "Forbidden – Access denied",
            "content": {
                "application/json": {
                    "example": {
                        "errorCode": "FORBIDDEN",
                        "message": "Token hợp lệ nhưng không có quyền truy cập hoặc đã vượt quá giới hạn gọi API."
                    }
                }
            }
        },
        404: {
            "description": "Not Found – Endpoint not found or model service offline",
            "content": {
                "application/json": {
                    "example": {
                        "errorCode": "NOT_FOUND",
                        "message": "Endpoint không tồn tại hoặc Service Model đang offline."
                    }
                }
            }
        },
        422: {
            "description": "Unprocessable Entity – Model processing error",
            "content": {
                "application/json": {
                    "example": {
                        "errorCode": "PROCESSING_ERROR",
                        "message": "Lỗi nội tại của Model khi xử lý dữ liệu ảnh."
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error – Unexpected server failure",
            "content": {
                "application/json": {
                    "example": {
                        "errorCode": "INTERNAL_SERVER_ERROR",
                        "message": "Lỗi hệ thống server không xác định."
                    }
                }
            }
        },
        504: {
            "description": "Gateway Timeout – Processing time exceeded the limit",
            "content": {
                "application/json": {
                    "example": {
                        "errorCode": "GATEWAY_TIMEOUT",
                        "message": "Thời gian xử lý vượt quá 600 giây.",
                        "processingTimeSec": 610
                    }
                }
            }
        }
    }
)

async def predict_lesion(
    token: str = Depends(verify_token),

    # File
    file: UploadFile = File(...),

    # Required fields
    seriesInstanceUID: str = Form(...),
    lesionID: int = Form(...),
    coordX: float = Form(...),
    coordY: float = Form(...),
    coordZ: float = Form(...),

    # Optional fields (API-level, baseline không dùng)
    patientID: str | None = Form(None),
    studyDate: str | None = Form(None),
    ageAtStudyDate: int | None = Form(None),
    gender: str | None = Form(None)
):
    start_time = time.time()

    # =========================
    # Validate input
    # =========================
    if not (file.filename.endswith(".mha") or file.filename.endswith(".mhd")):
        raise HTTPException(
            status_code=400,
            detail={
                "errorCode": "INVALID_FILE_FORMAT",
                "message": "Only .mha or .mhd files are supported"
            }
        )

    if not seriesInstanceUID:
        raise HTTPException(
            status_code=400,
            detail={
                "errorCode": "INVALID_FILE_FORMAT",
                "message": "seriesInstanceUID is required"
            }
        )

    if gender and gender not in ["Male", "Female"]:
        raise HTTPException(
            status_code=400,
            detail={
                "errorCode": "INVALID_FIELD",
                "message": "gender must be 'Male' or 'Female'"
            }
        )
    
    probability, label = await run_model_inference(
        file=file,
        seriesInstanceUID=seriesInstanceUID,
        lesionID=lesionID,
        coordX=coordX,
        coordY=coordY,
        coordZ=coordZ
    )

    processing_time_ms = int((time.time() - start_time) * 1000)

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "data": {
                "seriesInstanceUID": seriesInstanceUID,
                "lesionID": lesionID,
                "probability": float(round(float(probability), 3)),
                "predictionLabel": label,
                "processingTimeMs": processing_time_ms
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
