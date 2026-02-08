"""
후처리 (NMS, bbox 변환 등)
"""
import cv2
from typing import List, Tuple
from datetime import datetime


def check_intrusion(
    detections: List[Tuple[int, int, int, int, int, float]],
    warning_zone: Tuple[int, int, int, int]
) -> bool:
    """
    경고 영역 침입 확인
    
    Args:
        detections: 탐지 결과
        warning_zone: (x1, y1, x2, y2) 경고 영역
    
    Returns:
        침입 여부
    """
    wx1, wy1, wx2, wy2 = warning_zone
    
    for x1, y1, x2, y2, cls_id, score in detections:
        # 박스가 경고 영역과 겹치는지 확인
        if not (x2 < wx1 or x1 > wx2 or y2 < wy1 or y1 > wy2):
            return True
    return False


def draw_detections(
    frame: cv2.Mat,
    detections: List[Tuple[int, int, int, int, int, float]],
    names: List[str],
    fps: float = 0.0,
    detection_count: int = 0,
    saving: bool = False,
    camera_index: int = 0
) -> cv2.Mat:
    """
    탐지 결과를 프레임에 그리기
    """
    h, w = frame.shape[:2]
    
    # 경고 영역 정의 (화면 우측 20%)
    warning_zone_x1 = int(w * 0.8)
    warning_zone = (warning_zone_x1, 0, w, h)
    
    # 반투명 경고 영역 그리기
    overlay = frame.copy()
    cv2.rectangle(overlay, (warning_zone_x1, 0), (w, h), (0, 0, 255), -1)
    cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
    cv2.rectangle(frame, (warning_zone_x1, 0), (w, h), (0, 0, 255), 2)
    
    # 침입 감지
    intrusion_detected = check_intrusion(detections, warning_zone)
    
    # 바운딩 박스 그리기
    for x1, y1, x2, y2, cls_id, score in detections:
        if cls_id == 0:  # person
            # 침입 여부에 따라 색상 변경
            wx1, wy1, wx2, wy2 = warning_zone
            is_in_zone = not (x2 < wx1 or x1 > wx2 or y2 < wy1 or y1 > wy2)
            
            color = (0, 0, 255) if is_in_zone else (0, 255, 0)
            thickness = 3 if is_in_zone else 2
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
            
            label = names[cls_id] if 0 <= cls_id < len(names) else str(cls_id)
            text = f"{label} {score:.2f}"
            cv2.putText(frame, text, (x1, max(0, y1 - 5)),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
    
    # Warning 문구
    if intrusion_detected and not saving:
        warning_text = "WARNING!"
        font_scale = 2.0
        thickness = 4
        text_size = cv2.getTextSize(warning_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
        text_x = (w - text_size[0]) // 2
        text_y = (h + text_size[1]) // 2
        
        cv2.rectangle(frame, (text_x - 20, text_y - text_size[1] - 20),
                     (text_x + text_size[0] + 20, text_y + 10), (0, 0, 0), -1)
        cv2.putText(frame, warning_text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness, cv2.LINE_AA)
    
    # 우상단 정보
    font_scale = 0.6
    thickness = 2
    y_offset = 30
    
    if saving:
        text = "Saving..."
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
        x_pos = w - text_size[0] - 10
        cv2.putText(frame, text, (x_pos, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), thickness, cv2.LINE_AA)
    else:
        color = (0, 255, 255)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 시간
        text_time = f"Time: {current_time}"
        text_size = cv2.getTextSize(text_time, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
        x_pos = w - text_size[0] - 10
        cv2.putText(frame, text_time, (x_pos, y_offset),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)
        
        # FPS
        text_fps = f"FPS: {fps:.1f}"
        text_size = cv2.getTextSize(text_fps, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
        x_pos = w - text_size[0] - 10
        cv2.putText(frame, text_fps, (x_pos, y_offset + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)
        
        # 탐지 수
        text_count = f"Detected: {detection_count}"
        text_size = cv2.getTextSize(text_count, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
        x_pos = w - text_size[0] - 10
        cv2.putText(frame, text_count, (x_pos, y_offset + 60),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)
        
        # 카메라 번호
        text_camera = f"Camera: {camera_index}"
        text_size = cv2.getTextSize(text_camera, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)[0]
        x_pos = w - text_size[0] - 10
        cv2.putText(frame, text_camera, (x_pos, y_offset + 90),
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)
    
    # 좌하단 메뉴 (항상 표시)
    menu_font_scale = 0.5
    menu_thickness = 1
    menu_color = (255, 255, 255)
    menu_y_start = h - 50
    
    cv2.putText(frame, "[Q] Exit", (10, menu_y_start),
               cv2.FONT_HERSHEY_SIMPLEX, menu_font_scale, menu_color, menu_thickness, cv2.LINE_AA)
    cv2.putText(frame, "[C] Switch Camera", (10, menu_y_start + 20),
               cv2.FONT_HERSHEY_SIMPLEX, menu_font_scale, menu_color, menu_thickness, cv2.LINE_AA)
    
    return frame
