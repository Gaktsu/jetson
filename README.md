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

- `CAMERA_INDICES`: 사용 가능한 카메라 인덱스 리스트 (예: [0, 1])
- `MODEL_PATH`: YOLO 모델 경로
- `CONFIDENCE_THRESHOLD`: 신뢰도 임계값
- `INFER_STRIDE`: 추론 간격 (N프레임마다)
- `WARNING_ZONE_RATIO`: 경고 영역 비율

## 사용법

### 키보드 단축키

- **Q**: 프로그램 종료
- **C**: 카메라 전환 (여러 카메라가 연결된 경우)

### 다중 카메라 설정

`config/settings.py`에서 카메라 인덱스를 설정하세요:

```python
CAMERA_INDICES = [0, 1]  # 카메라 0번과 1번 사용
```

프로그램 실행 시 기본적으로 0번 카메라가 표시되며, `C` 키를 눌러 다른 카메라로 전환할 수 있습니다.
모든 카메라는 백그라운드에서 동시에 촬영되며, 화면에는 선택된 하나의 카메라만 표시됩니다.

## 지원 플랫폼

- **Windows**: DirectShow (CAP_DSHOW) 백엔드 사용
- **Jetson (NVIDIA)**: Video4Linux2 (CAP_V4L2) 백엔드 자동 사용
- **Linux (일반)**: Video4Linux2 (CAP_V4L2) 백엔드 사용

카메라 백엔드는 운영체제를 자동으로 감지하여 설정됩니다.

## 기능

- ✅ 실시간 사람 탐지 (YOLO)
- ✅ 경고 영역 침입 감지
- ✅ FPS, 시간, 탐지 수 표시
- ✅ 다중 카메라 지원 및 실시간 전환
- ✅ 모든 카메라 백그라운드 동시 촬영
- ✅ OS별 카메라 백엔드 자동 감지 (Windows/Jetson/Linux)
- ✅ 카메라 오류 진단 및 자동 재시도
- ✅ 로깅 시스템
- 🚧 GPS 연동 (개발 중)
- 🚧 부저 경고 (개발 중)
- 🚧 영상 저장 (개발 중)

## 라이선스

MIT
