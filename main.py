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
    
    # 2. 카메라 초기화 (2개)
    cameras = []
    states = []
    
    for idx in CAMERA_INDICES:
        logger.event_info(
            EventType.MODULE_INIT,
            f"카메라 {idx} 초기화 중"
        )
        camera = CameraCapture(idx)
        if not camera.start(CAMERA_MAX_RETRIES, CAMERA_RETRY_DELAY):
            logger.event_error(EventType.CAMERA_ERROR, f"카메라 {idx} 초기화 실패")
            # 이미 시작된 카메라 정리
            for cam in cameras:
                cam.release()
            return
        cameras.append(camera)
        states.append(SharedState())
        logger.event_info(EventType.CAMERA_OPEN, f"카메라 {idx} 초기화 완료")
    
    logger.debug(f"{len(cameras)}개 카메라 초기화 완료")
    
    # 3. 공유 상태 및 스레드 시작
    fps_counter = FPSCounter()
    threads = []
    
    # 각 카메라마다 캡처 및 추론 스레드 시작
    for i, (camera, state) in enumerate(zip(cameras, states)):
        t_capture = threading.Thread(
            target=capture_loop,
            args=(camera, state),
            daemon=True,
            name=f"capture_{i}"
        )
        t_infer = threading.Thread(
            target=inference_loop,
            args=(yolo_model, state, INFER_STRIDE),
            daemon=True,
            name=f"inference_{i}"
        )
        t_capture.start()
        t_infer.start()
        threads.append((t_capture, t_infer))
        logger.debug(f"카메라 {i} 스레드 시작")
    
    logger.event_info(
        EventType.MODULE_START,
        f"{len(cameras)}개 카메라 스레드 시작 완료"
    )
    
    # 4. 메인 루프
    saving = False
    current_camera_idx = 0  # 현재 표시 중인 카메라 인덱스 (0 또는 1)
    
    try:
        logger.event_info(
            EventType.STATE_CHANGE,
            "메인 루프 시작",
            {"exit_key": "q", "switch_key": "c", "num_cameras": len(cameras)}
        )
        
        while True:
            # 현재 선택된 카메라의 프레임 가져오기
            frame_to_show = None
            detections = []
            
            with states[current_camera_idx].frame_lock:
                if states[current_camera_idx].latest_frame is not None:
                    frame_to_show = states[current_camera_idx].latest_frame.copy()
            
            with states[current_camera_idx].det_lock:
                detections = list(states[current_camera_idx].last_detections)
            
            # 프레임이 준비되지 않았으면 대기
            if frame_to_show is None:
                time.sleep(0.001)
                continue
            
            # FPS 업데이트
            fps = fps_counter.update()
            logger.debug("프레임 처리", {"fps": round(fps, 2), "camera": CAMERA_INDICES[current_camera_idx]})
            
            # 프레임에 탐지 결과 그리기
            detection_count = len(detections)
            frame_drawn = draw_detections(
                frame_to_show,
                detections,
                yolo_model.names,
                fps,
                detection_count,
                saving,
                CAMERA_INDICES[current_camera_idx]
            )
            
            # 화면 표시
            cv2.imshow(WINDOW_NAME, frame_drawn)
            
            # 키 입력 처리
            key = cv2.waitKey(1) & 0xFF
            
            # 카메라 전환 (c 키)
            if key == ord('c'):
                current_camera_idx = (current_camera_idx + 1) % len(cameras)
                logger.event_info(
                    EventType.USER_INPUT,
                    "카메라 전환",
                    {"key": "c", "camera_index": CAMERA_INDICES[current_camera_idx]}
                )
                print(f"카메라 {CAMERA_INDICES[current_camera_idx]}번으로 전환")
            
            # 종료 (q 키)
            elif key == ord('q'):
                logger.event_info(
                    EventType.USER_INPUT,
                    "종료 신호 감지",
                    {"key": "q"}
                )
                saving = True
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
        
        # 모든 스레드 종료
        for state in states:
            state.stop_event.set()
        
        logger.debug("모든 스레드 종료 대기 중")
        for t_capture, t_infer in threads:
            t_capture.join(timeout=1.0)
            t_infer.join(timeout=1.0)
        
        # 모든 카메라 해제
        for i, camera in enumerate(cameras):
            camera.release()
            logger.event_info(EventType.CAMERA_CLOSE, f"카메라 {i} 리소스 해제")
        
        cv2.destroyAllWindows()
        logger.debug("OpenCV 윈도우 종료")
        
        logger.event_info(EventType.SYSTEM_STOP, "Person Detection System 종료 완료")


if __name__ == "__main__":
    main()
