"""Тестовый скрипт для проверки запуска UI."""

import sys
from pathlib import Path

print("Проверка зависимостей...")

# Проверка Python версии
print(f"Python версия: {sys.version}")

# Проверка импортов
try:
    import gradio as gr
    print(f"✓ Gradio установлен: {gr.__version__}")
except ImportError as e:
    print(f"❌ Gradio не установлен: {e}")
    print("Установите: pip install gradio")
    sys.exit(1)

try:
    import mediapipe as mp
    print(f"✓ MediaPipe установлен")
except ImportError as e:
    print(f"❌ MediaPipe не установлен: {e}")
    print("Установите: pip install mediapipe")
    sys.exit(1)

try:
    from PIL import Image
    print(f"✓ Pillow установлен")
except ImportError as e:
    print(f"❌ Pillow не установлен: {e}")
    print("Установите: pip install Pillow")
    sys.exit(1)

try:
    import cv2
    print(f"✓ OpenCV установлен: {cv2.__version__}")
except ImportError as e:
    print(f"❌ OpenCV не установлен: {e}")
    print("Установите: pip install opencv-python")
    sys.exit(1)

# Проверка импорта модуля
print("\nПроверка импорта модуля facecrop...")
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from facecrop.ui import launch_ui
    print("✓ Модуль facecrop импортирован успешно")
except Exception as e:
    print(f"❌ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("Все проверки пройдены! Запуск UI...")
print("="*60 + "\n")

try:
    launch_ui(server_name="127.0.0.1", server_port=7860)
except KeyboardInterrupt:
    print("\n\nСервер остановлен пользователем.")
except Exception as e:
    print(f"\n❌ Ошибка при запуске: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

