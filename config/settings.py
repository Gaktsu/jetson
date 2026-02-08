"""
프로젝트 전역 설정 및 상수
"""
import os

# 프로젝트 루트 디렉토리
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 모델 설정
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
DEFAULT_MODEL = "person_detect_v4.pt"
MODEL_PATH = os.path.join(MODEL_DIR, DEFAULT_MODEL)

# 카메라 설정
CAMERA_INDEX = 0
CAMERA_BACKEND = "CAP_DSHOW"  # Windows 권장
CAMERA_BUFFER_SIZE = 1
CAMERA_MAX_RETRIES = 10
CAMERA_RETRY_DELAY = 5.0  # 초

# YOLO 추론 설정
INFER_STRIDE = 3  # N프레임마다 1회 추론
CONFIDENCE_THRESHOLD = 0.5
IMAGE_SIZE = 640
TARGET_CLASS_ID = 0  # person 클래스

# 경고 영역 설정
WARNING_ZONE_RATIO = 0.8  # 화면 우측 20%

# FPS 계산 설정
FPS_UPDATE_INTERVAL = 1.0  # 초

# 저장 설정
SAVE_DIR = os.path.join(PROJECT_ROOT, "SaveVideos")
os.makedirs(SAVE_DIR, exist_ok=True)

# 디스플레이 설정
WINDOW_NAME = "Real-time YOLO"
FONT = "cv2.FONT_HERSHEY_SIMPLEX"
FONT_SCALE = 0.6
FONT_THICKNESS = 2

# 색상 설정 (BGR)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_YELLOW = (0, 255, 255)
COLOR_BLACK = (0, 0, 0)
