from fastapi import APIRouter, UploadFile, HTTPException, File
from starlette import status
from ultralytics import YOLO

import io
from PIL import Image
from typing import Any, Dict, List

router = APIRouter(
    prefix = "/yolo",
    tags = ["YOLO"]
)

try:
    model = YOLO('yolov8n.pt')
    print(f"모델 : {model.model_name}")
except Exception as e:
    print(f"error : {e}")
    raise RuntimeError("모델 로드 실패...")


# 객체 검출
@router.post("/detect", summary = "YOLO 객체 검출")
async def detect_objects(file: UploadFile = File(...)):
    # 애외 1. 파일이 이미지가 아님
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = {"이미지 파일을 업로드 해주세요."}
        )
    try:
        # 이미지 데이터 읽기
        image_byte = await file.read()
        image = Image.open(io.BytesIO(image_byte))

        results = model(image)
        # 결과 저장할 리스트
        all_detections: List[Dict[str, Any]] = []
        r = results[0]

        # 검출된 객체가 있을 경우
        if len(r.boxes)>0:
            for box in r.boxes:
                coords = box.xyxy[0].tolist()
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                confidence = float(box.conf[0])

                # 출력 리스트에 저장
                all_detections.append({
                    "box": [round(c, 2) for c in coords],
                    "class": class_name,
                    "confidence": round(confidence, 2)
                })
        return {
            "status": "success",
            "검출된 개수(count)": len(all_detections),
            "detections": all_detections
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = {"message": f"서버 에러: {e}"}
        )

