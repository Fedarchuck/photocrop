"""Скрипт для проверки и исправления проблем с MediaPipe."""

import sys
import subprocess

print("="*60)
print("Проверка и исправление MediaPipe")
print("="*60)

# Проверка текущей установки
print("\n1. Проверка текущей версии MediaPipe...")
try:
    import mediapipe as mp
    print(f"   ✓ MediaPipe установлен")
    
    # Проверка версии
    try:
        version = mp.__version__
        print(f"   ✓ Версия: {version}")
    except:
        print(f"   ⚠ Версия не определена")
    
    # Проверка наличия solutions
    if hasattr(mp, 'solutions'):
        print(f"   ✓ Атрибут 'solutions' доступен")
        if hasattr(mp.solutions, 'face_detection'):
            print(f"   ✓ face_detection доступен")
        else:
            print(f"   ❌ face_detection НЕ доступен")
            print(f"   → Требуется переустановка")
    else:
        print(f"   ❌ Атрибут 'solutions' НЕ доступен")
        print(f"   → Требуется переустановка")
        
except ImportError:
    print(f"   ❌ MediaPipe НЕ установлен")
    print(f"   → Требуется установка")

# Предложение исправления
print("\n2. Исправление проблемы...")
print("   Выполняется переустановка MediaPipe...")

try:
    # Удаление старой версии
    print("   → Удаление старой версии...")
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "mediapipe"])
    
    # Установка новой версии (используем доступную версию)
    print("   → Установка MediaPipe (последняя доступная версия)...")
    # Пробуем установить последнюю версию
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mediapipe"])
    except:
        # Если не получилось, пробуем конкретную версию
        print("   → Попытка установить mediapipe==0.10.30...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mediapipe==0.10.30"])
    
    print("   ✓ MediaPipe переустановлен")
    
except subprocess.CalledProcessError as e:
    print(f"   ❌ Ошибка при переустановке: {e}")
    print("\n   Попробуйте вручную:")
    print("   pip uninstall mediapipe")
    print("   pip install mediapipe==0.10.0")
    sys.exit(1)

# Финальная проверка
print("\n3. Финальная проверка...")
try:
    import mediapipe as mp
    if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'face_detection'):
        print("   ✓ MediaPipe работает корректно!")
        print("\n" + "="*60)
        print("Готово! Теперь перезапустите Web UI.")
        print("="*60)
    else:
        print("   ❌ Проблема сохраняется")
        print("   Попробуйте другую версию:")
        print("   pip install mediapipe==0.10.9")
except Exception as e:
    print(f"   ❌ Ошибка: {e}")

