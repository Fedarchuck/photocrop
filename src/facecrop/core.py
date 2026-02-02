"""Core функции для детекции лица и расчета квадратного кропа."""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional, List
from pathlib import Path
import sys


class FaceCropper:
    """Класс для детекции лица и расчета квадратного кропа."""
    
    def __init__(self):
        """Инициализация детектора лиц (OpenCV Haar Cascades)."""
        self.face_cascade = self._load_haar_cascade()

    def _load_haar_cascade(self) -> cv2.CascadeClassifier:
        """Ищет и загружает Haar каскад из возможных путей."""
        filenames = [
            "haarcascade_frontalface_default.xml",
            "haarcascade_frontalface_alt.xml",
        ]

        candidates = []
        # Стандартный путь OpenCV
        if hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades"):
            candidates.append(Path(cv2.data.haarcascades))

        # PyInstaller onefile: файлы могут лежать в _MEIPASS
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(Path(meipass) / "cv2" / "data" / "haarcascades")
            candidates.append(Path(meipass) / "haarcascades")

        for base in candidates:
            for name in filenames:
                path = base / name
                if path.exists():
                    cascade = cv2.CascadeClassifier(str(path))
                    if not cascade.empty():
                        return cascade

        # Пустой классификатор, чтобы не падать при detectMultiScale
        return cv2.CascadeClassifier()
    
    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Детектирует лицо на изображении с помощью OpenCV Haar Cascades.
        
        Args:
            image: Изображение в формате BGR (OpenCV)
            
        Returns:
            Tuple (x, y, width, height) bounding box лица или None
        """
        if self.face_cascade is None or self.face_cascade.empty():
            return None
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        if len(faces) > 0:
            # Берем самое большое лицо
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, width, height = face
            return (x, y, width, height)
        return None
    
    def calculate_orientation_crop(
        self,
        face_bbox: Tuple[int, int, int, int],
        image_size: Tuple[int, int],
        k: float = 2.5,
        safety_margin: float = 0.15
    ) -> Tuple[int, int, int, int]:
        """
        Рассчитывает параметры кропа с учетом ориентации изображения.
        Для вертикальных - кроп по высоте (сохраняет ширину)
        Для горизонтальных - кроп по ширине (сохраняет высоту)
        
        Args:
            face_bbox: (x, y, width, height) лица
            image_size: (width, height) исходного изображения
            k: Множитель размера лица
            safety_margin: Дополнительный запас в долях (0.15 = 15%)
            
        Returns:
            Tuple (x, y, width, height) - координаты и размеры кропа
        """
        x, y, face_w, face_h = face_bbox
        img_w, img_h = image_size
        
        # Центр лица
        face_center_x = x + face_w // 2
        face_center_y = y + face_h // 2
        
        # Определяем ориентацию изображения
        is_vertical = img_h > img_w  # Вертикальное (портрет)
        is_horizontal = img_w > img_h  # Горизонтальное (ландшафт)
        
        # Минимальный размер кропа на основе лица (для гарантии, что лицо поместится)
        face_max_dim = max(face_w, face_h)
        min_crop_size = int(face_max_dim * k * (1 + safety_margin))
        
        if is_vertical:
            # Вертикальное изображение: кроп по высоте, сохраняем всю ширину
            crop_width = img_w  # Сохраняем всю ширину
            
            # Для вертикального фото делаем кроп высотой БОЛЬШЕ ширины
            # Это гарантирует, что после ресайза будет финальный кроп с сохранением позиции лица
            # Высота должна быть достаточной для лица с запасом
            margin_needed = int(face_max_dim * k * safety_margin)
            
            # Минимальная высота = ширина (квадрат) или размер для лица с запасом
            min_needed_height = max(img_w, min_crop_size)
            
            # Делаем кроп выше квадрата, чтобы был финальный кроп
            # Используем примерно 1.5 * ширина, но не больше высоты изображения
            crop_height = min(int(img_w * 1.5), img_h)
            # Но не меньше минимальной требуемой высоты
            crop_height = max(crop_height, min_needed_height)
            # И не больше высоты изображения
            crop_height = min(crop_height, img_h)
            
            # Центрируем по горизонтали (всегда 0, так как берем всю ширину)
            crop_x = 0
            
            # Позиционируем по вертикали: центр кропа на центре лица
            crop_y = face_center_y - crop_height // 2
            
            # Корректируем границы, чтобы не выйти за пределы изображения
            if crop_y < 0:
                # Лицо слишком высоко - начинаем с верха
                crop_y = 0
            if crop_y + crop_height > img_h:
                # Лицо слишком низко - заканчиваем внизу
                crop_y = img_h - crop_height
                
        elif is_horizontal:
            # Горизонтальное изображение: кроп ТОЛЬКО по ширине, сохраняем ВСЮ высоту
            crop_height = img_h  # Сохраняем всю высоту
            
            # Используем максимально возможную ширину для квадрата (ширина = высота)
            # Но не больше исходной ширины изображения
            crop_width = min(img_h, img_w)  # Максимально квадрат, но не больше изображения
            
            # Убеждаемся, что ширина достаточна для лица (но не меньше минимальной)
            if crop_width < min_crop_size:
                crop_width = min(min_crop_size, img_w)
            
            # Центрируем по вертикали (всегда 0, так как берем всю высоту)
            crop_y = 0
            # Центрируем по горизонтали относительно лица
            crop_x = face_center_x - crop_width // 2
            
            # Корректируем, если выходит за границы
            if crop_x < 0:
                crop_x = 0
            if crop_x + crop_width > img_w:
                crop_x = img_w - crop_width
        else:
            # Квадратное изображение: делаем квадратный кроп
            crop_size = min(img_w, img_h)
            crop_width = crop_size
            crop_height = crop_size
            
            crop_x = face_center_x - crop_size // 2
            crop_y = face_center_y - crop_size // 2
            
            # Корректируем границы
            if crop_x < 0:
                crop_x = 0
            if crop_y < 0:
                crop_y = 0
            if crop_x + crop_size > img_w:
                crop_x = img_w - crop_size
            if crop_y + crop_size > img_h:
                crop_y = img_h - crop_size
        
        # Финальная проверка границ (но не перезаписываем позицию, если она уже правильная)
        # Гарантируем, что кроп не выходит за границы изображения
        crop_x = max(0, min(crop_x, img_w - crop_width))
        crop_y = max(0, min(crop_y, img_h - crop_height))
        # Корректируем размеры, если нужно (но они должны быть уже правильными)
        crop_width = min(crop_width, img_w - crop_x)
        crop_height = min(crop_height, img_h - crop_y)
        
        # Гарантируем минимальный размер
        crop_width = max(1, crop_width)
        crop_height = max(1, crop_height)
        
        return (crop_x, crop_y, crop_width, crop_height)
    
    def crop_to_square_with_face(
        self,
        image: Image.Image,
        target_size: int = 1024,
        k: float = 2.5,
        safety_margin: float = 0.15,
        padding: str = "none"
    ) -> Image.Image:
        """
        Кропает изображение с сохранением лица и ориентации.
        Для вертикальных - кроп по высоте (сохраняет ширину)
        Для горизонтальных - кроп по ширине (сохраняет высоту)
        
        Args:
            image: PIL Image
            target_size: Целевой размер для ресайза (используется только если нужно)
            k: Множитель размера лица
            safety_margin: Запас для гарантии полного лица
            padding: Тип padding если нужно ("blur", "mirror", "solid", "none")
            
        Returns:
            PIL Image с сохраненной ориентацией
        """
        # Учитываем EXIF ориентацию
        image = self._fix_orientation(image)
        
        # Конвертируем в numpy для детекции
        img_array = np.array(image)
        if len(img_array.shape) == 2:  # Grayscale
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2BGR)
        elif img_array.shape[2] == 4:  # RGBA
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        else:  # RGB
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Детектируем лицо
        face_bbox = self.detect_face(img_array)
        
        if face_bbox is None:
            # Fallback: центральный кроп с сохранением ориентации
            return self._center_crop_orientation(image, target_size)
        
        # Рассчитываем кроп с учетом ориентации
        img_w, img_h = image.size
        
        # Центр лица в исходном изображении
        face_center_x = face_bbox[0] + face_bbox[2] // 2
        face_center_y = face_bbox[1] + face_bbox[3] // 2
        
        crop_x, crop_y, crop_width, crop_height = self.calculate_orientation_crop(
            face_bbox, (img_w, img_h), k, safety_margin
        )
        
        # Выполняем кроп
        cropped = image.crop((crop_x, crop_y, crop_x + crop_width, crop_y + crop_height))
        
        # Вычисляем позицию лица в ОТНОСИТЕЛЬНЫХ координатах кропа (0.0 - 1.0)
        # Это нужно для сохранения позиции лица после ресайза
        face_x_in_crop = (face_center_x - crop_x) / crop_width
        face_y_in_crop = (face_center_y - crop_y) / crop_height
        
        # Всегда ресайз до квадрата target_size x target_size
        # Определяем ориентацию кропа для правильного масштабирования
        if crop_width > crop_height:
            # Горизонтальный кроп: масштабируем по высоте до target_size
            scale = target_size / crop_height
            new_width = int(crop_width * scale)
            new_height = target_size
        elif crop_height > crop_width:
            # Вертикальный кроп: масштабируем по ширине до target_size
            scale = target_size / crop_width
            new_width = target_size
            new_height = int(crop_height * scale)
        else:
            # Квадратный кроп
            new_width = target_size
            new_height = target_size
        
        # Ресайз до промежуточного размера
        cropped = cropped.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Если нужно, обрезаем до точного квадрата, сохраняя позицию лица
        if new_width != new_height:
            if new_width > new_height:
                # Обрезаем по ширине (горизонтальное) - сохраняем X позицию лица
                # Чтобы сохранить относительную позицию лица: top + face_x_in_crop * target_size = face_x_in_crop * new_width
                # Отсюда: left = face_x_in_crop * (new_width - target_size)
                left = int(face_x_in_crop * (new_width - target_size))
                
                # Корректируем, если выходит за границы (но стараемся сохранить позицию лица)
                left = max(0, min(left, new_width - target_size))
                cropped = cropped.crop((left, 0, left + target_size, target_size))
            else:
                # Обрезаем по высоте (вертикальное) - сохраняем Y позицию лица
                # После ресайза лицо находится на позиции: face_y_in_crop * new_height от верха (абсолютные координаты)
                # В финальном квадрате хотим, чтобы лицо было на позиции: face_y_in_crop * target_size от верха
                # Чтобы сохранить позицию лица: top + (face_y_in_crop * target_size) = face_y_in_crop * new_height
                # Отсюда: top = face_y_in_crop * new_height - face_y_in_crop * target_size = face_y_in_crop * (new_height - target_size)
                # Это правильно! Если лицо на 20% от верха кропа, после ресайза оно на 20% от верха ресайзнутого изображения
                # И в квадрате оно должно быть на 20% от верха: top + 20%*target_size = 20%*new_height
                top = int(face_y_in_crop * (new_height - target_size))
                
                # Корректируем границы, стараясь сохранить позицию лица
                top = max(0, min(top, new_height - target_size))
                cropped = cropped.crop((0, top, target_size, top + target_size))
        
        return cropped
    
    def _fix_orientation(self, image: Image.Image) -> Image.Image:
        """Исправляет ориентацию изображения на основе EXIF."""
        try:
            exif = image._getexif()
            if exif is not None:
                orientation = exif.get(274)  # EXIF tag for orientation
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
        except (AttributeError, KeyError, TypeError):
            pass
        return image
    
    def _center_crop(self, image: Image.Image, target_size: int) -> Image.Image:
        """Центральный кроп до квадрата (fallback)."""
        width, height = image.size
        size = min(width, height)
        left = (width - size) // 2
        top = (height - size) // 2
        cropped = image.crop((left, top, left + size, top + size))
        return cropped.resize((target_size, target_size), Image.Resampling.LANCZOS)
    
    def _center_crop_orientation(self, image: Image.Image, target_size: int) -> Image.Image:
        """Центральный кроп с сохранением ориентации, всегда квадрат (fallback)."""
        width, height = image.size
        
        if height > width:
            # Вертикальное: кроп по высоте, сохраняем ширину
            crop_height = min(width * 1.5, height)
            crop_width = width
            left = 0
            top = (height - int(crop_height)) // 2
            cropped = image.crop((left, top, left + crop_width, top + int(crop_height)))
            # Масштабируем по ширине до target_size
            scale = target_size / crop_width
            new_width = target_size
            new_height = int(crop_height * scale)
        elif width > height:
            # Горизонтальное: кроп по ширине, сохраняем высоту
            crop_width = min(height * 1.5, width)
            crop_height = height
            left = (width - int(crop_width)) // 2
            top = 0
            cropped = image.crop((left, top, left + int(crop_width), top + crop_height))
            # Масштабируем по высоте до target_size
            scale = target_size / crop_height
            new_height = target_size
            new_width = int(crop_width * scale)
        else:
            # Квадратное
            cropped = image
            new_width = target_size
            new_height = target_size
        
        # Ресайз до промежуточного размера
        cropped = cropped.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Обрезаем до точного квадрата если нужно
        if new_width != new_height:
            if new_width > new_height:
                # Обрезаем по ширине
                left = (new_width - target_size) // 2
                cropped = cropped.crop((left, 0, left + target_size, target_size))
            else:
                # Обрезаем по высоте
                top = (new_height - target_size) // 2
                cropped = cropped.crop((0, top, target_size, top + target_size))
        
        return cropped
    
    def _add_padding(
        self,
        image: Image.Image,
        target_size: int,
        padding_type: str,
        original_image: Image.Image
    ) -> Image.Image:
        """Добавляет padding к изображению."""
        if padding_type == "solid":
            # Однотонный (средний цвет)
            avg_color = self._get_average_color(image)
            result = Image.new(image.mode, (target_size, target_size), avg_color)
        elif padding_type == "blur":
            # Размытие краев
            result = self._blur_padding(image, target_size, original_image)
        elif padding_type == "mirror":
            # Зеркальное отражение
            result = self._mirror_padding(image, target_size)
        else:
            # Просто черный/белый фон
            bg_color = (255, 255, 255) if image.mode == 'RGB' else 255
            result = Image.new(image.mode, (target_size, target_size), bg_color)
        
        # Вставляем изображение по центру
        paste_x = (target_size - image.size[0]) // 2
        paste_y = (target_size - image.size[1]) // 2
        result.paste(image, (paste_x, paste_y))
        return result
    
    def _get_average_color(self, image: Image.Image) -> Tuple[int, ...]:
        """Вычисляет средний цвет изображения."""
        img_array = np.array(image)
        if len(img_array.shape) == 3:
            return tuple(map(int, img_array.mean(axis=(0, 1))))
        else:
            return (int(img_array.mean()),)
    
    def _blur_padding(
        self,
        image: Image.Image,
        target_size: int,
        original_image: Image.Image
    ) -> Image.Image:
        """Добавляет размытый padding."""
        # Увеличиваем оригинал и размываем
        scale = target_size / max(image.size)
        enlarged = original_image.resize(
            (int(original_image.size[0] * scale), int(original_image.size[1] * scale)),
            Image.Resampling.LANCZOS
        )
        
        # Кропаем до target_size
        width, height = enlarged.size
        left = (width - target_size) // 2
        top = (height - target_size) // 2
        blurred = enlarged.crop((left, top, left + target_size, top + target_size))
        
        # Применяем размытие
        blurred_array = np.array(blurred)
        blurred_array = cv2.GaussianBlur(blurred_array, (51, 51), 0)
        return Image.fromarray(blurred_array)
    
    def _mirror_padding(self, image: Image.Image, target_size: int) -> Image.Image:
        """Добавляет зеркальный padding."""
        width, height = image.size
        result = Image.new(image.mode, (target_size, target_size))
        
        # Копируем изображение в центр
        paste_x = (target_size - width) // 2
        paste_y = (target_size - height) // 2
        result.paste(image, (paste_x, paste_y))
        
        # Зеркалим края
        if paste_x > 0:
            left_edge = image.crop((0, 0, min(10, width), height))
            left_edge = left_edge.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
            for x in range(0, paste_x, left_edge.size[0]):
                result.paste(left_edge, (x, paste_y))
        
        if paste_y > 0:
            top_edge = image.crop((0, 0, width, min(10, height)))
            top_edge = top_edge.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
            for y in range(0, paste_y, top_edge.size[1]):
                result.paste(top_edge, (paste_x, y))
        
        return result

