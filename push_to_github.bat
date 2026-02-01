@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo === Git: добавление изменений ===
git add -A
git status

echo.
echo === Коммит ===
git commit -m "Добавлена поддержка Render: чтение PORT из env и bind на 0.0.0.0"
if errorlevel 1 (
  echo Нет изменений для коммита или ошибка коммита. Push пропущен.
  goto :end
)

echo.
echo === Отправка на GitHub ===
git push origin main
if errorlevel 1 echo Ошибка push. Проверьте доступ к GitHub и настройки git.

:end
echo.
echo Готово.
pause
