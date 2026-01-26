"""Тестовый скрипт с отладкой для проверки логики."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from facecrop.core import FaceCropper
from PIL import Image
import numpy as np
import cv2

def debug_crop(image_path):
    """Отладочная функция для проверки логики."""
    image = Image.open(image_path)
    img_w, img_h = image.size
    
    print(f"Исходное изображение: {img_w}x{img_h}")
    
    # Конвертируем в numpy для детекции
    img_array = np.array(image)
    if len(img_array.shape) == 2:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
    elif img_array.shape[2] == 4:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
    else:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    cropper = FaceCropper()
    face_bbox = cropper.detect_face(img_array)
    
    if face_bbox is None:
        print("Лицо не найдено!")
        return
    
    face_x, face_y, face_w, face_h = face_bbox
    face_center_x = face_x + face_w // 2
    face_center_y = face_y + face_h // 2
    
    print(f"\nЛицо найдено:")
    print(f"  bbox: {face_bbox}")
    print(f"  center: ({face_center_x}, {face_center_y})")
    
    # Вычисляем кроп
    crop_x, crop_y, crop_width, crop_height = cropper.calculate_orientation_crop(
        face_bbox, (img_w, img_h), k=2.5, safety_margin=0.15
    )
    
    print(f"\nПервый кроп:")
    print(f"  размер: {crop_width}x{crop_height}")
    print(f"  позиция: ({crop_x}, {crop_y})")
    
    # Вычисляем позицию лица в кропе
    face_x_in_crop = (face_center_x - crop_x) / crop_width
    face_y_in_crop = (face_center_y - crop_y) / crop_height
    
    print(f"\nПозиция лица в кропе (относительно):")
    print(f"  x={face_x_in_crop:.3f}, y={face_y_in_crop:.3f}")
    
    # Проверяем ресайз
    target_size = 1024
    if crop_height > crop_width:
        scale = target_size / crop_width
        new_width = target_size
        new_height = int(crop_height * scale)
    else:
        scale = target_size / crop_height
        new_width = int(crop_width * scale)
        new_height = target_size
    
    print(f"\nПосле ресайза:")
    print(f"  scale={scale:.3f}")
    print(f"  размер: {new_width}x{new_height}")
    
    if new_width != new_height:
        if new_height > new_width:
            top = int(face_y_in_crop * (new_height - target_size))
            print(f"\nФинальный кроп (вертикальное):")
            print(f"  top={top}")
            print(f"  face_y после ресайза: {face_y_in_crop * new_height:.1f}px")
            print(f"  желаемая позиция лица: {face_y_in_crop * target_size:.1f}px")
            print(f"  top должен быть: {face_y_in_crop * (new_height - target_size):.1f}")
        else:
            left = int(face_x_in_crop * (new_width - target_size))
            print(f"\nФинальный кроп (горизонтальное):")
            print(f"  left={left}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        debug_crop(sys.argv[1])
    else:
        print("Использование: python test_debug_crop.py <путь_к_изображению>")
