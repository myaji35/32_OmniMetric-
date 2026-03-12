"""
Upload Endpoint
CSV 파일 업로드 API
"""
import io
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import Dict, Any

from app.api.v1.dependencies import verify_api_key
from app.security.input_validator import validate_file_size
from app.core.config import settings


router = APIRouter()


@router.post(
    "/upload",
    summary="CSV 파일 업로드",
    description="CSV 파일을 업로드하여 데이터를 분석 가능한 형태로 변환합니다.",
)
async def upload_csv(
    file: UploadFile = File(..., description="CSV 파일"),
    target_column: str = Form(..., description="타겟 컬럼명"),
    _: None = Depends(verify_api_key),
) -> Dict[str, Any]:
    """CSV 파일 업로드 및 파싱"""
    # 1. 파일 형식 검증
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV 파일만 업로드 가능합니다.",
        )

    # 2. 파일 읽기
    contents = await file.read()

    # 3. 크기 검증
    try:
        validate_file_size(len(contents), settings.max_upload_size_mb)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=str(e))

    # 4. CSV 파싱
    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV 파싱 실패: {str(e)}",
        )

    # 5. 타겟 컬럼 확인
    if target_column not in df.columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"타겟 컬럼 '{target_column}'을 찾을 수 없습니다. "
            f"가능한 컬럼: {list(df.columns)}",
        )

    # 6. JSON 변환하여 반환
    data = df.to_dict(orient="records")

    return {
        "filename": file.filename,
        "rows": len(data),
        "columns": list(df.columns),
        "target_column": target_column,
        "data": data,
        "message": f"CSV 파일 업로드 성공: {len(data)}행 x {len(df.columns)}열",
    }
