import cv2
import numpy as np
import math
from PIL import Image

def mm_to_pixels(mm: float, dpi: int = 300) -> int:
    return int((mm / 25.4) * dpi)

def inches_to_pixels(inches: float, dpi: int = 300) -> int:
    return int(inches * dpi)

def pixels_to_mm(pixels: int, dpi: int = 300) -> float:
    return (pixels / dpi) * 25.4

def resize_with_aspect(image: np.ndarray, target_w: int, target_h: int) -> np.ndarray:
    h, w = image.shape[:2]
    if h == 0 or w == 0:
        return np.ones((target_h, target_w, 3), dtype=np.uint8) * 255

    aspect_image = w / h
    aspect_target = target_w / target_h

    if aspect_image > aspect_target:
        new_w = target_w
        new_h = max(1, int(target_w / aspect_image))
    else:
        new_h = target_h
        new_w = max(1, int(target_h * aspect_image))

    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA if (new_w < w or new_h < h) else cv2.INTER_CUBIC)
    
    num_channels = image.shape[2] if len(image.shape) == 3 else 3
    canvas = np.ones((target_h, target_w, num_channels), dtype=np.uint8) * 255
    y_offset = max(0, (target_h - new_h) // 2)
    x_offset = max(0, (target_w - new_w) // 2)
    
    actual_h = min(new_h, target_h - y_offset)
    actual_w = min(new_w, target_w - x_offset)
    
    canvas[y_offset:y_offset+actual_h, x_offset:x_offset+actual_w] = resized[:actual_h, :actual_w]
    return canvas

def straighten_face(image: np.ndarray, face_info: dict) -> tuple[np.ndarray, dict]:
    """
    Auto-correct selfie or tilted head pose:
    Rotates the image around the eyes so that the eyes and head are perfectly level (0 degree tilt).
    """
    if image is None or not face_info:
        return image, face_info

    h, w = image.shape[:2]
    landmarks = face_info.get('landmarks', {})
    bbox = face_info.get('bbox', {})
    tilt_angle = face_info.get('tilt_angle', 0.0)

    # Compute tilt angle from eyes if available
    le = landmarks.get('left_eye')
    re = landmarks.get('right_eye')
    
    if le and re:
        dy = re[1] - le[1]
        dx = re[0] - le[0]
        if dx != 0:
            tilt_angle = math.degrees(math.atan2(dy, dx))
        center_pt = (float((le[0] + re[0]) / 2.0), float((le[1] + re[1]) / 2.0))
    elif bbox:
        center_pt = (float(bbox.get('x', 0) + bbox.get('w', bbox.get('width', 0)) / 2.0),
                     float(bbox.get('y', 0) + bbox.get('h', bbox.get('height', 0)) / 2.0))
    else:
        return image, face_info

    # Only rotate if tilt is noticeable (> 0.5 degrees) and realistic (< 45 degrees)
    if abs(tilt_angle) < 0.5 or abs(tilt_angle) > 45.0:
        return image, face_info

    # Rotation matrix (rotate in opposite direction of tilt to level eyes)
    M = cv2.getRotationMatrix2D(center_pt, tilt_angle, 1.0)
    
    # Apply affine rotation with border replication
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    # Transform bbox coordinates
    new_bbox = dict(bbox)
    if bbox:
        bx = bbox.get('x', 0)
        by = bbox.get('y', 0)
        bw = bbox.get('w', bbox.get('width', 0))
        bh = bbox.get('h', bbox.get('height', 0))
        
        corners = np.array([
            [bx, by],
            [bx + bw, by],
            [bx, by + bh],
            [bx + bw, by + bh]
        ], dtype=np.float32)
        
        # Transform corners
        rotated_corners = cv2.transform(np.array([corners]), M)[0]
        min_x = max(0, int(np.min(rotated_corners[:, 0])))
        min_y = max(0, int(np.min(rotated_corners[:, 1])))
        max_x = min(w, int(np.max(rotated_corners[:, 0])))
        max_y = min(h, int(np.max(rotated_corners[:, 1])))
        
        new_bbox = {
            'x': min_x,
            'y': min_y,
            'w': max(10, max_x - min_x),
            'h': max(10, max_y - min_y),
            'width': max(10, max_x - min_x),
            'height': max(10, max_y - min_y)
        }

    updated_face_info = dict(face_info)
    updated_face_info['bbox'] = new_bbox
    updated_face_info['tilt_angle'] = 0.0

    return rotated, updated_face_info

def auto_crop_face(image: np.ndarray, face_bbox: dict, target_w: int, target_h: int, head_ratio: float = 0.62) -> np.ndarray:
    """
    Precision ICAO/Passport framing matching professional studio standard:
    - Crown of head (top of hair) has ~9% headroom from top edge.
    - Full head height (crown to chin) is ~60-65% of total photo height.
    - Chin sits at ~70% from top edge, leaving bottom 30% for neck, collar, and shoulders.
    - Horizontally centered.
    """
    h, w = image.shape[:2]
    face_x = float(face_bbox.get('x', 0))
    face_y = float(face_bbox.get('y', 0))
    face_w = float(face_bbox.get('width', face_bbox.get('w', 0)))
    face_h = float(face_bbox.get('height', face_bbox.get('h', 0)))
    
    crop_aspect = target_w / target_h
    
    if face_h <= 0 or face_w <= 0:
        # Fallback: center upper-body crop
        img_aspect = w / h
        if img_aspect > crop_aspect:
            crop_h = h
            crop_w = int(h * crop_aspect)
        else:
            crop_w = w
            crop_h = int(w / crop_aspect)
        x1 = max(0, (w - crop_w) // 2)
        y1 = max(0, int(h * 0.05))
        if y1 + crop_h > h:
            y1 = max(0, h - crop_h)
        x2 = min(w, x1 + crop_w)
        y2 = min(h, y1 + crop_h)
        cropped = image[y1:y2, x1:x2]
        return resize_with_aspect(cropped, target_w, target_h)
        
    face_center_x = face_x + face_w / 2.0
    
    # Anatomical estimation:
    # Face detector returns eyebrows-to-chin region.
    # Top of hair/crown is approx 0.35 * face_h above top of detected face box.
    # Bottom of chin is at face_y + face_h.
    crown_y = face_y - 0.35 * face_h
    chin_y = face_y + face_h
    head_height = max(1.0, chin_y - crown_y) # ~1.35 * face_h
    
    # Ideal proportion: head is ~62% of photo height
    target_prop = 0.62
    crop_h = int(head_height / target_prop)
    crop_w = int(crop_h * crop_aspect)
    
    # Headroom above crown is ~9% of total photo height
    headroom = int(crop_h * 0.09)
    y1 = int(crown_y - headroom)
    y2 = y1 + crop_h
    
    x1 = int(face_center_x - crop_w / 2.0)
    x2 = x1 + crop_w
    
    # Check if padding is needed outside image boundaries
    pad_top = max(0, -y1)
    pad_bottom = max(0, y2 - h)
    pad_left = max(0, -x1)
    pad_right = max(0, x2 - w)
    
    if pad_top > 0 or pad_bottom > 0 or pad_left > 0 or pad_right > 0:
        bg_val = (255, 255, 255, 255) if len(image.shape) == 3 and image.shape[2] == 4 else (255, 255, 255)
        padded_img = cv2.copyMakeBorder(
            image, pad_top, pad_bottom, pad_left, pad_right,
            cv2.BORDER_CONSTANT, value=bg_val
        )
        x1 += pad_left
        x2 += pad_left
        y1 += pad_top
        y2 += pad_top
        cropped = padded_img[y1:y2, x1:x2]
    else:
        cropped = image[y1:y2, x1:x2]
        
    if cropped.size == 0 or cropped.shape[0] == 0 or cropped.shape[1] == 0:
        cropped = image
        
    return resize_with_aspect(cropped, target_w, target_h)

def set_image_dpi(image_path: str, dpi: int = 300) -> None:
    img = Image.open(image_path)
    img.save(image_path, dpi=(dpi, dpi))

def get_image_dimensions(image_path: str) -> tuple[int, int]:
    img = Image.open(image_path)
    return img.size

def load_image(path: str) -> np.ndarray:
    return cv2.imread(path, cv2.IMREAD_UNCHANGED)

def save_image(image: np.ndarray, path: str, quality: int = 95) -> str:
    if path.lower().endswith('.jpg') or path.lower().endswith('.jpeg'):
        if len(image.shape) == 3 and image.shape[2] == 4:
            bgr = image[:, :, :3]
            alpha = image[:, :, 3] / 255.0
            bg = np.ones_like(bgr, dtype=np.float32) * 255
            fg = bgr.astype(np.float32)
            alpha_f = alpha[:, :, np.newaxis]
            blended = (fg * alpha_f + bg * (1.0 - alpha_f)).astype(np.uint8)
            cv2.imwrite(path, blended, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        else:
            cv2.imwrite(path, image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    else:
        cv2.imwrite(path, image)
    return path
