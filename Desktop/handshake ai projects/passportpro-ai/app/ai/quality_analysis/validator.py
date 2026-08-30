import numpy as np
import cv2

class QualityValidator:
    def validate(self, image: np.ndarray, face_data: dict = None, analysis_data: dict = None) -> dict:
        checks = []
        total_score = 0
        suggestions = []
        
        fd_check = self._check_face_detection(face_data)
        checks.append(fd_check)
        total_score += int(fd_check['score'])
        if not fd_check['passed']: suggestions.append("Ensure a single face is clearly visible.")
        
        fp_check = self._check_face_position(analysis_data)
        checks.append(fp_check)
        total_score += int(fp_check['score'])
        if not fp_check['passed']: suggestions.append("Center your face and ensure it occupies 60-80% of the image height.")
        
        bg_check = self._check_background(image)
        checks.append(bg_check)
        total_score += int(bg_check['score'])
        if not bg_check['passed']: suggestions.append("Use a plain white or light-colored background.")
        
        iq_check = self._check_image_quality(image, analysis_data)
        checks.append(iq_check)
        total_score += int(iq_check['score'])
        if not iq_check['passed']: suggestions.append("Ensure the photo is well-lit and not blurry.")
        
        fv_check = self._check_face_visibility(face_data, analysis_data)
        checks.append(fv_check)
        total_score += int(fv_check['score'])
        if not fv_check['passed']: suggestions.append("Look straight at the camera with both eyes visible.")
        
        status = self._get_status(int(total_score))
        
        return {
            'total_score': int(total_score),
            'status': status,
            'checks': checks,
            'suggestions': suggestions
        }

    def _check_face_detection(self, face_data) -> dict:
        score = 0
        passed = False
        message = "No face detected."
        
        if face_data and face_data.get('face_detected'):
            count = face_data.get('face_count', 0)
            if count == 1:
                score = 20
                passed = True
                message = "Single face detected."
            elif count > 1:
                score = 5
                passed = False
                message = "Multiple faces detected."
                
        return {'name': 'Face Detection', 'score': int(score), 'max_score': 20, 'passed': bool(passed), 'message': message}

    def _check_face_position(self, analysis_data) -> dict:
        score = 0
        message = "Face position not optimal."
        
        if analysis_data:
            if analysis_data.get('is_centered'):
                score += 10
            
            ratio = float(analysis_data.get('head_size_ratio', 0))
            if 0.5 <= ratio <= 0.85:
                score += 10
                
            if score == 20:
                message = "Face is perfectly centered and sized."
        
        return {'name': 'Face Position', 'score': int(score), 'max_score': 20, 'passed': bool(score >= 15), 'message': message}

    def _check_background(self, image) -> dict:
        is_uniform, std_dev = self._analyze_background_uniformity(image)
        score = 20 if is_uniform else max(0, int(20 - (std_dev - 10)))
        return {'name': 'Background', 'score': int(min(20, score)), 'max_score': 20, 'passed': bool(is_uniform), 'message': "Background is uniform." if is_uniform else "Background is cluttered or uneven."}

    def _check_image_quality(self, image, analysis_data) -> dict:
        score = 20
        h, w = image.shape[:2]
        if min(h, w) < 400:
            score -= 10
            
        if analysis_data and analysis_data.get('is_blurry'):
            score -= 10
            
        passed = bool(score >= 15)
        return {'name': 'Image Quality', 'score': int(score), 'max_score': 20, 'passed': passed, 'message': "Good quality." if passed else "Low resolution or blurry."}

    def _check_face_visibility(self, face_data, analysis_data) -> dict:
        score = 0
        if analysis_data:
            if analysis_data.get('eyes_visible'):
                score += 10
            if analysis_data.get('is_front_facing'):
                score += 10
                
        passed = bool(score == 20)
        return {'name': 'Face Visibility', 'score': int(score), 'max_score': 20, 'passed': passed, 'message': "Face fully visible and front-facing." if passed else "Face not fully visible."}

    def _get_status(self, score: int) -> str:
        if score >= 90: return 'Excellent'
        if score >= 75: return 'Acceptable'
        if score >= 50: return 'Needs Improvement'
        return 'Rejected'

    def _analyze_background_uniformity(self, image) -> tuple[bool, float]:
        h, w = image.shape[:2]
        corners = [
            image[0:int(h*0.1), 0:int(w*0.1)],
            image[0:int(h*0.1), int(w*0.9):w],
            image[int(h*0.9):h, 0:int(w*0.1)],
            image[int(h*0.9):h, int(w*0.9):w]
        ]
        
        std_devs = [float(np.std(c)) for c in corners if c.size > 0]
        if not std_devs:
            return False, 100.0
            
        avg_std_dev = float(sum(std_devs) / len(std_devs))
        return bool(avg_std_dev < 15), avg_std_dev
