"""Web UI для FaceCrop на Gradio."""

import gradio as gr
import tempfile
import zipfile
from pathlib import Path
from PIL import Image
from typing import List, Tuple
import os

from .core import FaceCropper


# Глобальное хранилище для отслеживания обработанных файлов
_processed_files_storage = {}

def process_images_ui(
    files: List,
    size: int,
    k: float
) -> Tuple[str, List[Tuple[str, str]]]:
    """Обрабатывает изображения через UI."""
    if not files:
        return "Загрузите изображения", []
    
    results = []
    temp_dir = tempfile.mkdtemp()
    _processed_files_storage['temp_dir'] = temp_dir
    _processed_files_storage['files_map'] = {}  # filename -> output_path
    
    try:
        # Инициализация cropper с проверкой ошибок
        try:
            cropper = FaceCropper()
        except ImportError as e:
            error_msg = str(e)
            if "MediaPipe" in error_msg or "mediapipe" in error_msg.lower():
                return (
                    f"Ошибка MediaPipe: {error_msg}\n\n"
                    "Решение:\n"
                    "1. Переустановите MediaPipe: pip install --upgrade mediapipe\n"
                    "2. Или установите конкретную версию: pip install mediapipe==0.10.0\n"
                    "3. Перезапустите сервер после установки",
                    []
                )
            else:
                return f"Ошибка импорта: {error_msg}", []
        except Exception as e:
            return f"Ошибка инициализации: {str(e)}", []
        
        try:
            for file_obj in files:
                # Gradio может передавать объекты файлов или пути
                file_path = file_obj.name if hasattr(file_obj, 'name') else str(file_obj)
                
                # Загружаем изображение
                try:
                    image = Image.open(file_path)
                except Exception as e:
                    return f"Ошибка загрузки изображения {Path(file_path).name}: {str(e)}", []
                
                # Кропаем
                try:
                    cropped = cropper.crop_to_square_with_face(
                        image, target_size=size, k=k, padding="none"
                    )
                except Exception as e:
                    return f"Ошибка обработки изображения {Path(file_path).name}: {str(e)}", []
                
                # Сохраняем во временную папку
                filename = Path(file_path).stem
                output_path = Path(temp_dir) / f"{filename}_square.jpg"
                cropped = cropped.convert('RGB')
                cropped.save(output_path, 'JPEG', quality=95)
                
                # Сохраняем маппинг для ручной обрезки
                _processed_files_storage['files_map'][filename] = {
                    'output': str(output_path),
                    'original': file_path
                }
                
                # Добавляем в результаты для предпросмотра
                results.append((str(output_path), f"Обработано: {filename}"))
            
            # Создаем ZIP архив
            zip_path = Path(temp_dir) / "results.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_obj in files:
                    file_path = file_obj.name if hasattr(file_obj, 'name') else str(file_obj)
                    filename = Path(file_path).stem
                    output_path = Path(temp_dir) / f"{filename}_square.jpg"
                    if output_path.exists():
                        zipf.write(output_path, f"{filename}_square.jpg")
            
            return str(zip_path), results
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return f"Ошибка обработки: {str(e)}\n\nДетали:\n{error_details}", []
        
    except Exception as e:
        import traceback
        return f"Критическая ошибка: {str(e)}\n\n{traceback.format_exc()}", []


def launch_ui(share: bool = False, server_name: str = "127.0.0.1", server_port: int = 7860):
    """Запускает Gradio UI."""
    import socket
    
    # Функция для проверки доступности порта
    def is_port_available(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((server_name, port))
                return True
            except OSError:
                return False
    
    # Если указанный порт занят, ищем свободный
    original_port = server_port
    if not is_port_available(server_port):
        print(f"⚠ Порт {server_port} занят, ищем свободный порт...")
        for port in range(server_port, server_port + 10):
            if is_port_available(port):
                server_port = port
                print(f"✓ Найден свободный порт: {port}")
                break
        else:
            print(f"❌ Не удалось найти свободный порт в диапазоне {original_port}-{original_port + 9}")
            print(f"Попробуйте указать другой порт: python -m facecrop --ui --port 8000")
            raise OSError(f"Не удалось найти свободный порт")
    
    # Получаем путь к шрифту
    fonts_dir = Path(__file__).parent.parent.parent / "fonts"
    font_path = fonts_dir / "Inter_24pt-Regular.ttf"
    
    # CSS для загрузки кастомного шрифта и скрытия ненужных кнопок
    custom_css = f"""
    @font-face {{
        font-family: 'Inter';
        src: url('{font_path.absolute().as_uri()}') format('truetype');
        font-weight: normal;
        font-style: normal;
    }}
    
    * {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }}
    
    body, .gradio-container {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }}
    
    /* Скрываем кнопки "Поделиться" и "Fullscreen" в Gallery */
    button[aria-label*="share" i],
    button[aria-label*="поделиться" i],
    button[title*="share" i],
    button[title*="поделиться" i],
    button svg[data-testid*="share"],
    button svg[data-testid*="Share"] {{
        display: none !important;
    }}
    
    /* Скрываем кнопку Fullscreen */
    button[aria-label*="fullscreen" i],
    button[aria-label*="полный экран" i],
    button[title*="fullscreen" i],
    button[title*="полный экран" i],
    button svg[data-testid*="fullscreen"],
    button svg[data-testid*="Fullscreen"] {{
        display: none !important;
    }}
    
    /* Скрываем все кнопки в правом верхнем углу Gallery (кроме закрытия) */
    #gallery button.absolute.top-2.right-2:not([aria-label*="close" i]):not([aria-label*="Close" i]):not([aria-label*="закрыть" i]):not([aria-label*="Закрыть" i]) {{
        display: none !important;
    }}
    
    /* Альтернативный селектор для кнопок в Gallery */
    div[data-testid*="gallery"] button.absolute.top-2.right-2:not([aria-label*="close" i]):not([aria-label*="Close" i]) {{
        display: none !important;
    }}
    
    /* Скрываем кнопки через селектор по классам */
    button[class*="absolute"][class*="top-2"][class*="right-2"]:not([aria-label*="close" i]):not([aria-label*="Close" i]) {{
        display: none !important;
    }}
    
    /* Скрываем кнопки в модальном окне Gallery */
    .gradio-modal button[aria-label*="share" i],
    .gradio-modal button[aria-label*="fullscreen" i],
    .gradio-modal button[title*="share" i],
    .gradio-modal button[title*="fullscreen" i] {{
        display: none !important;
    }}
    
    """
    
    # Используем темную тему по умолчанию
    with gr.Blocks(title="FaceCrop - Кроп фотографий до квадрата") as demo:
        gr.Markdown("""
        # FaceCrop - Автоматический кроп фотографий до квадрата
        
        Загрузите фотографии с лицами, и они будут автоматически обрезаны до квадратного формата
        с сохранением лица в центре.
        """)
        
        with gr.Row():
            with gr.Column():
                file_input = gr.File(
                    file_count="multiple",
                    label="Загрузить изображения",
                    file_types=["image"]
                )
                
                with gr.Row():
                    size_slider = gr.Slider(
                        minimum=256,
                        maximum=2048,
                        value=1024,
                        step=64,
                        label="Размер квадрата"
                    )
                    k_slider = gr.Slider(
                        minimum=1.5,
                        maximum=4.0,
                        value=2.5,
                        step=0.1,
                        label="Множитель размера лица (k)"
                    )
                
                process_btn = gr.Button("Обработать", variant="primary")
            
            with gr.Column():
                gr.Markdown("**Результаты обработки:**")
                output_gallery = gr.Gallery(
                    label="Результаты",
                    show_label=True,
                    elem_id="gallery",
                    columns=3,
                    height="auto"
                )
                
                download_file = gr.File(
                    label="Скачать все результаты (ZIP)",
                    visible=True
                )
        
        status_text = gr.Textbox(
            label="Статус",
            interactive=False,
            value="Готов к работе"
        )
        
        # Секция для просмотра и обрезки изображений
        gr.Markdown("---")
        gr.Markdown("## ✂️ Просмотр и обрезка результатов")
        
        # Хранилище состояния
        current_index = gr.State(value=0)
        gallery_data = gr.State(value=[])
        original_image_state = gr.State(value=None)  # Хранит оригинальное изображение для обрезки
        
        with gr.Row():
            # Левая колонка - текущее изображение
            with gr.Column(scale=2):
                current_image = gr.Image(
                    label="Текущее изображение",
                    type="pil",
                    height=400,
                    interactive=False
                )
                
                # Навигация
                with gr.Row():
                    prev_btn = gr.Button("◀ Предыдущее", size="lg")
                    image_counter = gr.Markdown("**0 / 0**")
                    next_btn = gr.Button("Следующее ▶", size="lg")
            
            # Правая колонка - обрезка
            with gr.Column(scale=1):
                gr.Markdown("**Настройка обрезки:**")
                
                crop_position = gr.Slider(
                    minimum=0,
                    maximum=100,
                    value=50,
                    step=1,
                    label="Положение обрезки (%)"
                )
                
                crop_size_slider = gr.Slider(
                    minimum=256,
                    maximum=2048,
                    value=1024,
                    step=64,
                    label="Размер квадрата (px)"
                )
                
                crop_btn = gr.Button("✂️ Обрезать это изображение", variant="primary", size="lg")
                
                crop_status = gr.Textbox(
                    label="Статус",
                    interactive=False,
                    value="Обработайте фотографии, чтобы начать"
                )
                
                # Превью обрезки
                crop_preview = gr.Image(
                    label="Превью обрезки",
                    type="pil",
                    height=200,
                    interactive=False
                )
        
        def get_original_for_index(idx, gallery):
            """Получает оригинальное изображение для указанного индекса."""
            if not gallery or idx < 0 or idx >= len(gallery):
                return None
            
            item = gallery[idx]
            result_path = item[0] if isinstance(item, tuple) else str(item)
            
            # Ищем оригинал в files_map
            filename = Path(result_path).stem.replace('_square', '')
            if filename in _processed_files_storage.get('files_map', {}):
                original_path = _processed_files_storage['files_map'][filename].get('original')
                if original_path and Path(original_path).exists():
                    return Image.open(original_path)
            
            return None
        
        def process_wrapper(files, size, k):
            if not files:
                return "Загрузите изображения", None, [], [], None, "**0 / 0**", "Загрузите и обработайте фотографии", None
            
            zip_path, gallery = process_images_ui(files, int(size), float(k))
            
            if zip_path and Path(zip_path).exists():
                status = f"✓ Обработано {len(gallery)} изображений"
                
                # Загружаем первое изображение для просмотра
                first_result = None
                first_original = None
                
                if gallery:
                    first_path = gallery[0][0] if isinstance(gallery[0], tuple) else str(gallery[0])
                    if Path(first_path).exists():
                        first_result = Image.open(first_path)
                    
                    # Загружаем оригинал
                    first_original = get_original_for_index(0, gallery)
                
                counter = f"**1 / {len(gallery)}**" if gallery else "**0 / 0**"
                
                if first_original:
                    crop_msg = "Двигайте слайдер для настройки обрезки"
                else:
                    crop_msg = "Используйте кнопки навигации для просмотра"
                
                return status, zip_path, gallery, gallery, first_result, counter, crop_msg, first_original
            else:
                return zip_path, None, [], [], None, "**0 / 0**", "Ошибка обработки", None
        
        def navigate_images(current_idx, gallery, direction):
            """Навигация по изображениям."""
            if not gallery:
                return None, "**0 / 0**", 0, "Нет изображений", None, None
            
            new_idx = current_idx + direction
            if new_idx < 0:
                new_idx = len(gallery) - 1  # Переход к последнему
            elif new_idx >= len(gallery):
                new_idx = 0  # Переход к первому
            
            # Загружаем обработанное изображение для показа
            item = gallery[new_idx]
            result_path = item[0] if isinstance(item, tuple) else str(item)
            
            result_img = None
            original_img = None
            
            if Path(result_path).exists():
                result_img = Image.open(result_path)
            
            # Загружаем оригинал для обрезки
            original_img = get_original_for_index(new_idx, gallery)
            
            counter = f"**{new_idx + 1} / {len(gallery)}**"
            
            if original_img:
                status = f"Изображение {new_idx + 1}. Двигайте слайдер для настройки обрезки."
            else:
                status = f"Изображение {new_idx + 1}. Оригинал не найден."
            
            return result_img, counter, new_idx, status, None, original_img
        
        def update_crop_preview(original_img, position_pct, target_size):
            """Обновляет превью обрезки из ОРИГИНАЛЬНОГО изображения."""
            if original_img is None:
                return None
            
            try:
                w, h = original_img.size
                crop_size = min(w, h)
                
                # Определяем направление смещения
                if w > h:
                    # Горизонтальное изображение - смещаем по X
                    max_offset = w - crop_size
                    x = int((position_pct / 100) * max_offset)
                    y = 0
                else:
                    # Вертикальное изображение - смещаем по Y
                    max_offset = h - crop_size
                    x = 0
                    y = int((position_pct / 100) * max_offset)
                
                cropped = original_img.crop((x, y, x + crop_size, y + crop_size))
                cropped = cropped.resize((target_size, target_size), Image.Resampling.LANCZOS)
                return cropped
            except:
                return None
        
        def apply_crop(original_img, position_pct, target_size, current_idx, gallery):
            """Применяет обрезку к текущему изображению из ОРИГИНАЛА."""
            try:
                if original_img is None or not gallery:
                    return gallery, gallery, None, "Ошибка: оригинал не найден. Попробуйте перейти к другому изображению."
                
                w, h = original_img.size
                crop_size = min(w, h)
                
                # Определяем направление смещения
                if w > h:
                    max_offset = w - crop_size
                    x = int((position_pct / 100) * max_offset)
                    y = 0
                else:
                    max_offset = h - crop_size
                    x = 0
                    y = int((position_pct / 100) * max_offset)
                
                cropped = original_img.crop((x, y, x + crop_size, y + crop_size))
                
                if cropped.mode != 'RGB':
                    cropped = cropped.convert('RGB')
                
                cropped = cropped.resize((target_size, target_size), Image.Resampling.LANCZOS)
                
                # Получаем путь к файлу результата
                item = gallery[current_idx]
                result_path = item[0] if isinstance(item, tuple) else str(item)
                
                # Сохраняем
                output_path = Path(result_path)
                cropped.save(output_path, 'JPEG', quality=95)
                
                # Обновляем галерею
                updated_gallery = []
                for idx, item in enumerate(gallery):
                    if idx == current_idx:
                        if isinstance(item, tuple):
                            updated_gallery.append((str(output_path), f"✓ Обрезано: {output_path.stem}"))
                        else:
                            updated_gallery.append((str(output_path), f"✓ Обрезано"))
                    else:
                        updated_gallery.append(item)
                
                return updated_gallery, updated_gallery, cropped, f"✓ Обрезка применена! {target_size}x{target_size}"
            
            except Exception as e:
                return gallery, gallery, None, f"Ошибка: {str(e)}"
        
        def update_zip_after_manual_crop():
            """Обновляет ZIP архив после ручной обрезки."""
            try:
                if 'temp_dir' not in _processed_files_storage:
                    return None
                
                temp_dir = _processed_files_storage['temp_dir']
                zip_path = Path(temp_dir) / "results.zip"
                
                # Пересоздаем ZIP со всеми файлами из temp_dir
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in Path(temp_dir).glob("*.jpg"):
                        zipf.write(file_path, file_path.name)
                
                return str(zip_path) if zip_path.exists() else None
            except Exception as e:
                return None
        
        # Обработка изображений
        process_btn.click(
            fn=process_wrapper,
            inputs=[file_input, size_slider, k_slider],
            outputs=[status_text, download_file, output_gallery, gallery_data, current_image, image_counter, crop_status, original_image_state]
        )
        
        # Навигация - предыдущее
        prev_btn.click(
            fn=lambda idx, gallery: navigate_images(idx, gallery, -1),
            inputs=[current_index, gallery_data],
            outputs=[current_image, image_counter, current_index, crop_status, crop_preview, original_image_state]
        )
        
        # Навигация - следующее
        next_btn.click(
            fn=lambda idx, gallery: navigate_images(idx, gallery, 1),
            inputs=[current_index, gallery_data],
            outputs=[current_image, image_counter, current_index, crop_status, crop_preview, original_image_state]
        )
        
        # Клик по галерее - переход к изображению
        def on_gallery_click(evt: gr.SelectData, gallery):
            if not gallery:
                return None, "**0 / 0**", 0, "Нет изображений", None, None
            
            idx = evt.index
            item = gallery[idx]
            result_path = item[0] if isinstance(item, tuple) else str(item)
            
            result_img = None
            original_img = None
            
            if Path(result_path).exists():
                result_img = Image.open(result_path)
            
            # Загружаем оригинал
            original_img = get_original_for_index(idx, gallery)
            
            if original_img:
                status = f"Изображение {idx + 1}. Двигайте слайдер для настройки обрезки."
            else:
                status = f"Изображение {idx + 1}. Оригинал не найден."
            
            return result_img, f"**{idx + 1} / {len(gallery)}**", idx, status, None, original_img
        
        output_gallery.select(
            fn=on_gallery_click,
            inputs=[gallery_data],
            outputs=[current_image, image_counter, current_index, crop_status, crop_preview, original_image_state]
        )
        
        # Обновление превью при изменении слайдера положения (из оригинала!)
        crop_position.change(
            fn=update_crop_preview,
            inputs=[original_image_state, crop_position, crop_size_slider],
            outputs=[crop_preview]
        )
        
        # Применение обрезки (из оригинала!)
        crop_btn.click(
            fn=apply_crop,
            inputs=[original_image_state, crop_position, crop_size_slider, current_index, gallery_data],
            outputs=[output_gallery, gallery_data, current_image, crop_status]
        ).then(
            fn=update_zip_after_manual_crop,
            outputs=[download_file]
        )
    
    # Вывод информации перед запуском
    print("\n" + "="*60)
    print("FaceCrop Web UI")
    print("="*60)
    print(f"\nЗапуск сервера на http://{server_name}:{server_port}")
    print("После запуска откройте этот адрес в браузере")
    print("\nДля остановки нажмите Ctrl+C")
    print("="*60 + "\n")
    
    # Проверка версии Gradio
    try:
        print(f"✓ Gradio версия: {gr.__version__}")
    except AttributeError:
        print("✓ Gradio загружен")
    
    try:
        print("Запуск сервера...")
        demo.launch(
            share=share,
            server_name=server_name if server_name else "127.0.0.1",
            server_port=server_port,
            show_error=True,
            inbrowser=False,
            theme=gr.themes.Monochrome(),
            css=custom_css
        )
        print("\n✓ Сервер запущен и работает!")
        print(f"✓ Откройте в браузере: http://{server_name}:{server_port}\n")
    except OSError as e:
        error_msg = str(e)
        if "Address already in use" in error_msg or "порт уже используется" in error_msg or "address is already in use" in error_msg.lower() or "Cannot find empty port" in error_msg:
            print(f"\n❌ Ошибка: Порт {server_port} уже занят!")
            print(f"\nРешение:")
            print(f"1. Используйте другой порт: python -m facecrop --ui --port 8000")
            print(f"2. Или закройте приложение, использующее порт {server_port}")
            print(f"3. Или используйте: python run_ui.py (автоматически найдет свободный порт)")
        elif "cannot assign requested address" in error_msg.lower():
            print(f"\n❌ Ошибка: Не удается привязать адрес {server_name}")
            print(f"Попробуйте использовать 0.0.0.0 или localhost")
        else:
            print(f"\n❌ Ошибка при запуске сервера: {e}")
            print(f"Тип ошибки: {type(e).__name__}")
        raise
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        print(f"Тип ошибки: {type(e).__name__}")
        import traceback
        print("\nПолный traceback:")
        traceback.print_exc()
        print("\nПроверьте:")
        print("1. Установлен ли Gradio: pip install gradio")
        print("2. Не занят ли порт другим приложением")
        print("3. Правильно ли установлены все зависимости: pip install -r requirements.txt")
        raise


if __name__ == '__main__':
    import sys
    try:
        launch_ui()
    except KeyboardInterrupt:
        print("\n\nСервер остановлен.")
        sys.exit(0)

