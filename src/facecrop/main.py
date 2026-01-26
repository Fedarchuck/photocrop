"""CLI интерфейс для FaceCrop."""

import argparse
import sys
import os
from pathlib import Path
from PIL import Image
from typing import List
import cv2
import numpy as np

from .core import FaceCropper


def get_image_files(path: Path, recursive: bool = False) -> List[Path]:
    """Получает список изображений из пути."""
    extensions = {'.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG', '.WEBP'}
    
    if path.is_file():
        if path.suffix.lower() in extensions:
            return [path]
        return []
    
    if path.is_dir():
        files = []
        pattern = '**/*' if recursive else '*'
        for ext in extensions:
            files.extend(path.glob(f'{pattern}{ext}'))
        return sorted(files)
    
    return []


def process_image(
    input_path: Path,
    output_path: Path,
    cropper: FaceCropper,
    target_size: int,
    k: float,
    padding: str,
    dry_run: bool,
    visualize: bool
) -> bool:
    """Обрабатывает одно изображение."""
    try:
        # Загружаем изображение
        image = Image.open(input_path)
        
        if dry_run:
            print(f"[DRY RUN] Обработка: {input_path.name}")
            return True
        
        # Кропаем
        cropped = cropper.crop_to_square_with_face(
            image, target_size=target_size, k=k, padding=padding
        )
        
        # Сохраняем
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Определяем формат
        output_format = 'JPEG'
        if output_path.suffix.lower() in ['.png', '.PNG']:
            output_format = 'PNG'
        elif output_path.suffix.lower() in ['.webp', '.WEBP']:
            output_format = 'WEBP'
        
        if output_format == 'JPEG':
            cropped = cropped.convert('RGB')
            cropped.save(output_path, output_format, quality=95)
        else:
            cropped.save(output_path, output_format)
        
        if visualize:
            # Создаем визуализацию с рамками
            vis_path = output_path.parent / f"{output_path.stem}_vis{output_path.suffix}"
            create_visualization(input_path, vis_path, cropper, target_size, k)
        
        return True
        
    except Exception as e:
        print(f"Ошибка при обработке {input_path.name}: {e}", file=sys.stderr)
        return False


def create_visualization(
    input_path: Path,
    output_path: Path,
    cropper: FaceCropper,
    target_size: int,
    k: float
):
    """Создает визуализацию с рамками лица и кропа."""
    image = Image.open(input_path)
    image = cropper._fix_orientation(image)
    
    img_array = np.array(image)
    if len(img_array.shape) == 2:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
    elif img_array.shape[2] == 4:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
    else:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    
    # Детектируем лицо
    face_bbox = cropper.detect_face(img_array)
    
    if face_bbox:
        x, y, w, h = face_bbox
        # Рисуем рамку лица (зеленая)
        cv2.rectangle(img_array, (x, y), (x + w, y + h), (0, 255, 0), 3)
        
        # Рисуем рамку кропа (красная)
        img_w, img_h = image.size
        crop_x, crop_y, crop_width, crop_height = cropper.calculate_orientation_crop(
            face_bbox, (img_w, img_h), k
        )
        cv2.rectangle(
            img_array,
            (crop_x, crop_y),
            (crop_x + crop_width, crop_y + crop_height),
            (0, 0, 255),
            3
        )
    
    # Конвертируем обратно в RGB для сохранения
    vis_image = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
    vis_pil = Image.fromarray(vis_image)
    vis_pil.save(output_path)


def main():
    """Главная функция CLI."""
    parser = argparse.ArgumentParser(
        description='Автоматический кроп фотографий до квадрата с сохранением лица'
    )
    parser.add_argument(
        '--ui',
        action='store_true',
        help='Запустить Web UI вместо CLI'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=7860,
        help='Порт для Web UI (по умолчанию 7860)'
    )
    parser.add_argument(
        '--input', '-i',
        type=str,
        required=False,
        help='Входной файл или папка'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        required=False,
        help='Выходная папка'
    )
    parser.add_argument(
        '--size',
        type=int,
        default=1024,
        help='Размер квадрата (по умолчанию 1024)'
    )
    parser.add_argument(
        '--k',
        type=float,
        default=2.5,
        help='Множитель размера лица для квадрата (по умолчанию 2.5)'
    )
    parser.add_argument(
        '--padding',
        type=str,
        choices=['none', 'blur', 'mirror', 'solid'],
        default='none',
        help='Тип padding если нужно (none/blur/mirror/solid)'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Рекурсивная обработка папок'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Только расчет без сохранения'
    )
    parser.add_argument(
        '--visualize', '-v',
        action='store_true',
        help='Сохранить визуализацию с рамками'
    )
    
    args = parser.parse_args()
    
    # Если запрошен UI - запускаем его
    if args.ui:
        from .ui import launch_ui
        try:
            launch_ui(server_port=args.port)
        except KeyboardInterrupt:
            print("\n\nСервер остановлен.")
        return
    
    # Проверяем обязательные параметры для CLI
    if not args.input or not args.output:
        parser.error("--input и --output обязательны для CLI режима (или используйте --ui)")
    
    # Проверяем входной путь
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Ошибка: путь {input_path} не существует", file=sys.stderr)
        sys.exit(1)
    
    # Получаем список файлов
    image_files = get_image_files(input_path, args.recursive)
    if not image_files:
        print(f"Ошибка: не найдено изображений в {input_path}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Найдено изображений: {len(image_files)}")
    
    # Создаем cropper
    cropper = FaceCropper()
    
    # Обрабатываем файлы
    output_dir = Path(args.output)
    success_count = 0
    
    for i, input_file in enumerate(image_files, 1):
        # Формируем имя выходного файла
        relative_path = input_file.relative_to(input_path) if input_path.is_dir() else input_file.name
        output_file = output_dir / relative_path
        output_file = output_file.parent / f"{output_file.stem}_square{output_file.suffix}"
        
        print(f"[{i}/{len(image_files)}] Обработка: {input_file.name}")
        
        if process_image(
            input_file, output_file, cropper,
            args.size, args.k, args.padding,
            args.dry_run, args.visualize
        ):
            success_count += 1
    
    print(f"\nГотово! Успешно обработано: {success_count}/{len(image_files)}")


if __name__ == '__main__':
    main()

