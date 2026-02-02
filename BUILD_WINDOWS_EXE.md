# Windows версия (для обычных пользователей)

Цель: собрать `FaceCrop.exe`, который запускается двойным кликом и открывает браузер с Web UI локально.

## Для пользователя (как запускать)

1. Скачайте архив `FaceCrop-Windows.zip` из GitHub Releases (или из артефактов GitHub Actions).
2. Распакуйте архив в любую папку.
3. Запустите `FaceCrop.exe`.
4. Откроется браузер. Если Windows спросит про доступ через firewall — разрешите для **Private networks**.

## Для разработчика (как собрать локально)

```bash
pip install -r requirements.txt
pip install -e .
pip install pyinstaller
pyinstaller facecrop_windows.spec
```

Результат будет в `dist/FaceCrop.exe`.

## Примечания

- Первый старт может занимать 10–30 секунд.
- Если UI не открылся автоматически — откройте в браузере `http://127.0.0.1:7860` (или соседний порт).

