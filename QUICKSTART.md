# Быстрый старт FaceCrop

## Установка

```bash
# Установите зависимости
pip install -r requirements.txt
```

## Использование

### CLI - Обработка одного файла
```bash
python -m facecrop --input photo.jpg --output output/
```

### CLI - Обработка папки
```bash
python -m facecrop --input photos/ --output output/ --recursive
```

### CLI - С параметрами
```bash
python -m facecrop -i photos/ -o output/ --size 512 --k 3.0 --padding blur
```

### Web UI
```bash
# Простой способ
python run_ui.py

# Или через CLI
python -m facecrop --ui

# С другим портом (если 7860 занят)
python -m facecrop --ui --port 7861
```

После запуска в терминале появится адрес. Откройте его в браузере (обычно http://127.0.0.1:7860)

## Параметры

- `--size` - Размер квадрата (по умолчанию 1024)
- `--k` - Множитель размера лица (по умолчанию 2.5)
  - Меньше = лицо крупнее
  - Больше = больше контекста
- `--padding` - Тип padding: none, blur, mirror, solid
- `--visualize` - Сохранить визуализацию с рамками
- `--dry-run` - Проверка без сохранения

## Примеры

```bash
# Крупное лицо в кадре
python -m facecrop -i photo.jpg -o output/ --k 2.0

# Больше контекста вокруг лица
python -m facecrop -i photo.jpg -o output/ --k 3.5

# С размытым фоном при padding
python -m facecrop -i photo.jpg -o output/ --padding blur

# Отладка с визуализацией
python -m facecrop -i photo.jpg -o output/ --visualize
```

