import numpy as np
import cv2
import logging

logger = logging.getLogger(__name__)

try:
    from rembg import remove
    HAS_REMBG = True
except ImportError:
    HAS_REMBG = False
    logger.warning("rembg not installed, background removal will fallback to original image.")

class BackgroundRemover:
    def __init__(self, model_name='u2net'):
        self.model_name = model_name

    def remove_background(self, image: np.ndarray) -> np.ndarray:
        if not HAS_REMBG:
            logger.warning("rembg missing, returning original image.")
            # return as RGBA
            if image.shape[2] == 3:
                return cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
            return image
            
        # rembg expects and returns images in RGB/RGBA usually, we'll convert appropriately
        # But rembg works well with PIL or raw bytes. For numpy arrays, it usually handles RGB.
        try:
            # We'll use the numpy array directly
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            result = remove(image_rgb)
            # convert back to BGRA for OpenCV consistency
            return cv2.cvtColor(result, cv2.COLOR_RGBA2BGRA)
        except Exception as e:
            logger.error(f"Error removing background: {str(e)}")
            if image.shape[2] == 3:
                return cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
            return image

    def remove_background_file(self, input_path: str, output_path: str) -> str:
        image = cv2.imread(input_path)
        if image is None:
            raise ValueError(f"Could not read image from {input_path}")
            
        result_rgba = self.remove_background(image)
        cv2.imwrite(output_path, result_rgba)
        return output_path

    def replace_background(self, image_rgba: np.ndarray, color: str = '#FFFFFF') -> np.ndarray:
        if image_rgba.shape[2] != 4:
            return image_rgba # not RGBA
            
        r, g, b = self._hex_to_rgb(color)
        
        alpha_channel = image_rgba[:, :, 3]
        smoothed_alpha = self._smooth_edges(alpha_channel) / 255.0
        
        bgr = image_rgba[:, :, :3]
        
        bg_image = np.zeros_like(bgr, dtype=np.float32)
        bg_image[:] = [b, g, r] # OpenCV uses BGR
        
        foreground = bgr.astype(np.float32)
        
        # Blend
        alpha_factor = smoothed_alpha[:, :, np.newaxis]
        blended = foreground * alpha_factor + bg_image * (1.0 - alpha_factor)
        
        return blended.astype(np.uint8)

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return (255, 255, 255)
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _smooth_edges(self, alpha_channel: np.ndarray) -> np.ndarray:
        return cv2.GaussianBlur(alpha_channel, (3, 3), 0)
