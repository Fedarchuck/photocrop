# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .
COPY setup.py .
COPY README.md .

# Копируем исходный код
COPY src/ ./src/

# Устанавливаем системные зависимости для OpenCV
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgthread-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -e .

# Открываем порт (будет использован из ENV PORT)
EXPOSE 8080

# Запускаем приложение
CMD python -m facecrop --ui --port ${PORT:-8080}
