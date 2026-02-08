"""
YOLO 추론
"""
from __future__ import annotations

import cv2
import threading
import time
from typing import List, Tuple, Optional
from utils.logger import get_logger, EventType

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

logger = get_logger("vision.yolo_infer")


class YOLOInference:
    """YOLO 추론 클래스"""
    
    def __init__(self, model_path: str, conf: float = 0.5, imgsz: int = 640):
        if YOLO is None:
            logger.event_error(
                EventType.ERROR_OCCURRED,
                "ultralytics 패키지가 설치되지 않음"
            )
            raise ImportError("ultralytics 패키지가 설치되지 않았습니다.")
        
        logger.event_info(
            EventType.MODULE_INIT,
            "YOLO 모델 초기화 시작",
            {"model_path": model_path, "conf": conf, "imgsz": imgsz}
        )
        
        self.model = YOLO(model_path)
        self.conf = conf
        self.imgsz = imgsz
        self.names = self.model.names if hasattr(self.model, "names") else []
        
        logger.event_info(
            EventType.MODULE_INIT,
            "YOLO 모델 초기화 완료",
            {"num_classes": len(self.names)}
        )
        
    def predict(self, frame: cv2.Mat) -> List[Tuple[int, int, int, int, int, float]]:
        """
        프레임에서 객체 탐지
        
        Args:
            frame: 입력 프레임
        
        Returns:
            탐지 결과 [(x1, y1, x2, y2, cls_id, score), ...]
        """
        logger.debug("추론 시작", {"conf": self.conf, "imgsz": self.imgsz})
        
        results = self.model(frame, conf=self.conf, imgsz=self.imgsz, verbose=False)
        if not results:
            logger.debug("추론 결과 없음")
            return []
        
        r = results[0]
        boxes = r.boxes
        
        detections: List[Tuple[int, int, int, int, int, float]] = []
        if boxes is not None and len(boxes) > 0:
            xyxy = boxes.xyxy.cpu().numpy()
            confs = boxes.conf.cpu().numpy()
            clss = boxes.cls.cpu().numpy().astype(int)
            
            for (x1, y1, x2, y2), sc, ci in zip(xyxy, confs, clss):
                # 사람(person) 클래스만 필터링 (COCO: cls_id=0)
                if ci == 0:
                    detections.append((int(x1), int(y1), int(x2), int(y2), int(ci), float(sc)))
        
        logger.event_info(
            EventType.DETECTION_RESULT,
            "객체 탐지 완료",
            {"num_detections": len(detections)}
        )
        
        return detections


class SharedState:
    """스레드 간 공유 상태"""
    
    def __init__(self):
        self.frame_lock = threading.Lock()
        self.det_lock = threading.Lock()
        
        self.latest_frame: Optional[cv2.Mat] = None
        self.latest_frame_seq: int = -1
        self.last_detections: List[Tuple[int, int, int, int, int, float]] = []
        
        self.stop_event = threading.Event()
        
        logger.debug("SharedState 객체 생성 완료")


def capture_loop(cap, state: SharedState) -> None:
    """캡처 스레드"""
    logger.event_info(
        EventType.MODULE_START,
        "캡처 루프 시작"
    )
    
    frame_count = 0
    while not state.stop_event.is_set():
        ok, frame = cap.read_frame()
        if not ok:
            time.sleep(0.001)
            continue
        
        with state.frame_lock:
            state.latest_frame = frame
            state.latest_frame_seq += 1
            frame_count += 1
        
        # 100 프레임마다 디버그 로깅
        if frame_count % 100 == 0:
            logger.debug("프레임 캡처 진행", {"frame_count": frame_count})
    
    logger.event_info(
        EventType.MODULE_STOP,
        "캡처 루프 종료",
        {"total_frames": frame_count}
    )


def inference_loop(
    model: YOLOInference,
    state: SharedState,
    infer_stride: int = 3
) -> None:
    """추론 스레드"""
    logger.event_info(
        EventType.MODULE_START,
        "추론 루프 시작",
        {"infer_stride": infer_stride}
    )
    
    last_processed_seq = -infer_stride
    inference_count = 0
    
    while not state.stop_event.is_set():
        frame_to_infer = None
        with state.frame_lock:
            seq = state.latest_frame_seq
            if state.latest_frame is not None and (seq - last_processed_seq) >= infer_stride:
                frame_to_infer = state.latest_frame.copy()
                last_processed_seq = seq
        
        if frame_to_infer is None:
            time.sleep(0.001)
            continue
        
        logger.debug("추론 시작", {"frame_seq": last_processed_seq})
        detections = model.predict(frame_to_infer)
        inference_count += 1
        
        with state.det_lock:
            state.last_detections = detections
        
        logger.debug(
            "추론 결과 저장",
            {"num_detections": len(detections), "inference_count": inference_count}
        )
    
    logger.event_info(
        EventType.MODULE_STOP,
        "추론 루프 종료",
        {"total_inferences": inference_count}
    )
