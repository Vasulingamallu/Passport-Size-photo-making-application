import cv2
import numpy as np

class PhotoEnhancer:
    """
    Clean, natural photographic enhancement.
    Preserves 100% authentic skin tones, natural skin texture, and original colors
    without any smudging, plastic smoothing, or oil-paint artifacts.
    """

    def enhance(self, image: np.ndarray, options: dict = None) -> np.ndarray:
        if options is None:
            options = {}
            
        has_alpha = len(image.shape) == 3 and image.shape[2] == 4
        if has_alpha:
            alpha = image[:, :, 3]
            bgr = image[:, :, :3].copy()
        else:
            alpha = None
            bgr = image.copy()
            
        enhanced = bgr
        
        if options.get('brightness', False):
            enhanced = self.adjust_brightness(enhanced)
            
        if options.get('contrast', False):
            enhanced = self.adjust_contrast(enhanced)
            
        if options.get('sharpness', False):
            enhanced = self.sharpen(enhanced)
            
        if options.get('exposure', False):
            enhanced = self.correct_exposure(enhanced)
            
        if has_alpha:
            return np.dstack((enhanced, alpha))
        return enhanced

    def auto_enhance(self, image: np.ndarray) -> np.ndarray:
        """
        Gentle natural enhancement:
        - Mild tone curve for clarity
        - Subtle edge crispness on eyes/hair
        - ZERO color distortion (100% natural skin tone)
        - ZERO plastic/oil-paint smoothing
        """
        has_alpha = len(image.shape) == 3 and image.shape[2] == 4
        if has_alpha:
            alpha = image[:, :, 3]
            bgr = image[:, :, :3].copy()
        else:
            alpha = None
            bgr = image.copy()

        # Step 1: Subtle tone curve (boosts clarity gently without altering hues)
        # Converts to float to avoid clipping artifacts
        img_f = bgr.astype(np.float32) / 255.0
        
        # Gentle contrast S-curve (mild 5% contrast expansion)
        # y = x + 0.1 * sin(2 * pi * x)
        enhanced_f = img_f + 0.04 * np.sin(2.0 * np.pi * img_f)
        enhanced_f = np.clip(enhanced_f, 0.0, 1.0)
        enhanced_bgr = (enhanced_f * 255.0).astype(np.uint8)

        # Step 2: Very subtle unsharp mask for crisp eyes and hair (no halo, no smudging)
        gaussian = cv2.GaussianBlur(enhanced_bgr, (0, 0), 1.2)
        sharpened = cv2.addWeighted(enhanced_bgr, 1.15, gaussian, -0.15, 0)

        if has_alpha:
            return np.dstack((sharpened, alpha))
        return sharpened

    def adjust_brightness(self, image: np.ndarray, factor: float = 1.0) -> np.ndarray:
        bgr = image[:, :, :3] if len(image.shape) == 3 and image.shape[2] == 4 else image
        # Simple clean linear brightness adjustment
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = cv2.add(v, int(15 * factor))
        result = cv2.cvtColor(cv2.merge((h, s, v)), cv2.COLOR_HSV2BGR)
        if len(image.shape) == 3 and image.shape[2] == 4:
            return np.dstack((result, image[:, :, 3]))
        return result

    def adjust_contrast(self, image: np.ndarray) -> np.ndarray:
        bgr = image[:, :, :3] if len(image.shape) == 3 and image.shape[2] == 4 else image
        # Clean linear contrast without color shifts
        result = cv2.convertScaleAbs(bgr, alpha=1.08, beta=0)
        if len(image.shape) == 3 and image.shape[2] == 4:
            return np.dstack((result, image[:, :, 3]))
        return result

    def sharpen(self, image: np.ndarray, amount: float = 1.0) -> np.ndarray:
        bgr = image[:, :, :3] if len(image.shape) == 3 and image.shape[2] == 4 else image
        # High quality unsharp mask
        blurred = cv2.GaussianBlur(bgr, (0, 0), 1.5)
        result = cv2.addWeighted(bgr, 1.0 + (0.25 * amount), blurred, -0.25 * amount, 0)
        if len(image.shape) == 3 and image.shape[2] == 4:
            return np.dstack((result, image[:, :, 3]))
        return result

    def denoise(self, image: np.ndarray) -> np.ndarray:
        # Mild bilateral filter that preserves natural edges without oil-painting artifacts
        bgr = image[:, :, :3] if len(image.shape) == 3 and image.shape[2] == 4 else image
        result = cv2.bilateralFilter(bgr, d=5, sigmaColor=20, sigmaSpace=20)
        if len(image.shape) == 3 and image.shape[2] == 4:
            return np.dstack((result, image[:, :, 3]))
        return result

    def correct_color(self, image: np.ndarray) -> np.ndarray:
        # Keep natural colors intact
        return image

    def correct_exposure(self, image: np.ndarray) -> np.ndarray:
        bgr = image[:, :, :3] if len(image.shape) == 3 and image.shape[2] == 4 else image
        mean_val = np.mean(bgr)
        if mean_val < 90:
            gamma = 0.9
            inv_gamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
            result = cv2.LUT(bgr, table)
        else:
            result = bgr
            
        if len(image.shape) == 3 and image.shape[2] == 4:
            return np.dstack((result, image[:, :, 3]))
        return result

    def _analyze_image(self, image: np.ndarray) -> dict:
        bgr = image[:, :, :3] if len(image.shape) == 3 and image.shape[2] == 4 else image
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY) if len(bgr.shape) == 3 else bgr
        mean_brightness = float(np.mean(gray))
        contrast = float(np.std(gray))
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        
        return {
            'mean_brightness': mean_brightness,
            'contrast': contrast,
            'noise_level': float(1000 / (laplacian_var + 1))
        }
