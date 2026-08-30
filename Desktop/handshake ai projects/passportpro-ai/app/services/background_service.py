import cv2
from app.ai.background_removal.remover import BackgroundRemover

class BackgroundService:
    def __init__(self):
        self.remover = BackgroundRemover()

    def remove_and_replace(self, input_path: str, output_path: str, bg_color: str = '#FFFFFF') -> str:
        image = cv2.imread(input_path)
        if image is None:
            raise ValueError(f"Could not read image from {input_path}")
            
        rgba_image = self.remover.remove_background(image)
        final_image = self.remover.replace_background(rgba_image, color=bg_color)
        
        cv2.imwrite(output_path, final_image)
        return output_path

    def remove_background(self, input_path: str, output_path: str) -> str:
        return self.remover.remove_background_file(input_path, output_path)

    def change_background(self, input_path: str, output_path: str, color: str) -> str:
        image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError(f"Could not read image from {input_path}")
            
        if image.shape[2] != 4:
            raise ValueError("Input image does not have an alpha channel")
            
        final_image = self.remover.replace_background(image, color=color)
        cv2.imwrite(output_path, final_image)
        return output_path
