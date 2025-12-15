import time
import random
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI(
    title="LUNA25 Model Inference API",
    version="5.0",
    description="Mock API for LUNA25 lesion prediction (random output)"
)

security = HTTPBearer()

# =========================
# Auth check (Mock)
# =========================
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    if token != "mock-token":
        raise HTTPException(
            status_code=401,
            detail={
                "errorCode": "UNAUTHORIZED",
                "message": "Invalid or missing Bearer token"
            }
        )
    return token


# =========================
# API Endpoint
# =========================
@app.post("/api/v1/predict/lesion")
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

    # Optional fields
    patientID: str | None = Form(None),
    studyDate: str | None = Form(None),
    ageAtStudyDate: int | None = Form(None),
    gender: str | None = Form(None)
):
    start_time = time.time()

    # =========================
    # Validate file format
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

    # Validate gender (if provided)
    if gender and gender not in ["Male", "Female"]:
        raise HTTPException(
            status_code=400,
            detail={
                "errorCode": "INVALID_FIELD",
                "message": "gender must be 'Male' or 'Female'"
            }
        )

    # =========================
    # MOCK MODEL INFERENCE
    # =========================
    probability = round(random.uniform(0.0, 1.0), 3)
    prediction_label = 1 if probability >= 0.5 else 0

    processing_time_ms = int((time.time() - start_time) * 1000)

    # =========================
    # Response
    # =========================
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "data": {
                "seriesInstanceUID": seriesInstanceUID,
                "lesionID": lesionID,
                "probability": probability,
                "predictionLabel": prediction_label,
                "processingTimeMs": processing_time_ms
            }
        }
    )
