from app.extensions import db
from app.models.country import CountryRequirement
from app.utils.image_utils import load_image, save_image, mm_to_pixels, auto_crop_face, set_image_dpi
import os
import numpy as np
import cv2

class PassportService:
    def generate_passport_photo(self, image_path: str, face_data: dict, country_code: str, document_type: str, output_path: str) -> str:
        req = db.session.query(CountryRequirement).filter_by(country_code=country_code, document_type=document_type).first()
        if not req:
            raise ValueError("Country requirements not found")
        
        image = load_image(image_path)
        width_px = mm_to_pixels(req.width_mm, req.dpi if hasattr(req, 'dpi') and req.dpi else 300)
        height_px = mm_to_pixels(req.height_mm, req.dpi if hasattr(req, 'dpi') and req.dpi else 300)
        
        head_min = (req.head_size_min / 100.0) if (hasattr(req, 'head_size_min') and req.head_size_min) else 0.5
        head_max = (req.head_size_max / 100.0) if (hasattr(req, 'head_size_max') and req.head_size_max) else 0.8
        
        target_head_ratio = (head_min + head_max) / 2
        
        processed = self._apply_requirements(image, face_data, width_px, height_px, head_min, head_max)
        
        save_image(processed, output_path)
        set_image_dpi(output_path, req.dpi if hasattr(req, 'dpi') and req.dpi else 300)
        
        return output_path

    def generate_custom_size(self, image_path: str, face_data: dict, width_mm: float, height_mm: float, dpi: int, output_path: str) -> str:
        image = load_image(image_path)
        width_px = mm_to_pixels(width_mm, dpi)
        height_px = mm_to_pixels(height_mm, dpi)
        
        target_head_ratio = 0.7
        
        processed = auto_crop_face(image, face_data, width_px, height_px, target_head_ratio)
        
        save_image(processed, output_path)
        set_image_dpi(output_path, dpi)
        
        return output_path

    def get_country_requirements(self, country_code: str, document_type: str = None) -> list[dict]:
        query = db.session.query(CountryRequirement).filter_by(country_code=country_code)
        if document_type:
            query = query.filter_by(document_type=document_type)
        return [req.to_dict() if hasattr(req, 'to_dict') else {'id': req.id, 'country_code': req.country_code, 'document_type': req.document_type} for req in query.all()]

    def get_all_countries(self) -> list[dict]:
        countries = db.session.query(CountryRequirement).all()
        result = {}
        for req in countries:
            if req.country_code not in result:
                result[req.country_code] = {'code': req.country_code, 'name': getattr(req, 'country_name', req.country_code), 'documents': []}
            if req.document_type not in result[req.country_code]['documents']:
                result[req.country_code]['documents'].append(req.document_type)
        return sorted(list(result.values()), key=lambda x: x['name'])

    def _apply_requirements(self, image: np.ndarray, face_data: dict, width_px: int, height_px: int, head_min: float, head_max: float) -> np.ndarray:
        target_head_ratio = (head_min + head_max) / 2
        return auto_crop_face(image, face_data, width_px, height_px, target_head_ratio)
