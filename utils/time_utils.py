"""
시간 관련 유틸리티
"""
from datetime import datetime
import time


def get_timestamp() -> str:
    """현재 타임스탬프 반환 (문자열)"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_formatted_time() -> str:
    """포맷된 현재 시간 반환"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class FPSCounter:
    """FPS 계산 클래스"""
    
    def __init__(self):
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0.0
    
    def update(self) -> float:
        """프레임 카운트 업데이트 및 FPS 계산"""
        self.frame_count += 1
        elapsed = time.time() - self.start_time
        
        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()
        
        return self.fps
    
    def get_fps(self) -> float:
        """현재 FPS 반환"""
        return self.fps
