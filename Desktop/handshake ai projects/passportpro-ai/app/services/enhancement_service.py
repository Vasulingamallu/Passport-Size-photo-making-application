import cv2
from app.ai.enhancement.enhancer import PhotoEnhancer

class EnhancementService:
    def __init__(self):
        self.enhancer = PhotoEnhancer()

    def enhance_photo(self, input_path: str, output_path: str, options: dict = None) -> str:
        image = cv2.imread(input_path)
        if image is None:
            raise ValueError(f"Could not read image from {input_path}")
            
        enhanced = self.enhancer.enhance(image, options)
        cv2.imwrite(output_path, enhanced)
        return output_path

    def auto_enhance(self, input_path: str, output_path: str) -> str:
        image = cv2.imread(input_path)
        if image is None:
            raise ValueError(f"Could not read image from {input_path}")
            
        enhanced = self.enhancer.auto_enhance(image)
        cv2.imwrite(output_path, enhanced)
        return output_path

    def get_enhancement_preview(self, input_path: str) -> dict:
        image = cv2.imread(input_path)
        if image is None:
            raise ValueError(f"Could not read image from {input_path}")
            
        return self.enhancer._analyze_image(image)
