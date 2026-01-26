"""Тесты для core функций."""

import unittest
import numpy as np
from PIL import Image

from src.facecrop.core import FaceCropper


class TestFaceCropper(unittest.TestCase):
    """Тесты для FaceCropper."""
    
    def setUp(self):
        """Инициализация перед каждым тестом."""
        self.cropper = FaceCropper()
    
    def test_calculate_square_crop_centered(self):
        """Тест расчета квадратного кропа для лица в центре."""
        # Лицо 100x100 в центре изображения 500x500
        face_bbox = (200, 200, 100, 100)
        image_size = (500, 500)
        k = 2.5
        safety_margin = 0.15
        
        crop_x, crop_y, side = self.cropper.calculate_square_crop(
            face_bbox, image_size, k, safety_margin
        )
        
        # Проверяем, что квадрат внутри границ
        self.assertGreaterEqual(crop_x, 0)
        self.assertGreaterEqual(crop_y, 0)
        self.assertLessEqual(crop_x + side, image_size[0])
        self.assertLessEqual(crop_y + side, image_size[1])
        
        # Проверяем, что квадрат содержит лицо
        face_center_x = face_bbox[0] + face_bbox[2] // 2
        face_center_y = face_bbox[1] + face_bbox[3] // 2
        self.assertGreaterEqual(face_center_x, crop_x)
        self.assertLessEqual(face_center_x, crop_x + side)
        self.assertGreaterEqual(face_center_y, crop_y)
        self.assertLessEqual(face_center_y, crop_y + side)
    
    def test_calculate_square_crop_near_edge(self):
        """Тест расчета кропа для лица у края изображения."""
        # Лицо в левом верхнем углу
        face_bbox = (10, 10, 100, 100)
        image_size = (500, 500)
        k = 2.5
        
        crop_x, crop_y, side = self.cropper.calculate_square_crop(
            face_bbox, image_size, k
        )
        
        # Проверяем границы
        self.assertGreaterEqual(crop_x, 0)
        self.assertGreaterEqual(crop_y, 0)
        self.assertLessEqual(crop_x + side, image_size[0])
        self.assertLessEqual(crop_y + side, image_size[1])
    
    def test_calculate_square_crop_small_image(self):
        """Тест для случая, когда изображение меньше квадрата."""
        face_bbox = (50, 50, 100, 100)
        image_size = (200, 200)  # Маленькое изображение
        k = 2.5
        
        crop_x, crop_y, side = self.cropper.calculate_square_crop(
            face_bbox, image_size, k
        )
        
        # Квадрат должен быть не больше изображения
        self.assertLessEqual(side, image_size[0])
        self.assertLessEqual(side, image_size[1])
        self.assertGreaterEqual(crop_x, 0)
        self.assertGreaterEqual(crop_y, 0)
        self.assertLessEqual(crop_x + side, image_size[0])
        self.assertLessEqual(crop_y + side, image_size[1])
    
    def test_center_crop(self):
        """Тест центрального кропа (fallback)."""
        # Создаем тестовое изображение
        image = Image.new('RGB', (800, 600), color='red')
        target_size = 512
        
        cropped = self.cropper._center_crop(image, target_size)
        
        self.assertEqual(cropped.size, (target_size, target_size))
    
    def test_fix_orientation(self):
        """Тест исправления ориентации."""
        image = Image.new('RGB', (100, 200), color='blue')
        # Просто проверяем, что функция не падает
        result = self.cropper._fix_orientation(image)
        self.assertIsNotNone(result)
    
    def test_get_average_color(self):
        """Тест вычисления среднего цвета."""
        # Красное изображение
        image = Image.new('RGB', (100, 100), color=(255, 0, 0))
        avg_color = self.cropper._get_average_color(image)
        self.assertEqual(avg_color, (255, 0, 0))
        
        # Серое изображение
        image = Image.new('RGB', (100, 100), color=(128, 128, 128))
        avg_color = self.cropper._get_average_color(image)
        self.assertEqual(avg_color, (128, 128, 128))


if __name__ == '__main__':
    unittest.main()

