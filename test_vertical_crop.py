"""Тестовый скрипт для диагностики проблем с вертикальными фото."""

import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / "src"))

from facecrop.core import FaceCropper
from PIL import Image

def test_vertical_crop(image_path):
    """Тестирует обрезку вертикального фото с детальным выводом."""
    print(f"\nТестирование: {image_path}")
    print("=" * 60)
    
    # Загружаем изображение
    image = Image.open(image_path)
    img_w, img_h = image.size
    print(f"Исходное изображение: {img_w}x{img_h} ({'вертикальное' if img_h > img_w else 'горизонтальное' if img_w > img_h else 'квадратное'})")
    
    # Создаем cropper
    cropper = FaceCropper()
    
    # Обрабатываем
    try:
        cropped = cropper.crop_to_square_with_face(
            image, 
            target_size=1024,
            k=2.5,
            safety_margin=0.15
        )
        print(f"\nРезультат: {cropped.size[0]}x{cropped.size[1]}")
        print("✓ Обработка завершена")
        
        # Сохраняем результат для визуальной проверки
        output_path = Path(image_path).parent / f"{Path(image_path).stem}_test_result.jpg"
        cropped.convert('RGB').save(output_path, 'JPEG', quality=95)
        print(f"Сохранено: {output_path}")
        
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_vertical_crop(sys.argv[1])
    else:
        print("Использование: python test_vertical_crop.py <путь_к_изображению>")
        print("\nПример:")
        print("  python test_vertical_crop.py photo.jpg")
