# Person Detection System

실시간 사람 탐지 및 경고 시스템

## 프로젝트 구조

```
project/
 ├─ main.py                 # 전체 흐름 제어
 │
 ├─ config/
 │   └─ settings.py         # 상수, 경로, 파라미터
 │
 ├─ errors/
 │   └─ enums.py            # CameraError, GPSError 등
 │
 ├─ hardware/
 │   ├─ camera.py           # USB / CSI 초기화 + 캡처
 │   ├─ gps.py              # NEO-6M 처리
 │   ├─ buzzer.py           # 부저 제어
 │   └─ imu.py              # IMU 센서
 │
 ├─ vision/
 │   ├─ preprocess.py       # resize / normalize
 │   ├─ yolo_infer.py       # YOLO 추론
 │   └─ postprocess.py      # NMS / bbox 변환
 │
 ├─ system/
 │   ├─ autostart.py        # 부팅 자동 실행
 │   ├─ storage.py          # 용량 관리
 │   └─ watchdog.py         # 재시작 / 오류 감지
 │
 └─ utils/
     ├─ logger.py           # 로그
     └─ time_utils.py       # timestamp
```

## 설치

```bash
pip install ultralytics opencv-python
```

## 실행

```bash
# 기본 실행
python main.py

# Watchdog로 실행 (자동 재시작)
python system/watchdog.py
```

## 설정

`config/settings.py`에서 다음 항목을 수정할 수 있습니다:

- `CAMERA_INDEX`: 카메라 인덱스
- `MODEL_PATH`: YOLO 모델 경로
- `CONFIDENCE_THRESHOLD`: 신뢰도 임계값
- `INFER_STRIDE`: 추론 간격 (N프레임마다)
- `WARNING_ZONE_RATIO`: 경고 영역 비율

## 기능

- ✅ 실시간 사람 탐지 (YOLO)
- ✅ 경고 영역 침입 감지
- ✅ FPS, 시간, 탐지 수 표시
- ✅ 카메라 오류 진단 및 자동 재시도
- ✅ 로깅 시스템
- 🚧 GPS 연동 (개발 중)
- 🚧 부저 경고 (개발 중)
- 🚧 영상 저장 (개발 중)

## 라이선스

MIT
