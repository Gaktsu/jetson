"""
부저 제어
"""


class Buzzer:
    """부저 제어 클래스"""
    
    def __init__(self, pin: int = 18):
        self.pin = pin
        self.is_active = False
        
    def start(self) -> bool:
        """부저 초기화"""
        # TODO: GPIO 핀 초기화
        print(f"부저 초기화 (핀: {self.pin})")
        return True
    
    def activate(self):
        """부저 켜기"""
        # TODO: GPIO 핀 HIGH
        self.is_active = True
        print("부저 활성화")
    
    def deactivate(self):
        """부저 끄기"""
        # TODO: GPIO 핀 LOW
        self.is_active = False
        print("부저 비활성화")
    
    def stop(self):
        """부저 정리"""
        self.deactivate()
