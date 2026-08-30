import numpy as np
import cv2
import math

class FaceAnalyzer:
    def analyze(self, image: np.ndarray, face_data: dict) -> dict:
        if not face_data or not face_data.get('face_detected') or not face_data.get('faces'):
            return {}
            
        face = face_data['faces'][0]
        bbox = face['bbox']
        landmarks = face.get('landmarks', {})
        h, w = image.shape[:2]
        
        is_centered, head_pos = self._check_centered((h, w), bbox)
        is_front_facing = self._check_front_facing(landmarks)
        head_size_ratio = self._calculate_head_size((h, w), bbox)
        face_angle = self._calculate_face_angle(landmarks)
        is_blurry, blur_score = self._check_blur(image, bbox)
        
        spacing = {
            'top': float(bbox['y'] / h),
            'bottom': float((h - (bbox['y'] + bbox['h'])) / h),
            'left': float(bbox['x'] / w),
            'right': float((w - (bbox['x'] + bbox['w'])) / w)
        }
        
        eyes_visible = bool(landmarks.get('left_eye') and landmarks.get('right_eye'))
        
        return {
            'is_centered': bool(is_centered),
            'is_front_facing': bool(is_front_facing),
            'eyes_visible': bool(eyes_visible),
            'head_size_ratio': float(head_size_ratio),
            'face_angle': float(face_angle),
            'head_position': head_pos,
            'spacing': spacing,
            'is_blurry': bool(is_blurry),
            'blur_score': float(blur_score)
        }

    def _check_centered(self, image_shape, face_bbox) -> tuple[bool, dict]:
        h, w = image_shape
        img_center_x = w / 2.0
        img_center_y = h / 2.0
        
        face_center_x = face_bbox['x'] + face_bbox['w'] / 2.0
        face_center_y = face_bbox['y'] + face_bbox['h'] / 2.0
        
        x_offset = float((face_center_x - img_center_x) / w)
        y_offset = float((face_center_y - img_center_y) / h)
        
        is_centered = bool(abs(x_offset) <= 0.1 and abs(y_offset) <= 0.1)
        return is_centered, {'x_offset': x_offset, 'y_offset': y_offset}

    def _check_front_facing(self, landmarks) -> bool:
        if not landmarks or 'left_eye' not in landmarks or 'right_eye' not in landmarks or 'nose' not in landmarks:
            return True
            
        le = landmarks['left_eye']
        re = landmarks['right_eye']
        n = landmarks['nose']
        
        eye_center_x = (le[0] + re[0]) / 2.0
        eye_dist = math.dist(le, re)
        if eye_dist == 0:
            return False
            
        nose_offset = abs(n[0] - eye_center_x) / eye_dist
        return bool(nose_offset < 0.2)

    def _calculate_face_angle(self, landmarks) -> float:
        if not landmarks or 'left_eye' not in landmarks or 'right_eye' not in landmarks:
            return 0.0
            
        le = landmarks['left_eye']
        re = landmarks['right_eye']
        
        dy = re[1] - le[1]
        dx = re[0] - le[0]
        angle = math.degrees(math.atan2(dy, dx))
        return float(angle)

    def _calculate_head_size(self, image_shape, face_bbox) -> float:
        h, _ = image_shape
        return float(face_bbox['h'] / h)

    def _check_blur(self, image, face_bbox) -> tuple[bool, float]:
        x, y, w, h = face_bbox['x'], face_bbox['y'], face_bbox['w'], face_bbox['h']
        x = max(0, x)
        y = max(0, y)
        face_roi = image[y:y+h, x:x+w]
        
        if face_roi.size == 0:
            return True, 0.0
            
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY) if len(face_roi.shape) >= 3 else face_roi
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        
        return bool(laplacian_var < 100), laplacian_var
