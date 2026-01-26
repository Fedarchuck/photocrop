# Исправление проблемы с MediaPipe

## Проблема
Ошибка: `module 'mediapipe' has no attribute 'solutions'`

Это происходит когда MediaPipe установлен, но структура модуля не соответствует ожидаемой.

## Решение

### Вариант 1: Переустановка MediaPipe

```bash
pip uninstall mediapipe
pip install mediapipe
```

### Вариант 2: Установка конкретной версии

Если у вас Python 3.13, попробуйте:

```bash
pip uninstall mediapipe
pip install mediapipe==0.10.30
```

Или:

```bash
pip uninstall mediapipe
pip install mediapipe==0.10.31
```

### Вариант 3: Использование альтернативной библиотеки

Если MediaPipe не работает, можно временно использовать OpenCV для детекции лиц (требует доработки кода).

## Проверка

После установки проверьте:

```python
python -c "import mediapipe as mp; print(hasattr(mp, 'solutions'))"
```

Должно вывести `True`.

## После исправления

1. Перезапустите Web UI
2. Попробуйте обработать фото снова

## Если проблема сохраняется

Проверьте версию Python:
```bash
python --version
```

MediaPipe может не поддерживать Python 3.13. В этом случае:
- Используйте Python 3.11 или 3.12
- Или дождитесь обновления MediaPipe

