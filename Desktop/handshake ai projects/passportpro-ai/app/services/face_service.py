import cv2
import time
from app.ai.face_detection.detector import FaceDetector
from app.ai.face_detection.analyzer import FaceAnalyzer

class FaceService:
    def __init__(self):
        self.detector = FaceDetector()
        self.analyzer = FaceAnalyzer()

    def detect_and_analyze(self, image_path: str) -> dict:
        start_time = time.time()
        
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image at {image_path}")
            
        detect_result = self.detector.detect(image)
        
        if not detect_result.get('face_detected'):
            return {
                'detection': detect_result,
                'analysis': {},
                'processing_time': time.time() - start_time
            }
            
        analysis_result = self.analyzer.analyze(image, detect_result)
        
        return {
            'detection': detect_result,
            'analysis': analysis_result,
            'processing_time': time.time() - start_time
        }

    def detect_face(self, image_path: str) -> dict:
        return self.detector.detect_from_file(image_path)

    def analyze_face(self, image_path: str, face_data: dict) -> dict:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image at {image_path}")
        return self.analyzer.analyze(image, face_data)
