"""
IMU 센서 (선택 사항)
"""


class IMU:
    """IMU 센서 제어 클래스"""
    
    def __init__(self):
        self.running = False
        
    def start(self) -> bool:
        """IMU 초기화"""
        # TODO: IMU 센서 초기화
        print("IMU 초기화 중...")
        return True
    
    def read_data(self):
        """IMU 데이터 읽기"""
        # TODO: 가속도, 자이로 데이터 읽기
        return None
    
    def stop(self):
        """IMU 중지"""
        self.running = False
