"""Диагностика способов импорта MediaPipe."""

print("="*60)
print("Диагностика MediaPipe")
print("="*60)

try:
    import mediapipe as mp
    print(f"\n✓ MediaPipe установлен")
    
    # Проверка версии
    try:
        version = mp.__version__
        print(f"✓ Версия: {version}")
    except:
        print(f"⚠ Версия не определена")
    
    # Проверка структуры модуля
    print("\nПроверка структуры модуля:")
    print(f"  dir(mp) содержит: {[x for x in dir(mp) if not x.startswith('_')][:10]}")
    
    # Проверка разных способов доступа
    print("\nПроверка способов доступа к face_detection:")
    
    # Способ 1: mp.solutions.face_detection
    try:
        fd1 = mp.solutions.face_detection
        print("  ✓ mp.solutions.face_detection - РАБОТАЕТ")
        print(f"    Тип: {type(fd1)}")
    except AttributeError as e:
        print(f"  ❌ mp.solutions.face_detection - НЕ РАБОТАЕТ: {e}")
    
    # Способ 2: mp.solutions
    try:
        solutions = mp.solutions
        print("  ✓ mp.solutions - РАБОТАЕТ")
        print(f"    Тип: {type(solutions)}")
        print(f"    dir(solutions): {[x for x in dir(solutions) if not x.startswith('_')][:10]}")
    except AttributeError as e:
        print(f"  ❌ mp.solutions - НЕ РАБОТАЕТ: {e}")
    
    # Способ 3: Прямой импорт
    try:
        from mediapipe.python.solutions import face_detection
        print("  ✓ from mediapipe.python.solutions import face_detection - РАБОТАЕТ")
    except ImportError as e:
        print(f"  ❌ from mediapipe.python.solutions import face_detection - НЕ РАБОТАЕТ: {e}")
    
    # Способ 4: tasks
    try:
        from mediapipe.tasks import python
        print("  ✓ from mediapipe.tasks import python - РАБОТАЕТ")
    except ImportError as e:
        print(f"  ❌ from mediapipe.tasks import python - НЕ РАБОТАЕТ: {e}")
    
    # Проверка всех атрибутов
    print("\nВсе доступные атрибуты mp (первые 20):")
    attrs = [x for x in dir(mp) if not x.startswith('_')]
    for attr in attrs[:20]:
        print(f"  - {attr}")
    
    # Попытка создать FaceDetection
    print("\nПопытка создать FaceDetection:")
    try:
        if hasattr(mp, 'solutions') and hasattr(mp.solutions, 'face_detection'):
            FaceDetection = mp.solutions.face_detection.FaceDetection
            detector = FaceDetection(model_selection=1, min_detection_confidence=0.5)
            print("  ✓ FaceDetection создан успешно через mp.solutions.face_detection")
        else:
            print("  ❌ mp.solutions.face_detection недоступен")
    except Exception as e:
        print(f"  ❌ Ошибка создания FaceDetection: {e}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"\n❌ MediaPipe не установлен: {e}")

print("\n" + "="*60)

