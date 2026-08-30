import os
import cv2
import base64
import json
import logging
import requests
import numpy as np

logger = logging.getLogger(__name__)

class CloudAIService:
    """
    Cloud AI API Service for professional passport photo generation and analysis.
    Supports:
    - OpenAI GPT-4o Vision & Image API
    - Google Gemini 1.5 Vision API
    - Clipdrop / Stability AI APIs
    """

    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', '')
        self.clipdrop_api_key = os.getenv('CLIPDROP_API_KEY', '')
        self.stability_api_key = os.getenv('STABILITY_API_KEY', '')

    def get_configured_provider(self, custom_api_key: str = '', custom_provider: str = '') -> tuple[str, str]:
        """Determine active AI provider and key."""
        if custom_provider and custom_api_key:
            return custom_provider.lower(), custom_api_key
            
        if self.openai_api_key:
            return 'openai', self.openai_api_key
        elif self.gemini_api_key:
            return 'gemini', self.gemini_api_key
        elif self.clipdrop_api_key:
            return 'clipdrop', self.clipdrop_api_key
        elif self.stability_api_key:
            return 'stability', self.stability_api_key
        elif custom_api_key:
            if custom_api_key.startswith('sk-'):
                return 'openai', custom_api_key
            elif custom_api_key.startswith('AIza'):
                return 'gemini', custom_api_key
            else:
                return 'openai', custom_api_key
                
        return 'local', ''

    def process_with_ai_api(
        self,
        image_path: str,
        output_path: str,
        provider: str = 'auto',
        api_key: str = '',
        country_code: str = 'US',
        document_type: str = 'Passport'
    ) -> dict:
        """
        Process photo using AI Cloud API.
        """
        active_provider, key = self.get_configured_provider(api_key, provider)
        
        if active_provider == 'openai' and key:
            return self._process_openai_gpt4o(image_path, output_path, key, country_code, document_type)
        elif active_provider == 'gemini' and key:
            return self._process_gemini_vision(image_path, output_path, key, country_code, document_type)
        elif active_provider == 'clipdrop' and key:
            return self._process_clipdrop_api(image_path, output_path, key)
        else:
            return {'used_api': False, 'message': 'No cloud API key configured, using local AI engine'}

    def _process_openai_gpt4o(self, image_path: str, output_path: str, api_key: str, country_code: str, document_type: str) -> dict:
        """
        Analyze and align photo using OpenAI GPT-4o Vision API.
        """
        try:
            with open(image_path, 'rb') as img_file:
                b64_img = base64.b64encode(img_file.read()).decode('utf-8')
                
            mime_type = 'image/png' if image_path.lower().endswith('.png') else 'image/jpeg'
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            
            prompt = f"""You are a biometric passport photo compliance AI.
Analyze this photo for official {country_code} {document_type} requirements.
Return a STRICT JSON response with this exact structure:
{{
    "face_detected": true,
    "head_tilt_angle_degrees": 0.0,
    "head_center_x_percent": 50.0,
    "head_center_y_percent": 40.0,
    "head_height_percent": 65.0,
    "lighting_quality": "good",
    "shadow_imbalance": false,
    "suggested_actions": ["auto_level_eyes", "neutralize_white_balance", "solid_white_background"],
    "icao_compliant": true
}}"""

            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{b64_img}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                "response_format": {"type": "json_object"},
                "max_tokens": 500
            }
            
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=25)
            if response.status_code == 200:
                data = response.json()
                content = json.loads(data['choices'][0]['message']['content'])
                logger.info(f"OpenAI GPT-4o Vision Analysis: {content}")
                return {
                    'used_api': True,
                    'provider': 'OpenAI GPT-4o Vision',
                    'analysis': content,
                    'model': 'gpt-4o-mini'
                }
            else:
                logger.warning(f"OpenAI API error {response.status_code}: {response.text}")
                return {'used_api': False, 'error': f"OpenAI API Error ({response.status_code})"}
        except Exception as e:
            logger.warning(f"OpenAI API request failed: {e}")
            return {'used_api': False, 'error': str(e)}

    def _process_gemini_vision(self, image_path: str, output_path: str, api_key: str, country_code: str, document_type: str) -> dict:
        """
        Analyze and align photo using Google Gemini 1.5 Flash Vision API.
        """
        try:
            with open(image_path, 'rb') as img_file:
                b64_img = base64.b64encode(img_file.read()).decode('utf-8')
                
            mime_type = 'image/png' if image_path.lower().endswith('.png') else 'image/jpeg'
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            prompt = f"""Analyze this portrait photo for official {country_code} {document_type} passport compliance.
Return ONLY valid JSON with fields:
{{"face_detected": true, "head_tilt_angle_degrees": 0.0, "lighting_quality": "good", "compliance_score": 95, "recommendations": ["level_eyes", "white_backdrop"]}}"""

            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": b64_img
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "response_mime_type": "application/json"
                }
            }
            
            response = requests.post(url, json=payload, timeout=25)
            if response.status_code == 200:
                data = response.json()
                candidate = data.get('candidates', [{}])[0]
                text = candidate.get('content', {}).get('parts', [{}])[0].get('text', '{}')
                parsed = json.loads(text)
                return {
                    'used_api': True,
                    'provider': 'Google Gemini 1.5 Flash',
                    'analysis': parsed,
                    'model': 'gemini-1.5-flash'
                }
            else:
                return {'used_api': False, 'error': f"Gemini API Error ({response.status_code})"}
        except Exception as e:
            return {'used_api': False, 'error': str(e)}

    def _process_clipdrop_api(self, image_path: str, output_path: str, api_key: str) -> dict:
        """
        Remove background and isolate subject using Clipdrop API.
        """
        try:
            with open(image_path, 'rb') as f:
                r = requests.post(
                    'https://clipdrop-api.co/remove-background/v1',
                    files={'image_file': f},
                    headers={'x-api-key': api_key},
                    timeout=30
                )
            if r.status_code == 200:
                with open(output_path, 'wb') as out_f:
                    out_f.write(r.content)
                return {
                    'used_api': True,
                    'provider': 'Clipdrop API',
                    'output_path': output_path
                }
            else:
                return {'used_api': False, 'error': f"Clipdrop API Error ({r.status_code})"}
        except Exception as e:
            return {'used_api': False, 'error': str(e)}
