"""Простой запуск Web UI для FaceCrop."""

import sys
from pathlib import Path

# Добавляем src в путь
sys.path.insert(0, str(Path(__file__).parent / "src"))

from facecrop.ui import launch_ui

if __name__ == '__main__':
    import socket
    
    def find_free_port(start_port=7860, max_attempts=10):
        """Находит свободный порт начиная с start_port."""
        for port in range(start_port, start_port + max_attempts):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('127.0.0.1', port))
                    return port
                except OSError:
                    continue
        return None
    
    print("\n" + "="*60)
    print("FaceCrop Web UI - Простой запуск")
    print("="*60)
    
    # Ищем свободный порт
    port = find_free_port(7860)
    if port is None:
        print("\n❌ Не удалось найти свободный порт в диапазоне 7860-7869")
        print("Попробуйте закрыть другие приложения или использовать:")
        print("python -m facecrop --ui --port 8000")
        sys.exit(1)
    
    if port != 7860:
        print(f"\n⚠ Порт 7860 занят, используем порт {port}")
    else:
        print(f"\n✓ Используем порт {port}")
    
    print(f"После запуска откройте браузер по адресу: http://127.0.0.1:{port}")
    print("\nДля остановки нажмите Ctrl+C\n")
    
    try:
        launch_ui(server_name="127.0.0.1", server_port=port)
    except KeyboardInterrupt:
        print("\n\nСервер остановлен.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("\nПопробуйте:")
        print("1. Проверить установку: pip install -r requirements.txt")
        print(f"2. Использовать другой порт: python -m facecrop --ui --port {port + 1}")
        sys.exit(1)

