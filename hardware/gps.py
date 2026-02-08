"""
GPS 처리 (NEO-6M)
"""
from errors.enums import GPSError


class GPS:
    """GPS 장치 제어 클래스"""
    
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.running = False
        
    def start(self) -> bool:
        """GPS 시작"""
        # TODO: GPS 연결 구현
        print(f"GPS 초기화 중... (포트: {self.port})")
        return True
    
    def read_data(self):
        """GPS 데이터 읽기"""
        # TODO: GPS 데이터 읽기 구현
        return None
    
    def stop(self):
        """GPS 중지"""
        self.running = False
