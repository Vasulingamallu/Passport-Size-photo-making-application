import os
import cv2
import json
import logging
from app.extensions import db
from app.models.country import CountryRequirement
from app.services.face_service import FaceService
from app.services.background_service import BackgroundService
from app.services.enhancement_service import EnhancementService
from app.services.passport_service import PassportService
from app.services.print_service import PrintService
from app.services.cloud_ai_service import CloudAIService
from app.utils.image_utils import load_image, save_image, straighten_face

logger = logging.getLogger(__name__)

class AIStudioService:
    def __init__(self):
        self.face_service = FaceService()
        self.bg_service = BackgroundService()
        self.enh_service = EnhancementService()
        self.passport_service = PassportService()
        self.print_service = PrintService()
        self.cloud_ai_service = CloudAIService()

    def process_one_click(
        self,
        input_image_path: str,
        output_dir: str,
        file_prefix: str,
        country_code: str = 'US',
        document_type: str = 'Passport',
        bg_color: str = '#FFFFFF',
        sheet_size: str = '4x6',
        photo_count: int = 8,
        cutting_guides: bool = True,
        custom_w: float = 35.0,
        custom_h: float = 45.0,
        custom_dpi: int = 300,
        ai_provider: str = 'none',
        api_key: str = '',
        apply_enhancement: bool = False,
        remove_bg: bool = True
    ) -> dict:
        """
        Execute direct passport photo and print sheet generation:
        - By default, applies NO AI enhancements (preserving 100% natural colors, skin tones, and original pixels).
        - Direct geometric head alignment and precision passport proportion cropping.
        - Evenly tiles 8 photos onto 4x6 photo paper with cutting guides.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Load source image
        raw_image = load_image(input_image_path)
        current_image_path = input_image_path
        
        # Step 0: Cloud AI API (optional, only if explicitly requested)
        cloud_api_result = {'used_api': False}
        if ai_provider not in ('none', 'local', '') and (api_key or os.getenv('OPENAI_API_KEY') or os.getenv('GEMINI_API_KEY') or os.getenv('CLIPDROP_API_KEY')):
            try:
                cloud_api_result = self.cloud_ai_service.process_with_ai_api(
                    image_path=input_image_path,
                    output_path=os.path.join(output_dir, f"{file_prefix}_cloud_bg.png"),
                    provider=ai_provider,
                    api_key=api_key,
                    country_code=country_code,
                    document_type=document_type
                )
                if cloud_api_result.get('used_api') and cloud_api_result.get('output_path'):
                    current_image_path = cloud_api_result['output_path']
            except Exception as e:
                logger.warning(f"Cloud AI API exception: {e}")

        # Step 1: Detect Face Coordinates
        face_data = {'x': 0, 'y': 0, 'width': 0, 'height': 0}
        face_info = {}
        try:
            face_result = self.face_service.detect_and_analyze(current_image_path)
            faces = face_result.get('detection', {}).get('faces', [])
            if faces:
                face_info = faces[0]
                bbox = face_info.get('bbox', {})
                face_data = {
                    'x': bbox.get('x', 0),
                    'y': bbox.get('y', 0),
                    'width': bbox.get('w', bbox.get('width', 0)),
                    'height': bbox.get('h', bbox.get('height', 0))
                }
        except Exception as e:
            logger.warning(f"Face detection: {e}")

        # Step 2: Auto-Straighten Tilted Head / Selfie Posture (if tilted)
        if face_info and raw_image is not None:
            try:
                straightened_img, updated_face_info = straighten_face(raw_image, face_info)
                if updated_face_info.get('tilt_angle', 0.0) == 0.0:
                    straightened_path = os.path.join(output_dir, f"{file_prefix}_straightened.jpg")
                    save_image(straightened_img, straightened_path)
                    current_image_path = straightened_path
                    bbox = updated_face_info.get('bbox', {})
                    face_data = {
                        'x': bbox.get('x', 0),
                        'y': bbox.get('y', 0),
                        'width': bbox.get('w', bbox.get('width', 0)),
                        'height': bbox.get('h', bbox.get('height', 0))
                    }
            except Exception as e:
                logger.warning(f"Auto-straightening fallback: {e}")

        # Step 3: Background Removal (Only if requested and not "keep_original")
        active_image_path = current_image_path
        if remove_bg and bg_color.lower() != 'keep_original':
            bg_removed_path = os.path.join(output_dir, f"{file_prefix}_bg.png")
            try:
                self.bg_service.remove_and_replace(current_image_path, bg_removed_path, bg_color)
                active_image_path = bg_removed_path
            except Exception as e:
                logger.warning(f"Background removal fallback: {e}")
                active_image_path = current_image_path

        # Step 4: AI Enhancement (DISABLED BY DEFAULT to keep natural photo)
        if apply_enhancement:
            enhanced_path = os.path.join(output_dir, f"{file_prefix}_enh.png")
            try:
                self.enh_service.auto_enhance(active_image_path, enhanced_path)
                active_image_path = enhanced_path
            except Exception as e:
                logger.warning(f"Enhancement fallback: {e}")

        # Step 5: Pure Geometric Passport Crop & Sizing (Preserves natural pixels)
        passport_output_path = os.path.join(output_dir, f"passport_{file_prefix}.jpg")
        dimension_label = ""
        
        if country_code == 'CUSTOM' or not country_code:
            self.passport_service.generate_custom_size(
                active_image_path, face_data, custom_w, custom_h, custom_dpi, passport_output_path
            )
            dimension_label = f"{custom_w} × {custom_h} mm ({custom_dpi} DPI)"
        else:
            # Lookup country requirement
            req = db.session.query(CountryRequirement).filter_by(
                country_code=country_code, document_type=document_type
            ).first()
            
            if not req:
                req = db.session.query(CountryRequirement).filter_by(country_code=country_code).first()
                
            if req:
                self.passport_service.generate_passport_photo(
                    active_image_path, face_data, req.country_code, req.document_type, passport_output_path
                )
                dimension_label = f"{req.country_name} {req.document_type} ({req.width_mm} × {req.height_mm} mm)"
            else:
                self.passport_service.generate_custom_size(
                    active_image_path, face_data, 35.0, 45.0, 300, passport_output_path
                )
                dimension_label = "Standard 35 × 45 mm"

        # Step 6: Generate Print Sheet (JPG + PDF)
        sheet_jpg_path = os.path.join(output_dir, f"printsheet_{file_prefix}.jpg")
        sheet_pdf_path = os.path.join(output_dir, f"printsheet_{file_prefix}.pdf")
        
        self.print_service.generate_print_sheet(
            passport_output_path, sheet_size, photo_count, sheet_jpg_path, cutting_guides
        )
        
        self.print_service.generate_pdf_sheet(
            passport_output_path, sheet_size, photo_count, sheet_pdf_path, cutting_guides
        )

        return {
            'passport_jpg_path': passport_output_path,
            'sheet_jpg_path': sheet_jpg_path,
            'sheet_pdf_path': sheet_pdf_path,
            'dimension_label': dimension_label,
            'sheet_info': f"{photo_count} photos on {sheet_size} paper",
            'face_detected': bool(face_data.get('width', 0) > 0),
            'cloud_ai': cloud_api_result
        }
