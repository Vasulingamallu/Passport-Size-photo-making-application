import cv2
from app.ai.quality_analysis.validator import QualityValidator
from app.services.face_service import FaceService

class ValidationService:
    def __init__(self):
        self.validator = QualityValidator()
        self.face_service = FaceService()

    def validate_photo(self, image_path: str) -> dict:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image from {image_path}")
            
        face_result = self.face_service.detect_and_analyze(image_path)
        face_data = face_result.get('detection')
        analysis_data = face_result.get('analysis')
        
        validation = self.validator.validate(image, face_data, analysis_data)
        validation['face_details'] = face_result
        return validation

    def quick_check(self, image_path: str) -> dict:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image from {image_path}")
            
        face_data = self.face_service.detect_face(image_path)
        h, w = image.shape[:2]
        
        resolution_ok = min(h, w) >= 400
        
        return {
            'face_detected': face_data.get('face_detected', False),
            'face_count': face_data.get('face_count', 0),
            'resolution_ok': resolution_ok,
            'dimensions': {'width': w, 'height': h}
        }
