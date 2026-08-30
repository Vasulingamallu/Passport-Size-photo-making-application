import cv2
import numpy as np
import logging
import math

logger = logging.getLogger(__name__)

# Check if MediaPipe solutions API is available
HAS_MEDIAPIPE = False
try:
    import mediapipe as mp
    if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'face_detection'):
        HAS_MEDIAPIPE = True
    else:
        from mediapipe.python.solutions import face_detection as mp_face_detection
        mp.solutions = type('obj', (object,), {'face_detection': mp_face_detection})
        HAS_MEDIAPIPE = True
except Exception as e:
    HAS_MEDIAPIPE = False
    logger.info(f"MediaPipe solutions not available ({e}), using OpenCV Haar cascades.")


class FaceDetector:
    def __init__(self, min_confidence=0.4):
        self.min_confidence = min_confidence
        self.use_mediapipe = False
        self.face_detection = None
        self.mp_face_detection = None
        
        if HAS_MEDIAPIPE:
            try:
                import mediapipe as mp
                self.mp_face_detection = mp.solutions.face_detection
                # model_selection=1 is optimized for full-range / distance / scenery photos (up to 5 meters)
                self.face_detection = self.mp_face_detection.FaceDetection(
                    model_selection=1,
                    min_detection_confidence=self.min_confidence
                )
                self.use_mediapipe = True
            except Exception as e:
                logger.warning(f"Failed to initialize MediaPipe FaceDetection: {e}. Falling back to OpenCV.")
                self.use_mediapipe = False
        
        cascade_dir = cv2.data.haarcascades
        self.face_cascade = cv2.CascadeClassifier(cascade_dir + 'haarcascade_frontalface_default.xml')
        self.face_alt_cascade = cv2.CascadeClassifier(cascade_dir + 'haarcascade_frontalface_alt2.xml')
        self.eye_cascade = cv2.CascadeClassifier(cascade_dir + 'haarcascade_eye.xml')

    def detect(self, image: np.ndarray) -> dict:
        result = {
            'face_detected': False,
            'face_count': 0,
            'faces': []
        }
        
        if image is None or image.size == 0:
            return result

        h, w = image.shape[:2]

        if self.use_mediapipe and self.face_detection:
            try:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if len(image.shape) >= 3 else image
                results = self.face_detection.process(image_rgb)
                
                if results.detections:
                    result['face_detected'] = True
                    result['face_count'] = len(results.detections)
                    
                    for detection in results.detections:
                        bboxC = detection.location_data.relative_bounding_box
                        x = max(0, int(bboxC.xmin * w))
                        y = max(0, int(bboxC.ymin * h))
                        width = min(w - x, int(bboxC.width * w))
                        height = min(h - y, int(bboxC.height * h))
                        
                        keypoints = self.mp_face_detection.FaceKeyPoint
                        get_kp = lambda k: (
                            int(self.mp_face_detection.get_key_point(detection, k).x * w),
                            int(self.mp_face_detection.get_key_point(detection, k).y * h)
                        )
                        
                        landmarks = {}
                        try:
                            le = get_kp(keypoints.LEFT_EYE)
                            re = get_kp(keypoints.RIGHT_EYE)
                            landmarks = {
                                'left_eye': le,
                                'right_eye': re,
                                'nose': get_kp(keypoints.NOSE_TIP),
                                'mouth': get_kp(keypoints.MOUTH_CENTER)
                            }
                            # Calculate tilt angle between eyes
                            dy = re[1] - le[1]
                            dx = re[0] - le[0]
                            tilt_angle = math.degrees(math.atan2(dy, dx))
                        except Exception:
                            tilt_angle = 0.0
                            
                        face_data = {
                            'bbox': {'x': int(x), 'y': int(y), 'w': int(width), 'h': int(height)},
                            'confidence': float(detection.score[0]) if detection.score else 1.0,
                            'landmarks': landmarks,
                            'tilt_angle': float(tilt_angle)
                        }
                        result['faces'].append(face_data)
                        
                    # Sort by face box area (largest face first for scenery/long-shot photos)
                    result['faces'].sort(key=lambda f: f['bbox']['w'] * f['bbox']['h'], reverse=True)
                    return result
            except Exception as e:
                logger.warning(f"MediaPipe runtime error: {e}. Falling back to OpenCV.")
                
        # OpenCV Haar Cascade fallback with wide multi-scale detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) >= 3 else image
        
        # MinSize allows detecting distant faces in scenery photos
        min_sz = max(24, int(min(h, w) * 0.04))
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.08,
            minNeighbors=4,
            minSize=(min_sz, min_sz)
        )
        
        if len(faces) == 0 and self.face_alt_cascade:
            faces = self.face_alt_cascade.detectMultiScale(
                gray,
                scaleFactor=1.08,
                minNeighbors=4,
                minSize=(min_sz, min_sz)
            )
        
        if len(faces) > 0:
            result['face_detected'] = True
            result['face_count'] = len(faces)
            
            # Sort by area descending to prioritize main person in scenery
            faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
            
            for (x, y, width, height) in faces:
                landmarks = {}
                face_roi_gray = gray[y:y + int(height * 0.65), x:x + width]
                eyes = self.eye_cascade.detectMultiScale(face_roi_gray, scaleFactor=1.08, minNeighbors=3, minSize=(12, 12))
                
                tilt_angle = 0.0
                if len(eyes) >= 2:
                    sorted_eyes = sorted(eyes, key=lambda e: e[0])
                    ex1, ey1, ew1, eh1 = sorted_eyes[0]
                    ex2, ey2, ew2, eh2 = sorted_eyes[1]
                    le = (int(x + ex1 + ew1 // 2), int(y + ey1 + eh1 // 2))
                    re = (int(x + ex2 + ew2 // 2), int(y + ey2 + eh2 // 2))
                    landmarks['left_eye'] = le
                    landmarks['right_eye'] = re
                    landmarks['nose'] = (int(x + width // 2), int(y + int(height * 0.55)))
                    landmarks['mouth'] = (int(x + width // 2), int(y + int(height * 0.75)))
                    
                    dy = re[1] - le[1]
                    dx = re[0] - le[0]
                    if dx != 0:
                        tilt_angle = math.degrees(math.atan2(dy, dx))
                else:
                    landmarks['left_eye'] = (int(x + width * 0.35), int(y + height * 0.38))
                    landmarks['right_eye'] = (int(x + width * 0.65), int(y + height * 0.38))
                    landmarks['nose'] = (int(x + width * 0.50), int(y + height * 0.55))
                    landmarks['mouth'] = (int(x + width * 0.50), int(y + height * 0.75))

                result['faces'].append({
                    'bbox': {'x': int(x), 'y': int(y), 'w': int(width), 'h': int(height)},
                    'confidence': 0.95,
                    'landmarks': landmarks,
                    'tilt_angle': float(tilt_angle)
                })

        return result

    def detect_from_file(self, file_path: str) -> dict:
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError(f"Could not read image from {file_path}")
        return self.detect(image)

    def __del__(self):
        if self.face_detection and hasattr(self.face_detection, 'close'):
            try:
                self.face_detection.close()
            except Exception:
                pass
