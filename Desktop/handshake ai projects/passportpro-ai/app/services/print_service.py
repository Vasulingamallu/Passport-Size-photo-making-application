from fpdf import FPDF
from app.utils.image_utils import load_image, save_image, mm_to_pixels, inches_to_pixels
import cv2
import numpy as np
import os

class PrintService:
    def generate_print_sheet(self, photo_path: str, sheet_size: str, photo_count: int, output_path: str, cutting_guides: bool = True) -> str:
        dpi = 300
        sheet_w, sheet_h = self._get_sheet_dimensions(sheet_size, photo_count, dpi)
        raw_photo = load_image(photo_path)
        if raw_photo is None:
            raise ValueError(f"Could not load photo from {photo_path}")
            
        # If photo is 4-channel BGRA, blend onto white BGR
        if len(raw_photo.shape) == 3 and raw_photo.shape[2] == 4:
            bgr = raw_photo[:, :, :3]
            alpha = raw_photo[:, :, 3] / 255.0
            bg = np.ones_like(bgr, dtype=np.float32) * 255
            fg = bgr.astype(np.float32)
            alpha_f = alpha[:, :, np.newaxis]
            photo = (fg * alpha_f + bg * (1.0 - alpha_f)).astype(np.uint8)
        else:
            photo = raw_photo
            
        img_h, img_w = photo.shape[:2]
        aspect = img_w / img_h if img_h > 0 else (35.0 / 45.0)
        
        rows, cols = self._calculate_grid(sheet_size, photo_count)
        
        # Calculate available cell area with uniform spacing
        gap_px = mm_to_pixels(2.0, dpi) # 2mm cutting space between photos
        
        avail_w_per_col = (sheet_w - (cols + 1) * gap_px) / cols
        avail_h_per_row = (sheet_h - (rows + 1) * gap_px) / rows
        
        # Determine passport tile dimensions preserving aspect ratio
        if avail_w_per_col / avail_h_per_row > aspect:
            tile_h = int(avail_h_per_row)
            tile_w = int(tile_h * aspect)
        else:
            tile_w = int(avail_w_per_col)
            tile_h = int(tile_w / aspect)
            
        pw = max(10, tile_w)
        ph = max(10, tile_h)
        
        photo_tile = cv2.resize(photo, (pw, ph), interpolation=cv2.INTER_AREA)
        canvas = np.ones((sheet_h, sheet_w, 3), dtype=np.uint8) * 255
        
        total_grid_w = cols * pw + (cols - 1) * gap_px
        total_grid_h = rows * ph + (rows - 1) * gap_px
        
        # Evenly center the entire grid onto the sheet
        start_x = max(0, int((sheet_w - total_grid_w) / 2))
        start_y = max(0, int((sheet_h - total_grid_h) / 2))
        
        for r in range(rows):
            for c in range(cols):
                idx = r * cols + c
                if idx >= photo_count:
                    break
                
                x = start_x + c * (pw + gap_px)
                y = start_y + r * (ph + gap_px)
                
                if x + pw <= sheet_w and y + ph <= sheet_h:
                    canvas[y:y+ph, x:x+pw] = photo_tile
                    
                    if cutting_guides:
                        # Draw thin light-grey cutting guide rectangle
                        cv2.rectangle(canvas, (x, y), (x + pw, y + ph), (180, 180, 180), 1, cv2.LINE_AA)
        
        save_image(canvas, output_path)
        from app.utils.image_utils import set_image_dpi
        set_image_dpi(output_path, dpi)
        return output_path

    def generate_pdf_sheet(self, photo_path: str, sheet_size: str, photo_count: int, output_path: str, cutting_guides: bool = True) -> str:
        temp_jpg = output_path + '.temp.jpg'
        self.generate_print_sheet(photo_path, sheet_size, photo_count, temp_jpg, cutting_guides)
        
        if sheet_size == '4x6':
            # 6x4 inches landscape: 152.4mm x 101.6mm
            pdf = FPDF(orientation='L', unit='mm', format=(101.6, 152.4))
            pdf.add_page()
            pdf.image(temp_jpg, x=0, y=0, w=152.4, h=101.6)
        else:
            # A4: 210mm x 297mm
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.add_page()
            pdf.image(temp_jpg, x=0, y=0, w=210, h=297)
            
        pdf.output(output_path)
        if os.path.exists(temp_jpg):
            try:
                os.remove(temp_jpg)
            except Exception:
                pass
        return output_path

    def _get_sheet_dimensions(self, sheet_size: str, photo_count: int = 6, dpi: int = 300) -> tuple[int, int]:
        if sheet_size == '4x6':
            # Standard 4x6 photo paper is 6 inches wide x 4 inches high in photo printers
            return inches_to_pixels(6, dpi), inches_to_pixels(4, dpi)
        elif sheet_size == 'A4':
            return mm_to_pixels(210, dpi), mm_to_pixels(297, dpi)
        else:
            return mm_to_pixels(210, dpi), mm_to_pixels(297, dpi)

    def _calculate_grid(self, sheet_size: str, photo_count: int) -> tuple[int, int]:
        if sheet_size == '4x6':
            if photo_count <= 4:
                return 2, 2
            elif photo_count <= 6:
                return 2, 3   # 2 rows x 3 cols = 6 photos
            elif photo_count <= 8:
                return 2, 4   # 2 rows x 4 cols = 8 photos (fills 4x6 evenly)
            elif photo_count <= 12:
                return 3, 4   # 3 rows x 4 cols = 12 photos
            else:
                return 3, 4
        else:  # A4
            if photo_count <= 4:
                return 2, 2
            elif photo_count <= 6:
                return 2, 3
            elif photo_count <= 8:
                return 4, 2
            elif photo_count <= 12:
                return 4, 3
            elif photo_count <= 16:
                return 4, 4
            else:
                cols = int(np.ceil(np.sqrt(photo_count)))
                rows = int(np.ceil(photo_count / cols))
                return rows, cols
