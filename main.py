"""
메인 실행 파일 - 전체 흐름 제어
"""
import cv2
import threading
import time

from config.settings import *
from hardware.camera import CameraCapture
from vision.yolo_infer import YOLOInference, SharedState, capture_loop, inference_loop
from vision.postprocess import draw_detections
from utils.time_utils import FPSCounter
from utils.logger import get_logger, EventType

# 중앙 Orchestrator 로거
logger = get_logger("main_orchestrator")


def main():
    """메인 함수"""
    logger.event_info(EventType.SYSTEM_START, "Person Detection System 시작")
    
    # 1. YOLO 모델 로드
    try:
        logger.event_info(
            EventType.MODULE_INIT,
            "YOLO 모델 로드 중",
            {"model_path": MODEL_PATH}
        )
        yolo_model = YOLOInference(MODEL_PATH, CONFIDENCE_THRESHOLD, IMAGE_SIZE)
        logger.event_info(EventType.MODULE_INIT, "YOLO 모델 로드 완료")
    except Exception as e:
        logger.event_error(
            EventType.ERROR_OCCURRED,
            "YOLO 모델 로드 실패",
            {"error": str(e)},
            exc_info=True
        )
        return
    
    # 2. 카메라 초기화
    logger.event_info(
        EventType.MODULE_INIT,
        "카메라 초기화 중",
        {"camera_index": CAMERA_INDEX}
    )
    camera = CameraCapture(CAMERA_INDEX)
    if not camera.start(CAMERA_MAX_RETRIES, CAMERA_RETRY_DELAY):
        logger.event_error(EventType.CAMERA_ERROR, "카메라 초기화 실패")
        return
    logger.event_info(EventType.CAMERA_OPEN, "카메라 초기화 완료")
    
    # 3. 공유 상태 및 스레드 시작
    state = SharedState()
    fps_counter = FPSCounter()
    
    logger.debug("공유 상태 객체 생성 완료")
    
    t_capture = threading.Thread(target=capture_loop, args=(camera, state), daemon=True)
    t_infer = threading.Thread(
        target=inference_loop,
        args=(yolo_model, state, INFER_STRIDE),
        daemon=True
    )
    
    t_capture.start()
    t_infer.start()
    logger.event_info(
        EventType.MODULE_START,
        "캡처 및 추론 스레드 시작",
        {"threads": ["capture", "inference"]}
    )
    
    # 4. 메인 루프
    saving = False
    
    try:
        logger.event_info(
            EventType.STATE_CHANGE,
            "메인 루프 시작",
            {"exit_key": "q"}
        )
        
        while True:
            # 최신 프레임 가져오기
            frame_to_show = None
            with state.frame_lock:
                if state.latest_frame is not None:
                    frame_to_show = state.latest_frame.copy()
            
            if frame_to_show is None:
                time.sleep(0.001)
                continue
            
            # FPS 업데이트
            fps = fps_counter.update()
            logger.debug("프레임 처리", {"fps": round(fps, 2)})
            
            # 탐지 결과 가져오기
            with state.det_lock:
                detections = list(state.last_detections)
            
            # 프레임에 그리기
            detection_count = len(detections)
            logger.debug("탐지 결과 획득", {"count": detection_count})
            
            frame_drawn = draw_detections(
                frame_to_show,
                detections,
                yolo_model.names,
                fps,
                detection_count,
                saving
            )
            
            # 화면 표시
            cv2.imshow(WINDOW_NAME, frame_drawn)
            
            # 키 입력 처리
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                logger.event_info(
                    EventType.USER_INPUT,
                    "종료 신호 감지",
                    {"key": "q"}
                )
                saving = True
                
                # 저장중 화면 표시
                with state.frame_lock:
                    if state.latest_frame is not None:
                        fresh_frame = state.latest_frame.copy()
                    else:
                        fresh_frame = frame_to_show.copy()
                
                # 바운딩 박스만 그리기
                for x1, y1, x2, y2, cls_id, score in detections:
                    if cls_id == 0:
                        cv2.rectangle(fresh_frame, (x1, y1), (x2, y2), COLOR_GREEN, 2)
                        label = yolo_model.names[cls_id] if 0 <= cls_id < len(yolo_model.names) else str(cls_id)
                        text = f"{label} {score:.2f}"
                        cv2.putText(
                            fresh_frame, text, (x1, max(0, y1 - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_GREEN, 1, cv2.LINE_AA
                        )
                
                # "Saving..." 문구
                h, w = fresh_frame.shape[:2]
                text = "Saving..."
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, FONT_THICKNESS)[0]
                x_pos = w - text_size[0] - 10
                cv2.putText(
                    fresh_frame, text, (x_pos, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, COLOR_RED, FONT_THICKNESS, cv2.LINE_AA
                )
                
                cv2.imshow(WINDOW_NAME, fresh_frame)
                cv2.waitKey(500)
                break
    
    except KeyboardInterrupt:
        logger.event_warning(
            EventType.USER_INPUT,
            "키보드 인터럽트로 종료"
        )
    except Exception as e:
        logger.event_error(
            EventType.ERROR_OCCURRED,
            "메인 루프 오류 발생",
            {"error": str(e)},
            exc_info=True
        )
    finally:
        # 5. 정리
        logger.event_info(
            EventType.MODULE_STOP,
            "시스템 종료 프로세스 시작"
        )
        state.stop_event.set()
        
        logger.debug("스레드 종료 대기 중")
        t_capture.join(timeout=1.0)
        t_infer.join(timeout=1.0)
        
        camera.release()
        logger.event_info(EventType.CAMERA_CLOSE, "카메라 리소스 해제")
        
        cv2.destroyAllWindows()
        logger.debug("OpenCV 윈도우 종료")
        
        logger.event_info(EventType.SYSTEM_STOP, "Person Detection System 종료 완료")


if __name__ == "__main__":
    main()
