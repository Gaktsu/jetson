"""
이미지 전처리
"""
import cv2
import numpy as np


def resize_frame(frame: cv2.Mat, target_size: int = 640) -> cv2.Mat:
    """
    프레임 크기 조정
    
    Args:
        frame: 입력 프레임
        target_size: 목표 크기 (정사각형 기준)
    
    Returns:
        리사이즈된 프레임
    """
    h, w = frame.shape[:2]
    scale = target_size / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    return cv2.resize(frame, (new_w, new_h))


def normalize_frame(frame: cv2.Mat) -> np.ndarray:
    """
    프레임 정규화 (0-1 범위)
    
    Args:
        frame: 입력 프레임
    
    Returns:
        정규화된 프레임
    """
    return frame.astype(np.float32) / 255.0
