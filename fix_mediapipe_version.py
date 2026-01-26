"""Установка совместимой версии MediaPipe."""

import sys
import subprocess

print("="*60)
print("Установка совместимой версии MediaPipe")
print("="*60)
print("\nMediaPipe 0.10.31 использует новый Tasks API, который требует файлы моделей.")
print("Для FaceCrop лучше использовать версию 0.10.30 с старым Solutions API.\n")

try:
    print("1. Удаление текущей версии MediaPipe...")
    subprocess.check_call([sys.executable, "-m", "pip", "uninstall", "-y", "mediapipe"])
    print("   ✓ Удалено\n")
    
    print("2. Установка MediaPipe 0.10.30...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mediapipe==0.10.30"])
    print("   ✓ Установлено\n")
    
    print("3. Проверка установки...")
    import mediapipe as mp
    if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'face_detection'):
        print("   ✓ MediaPipe 0.10.30 работает корректно!")
        print("   ✓ Solutions API доступен")
        print("\n" + "="*60)
        print("Готово! Теперь перезапустите Web UI.")
        print("="*60)
    else:
        print("   ⚠ Solutions API все еще недоступен")
        print("   Попробуйте: pip install mediapipe==0.10.9")
        
except subprocess.CalledProcessError as e:
    print(f"\n❌ Ошибка: {e}")
    print("\nПопробуйте вручную:")
    print("pip uninstall mediapipe")
    print("pip install mediapipe==0.10.30")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

