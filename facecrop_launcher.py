"""
Локальный запуск для "обычных пользователей".

Цель: один .exe, двойной клик → открылся браузер → UI работает локально.
"""

from __future__ import annotations

import io
import socket
import threading
import time
import webbrowser
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class LaunchConfig:
    host: str = "127.0.0.1"
    start_port: int = 7860
    max_attempts: int = 20
    open_browser_delay_s: float = 1.5


def find_free_port(host: str, start_port: int, max_attempts: int) -> int:
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((host, port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"Не удалось найти свободный порт в диапазоне {start_port}-{start_port + max_attempts - 1}")


def _open_browser_later(url: str, delay_s: float) -> None:
    time.sleep(delay_s)
    try:
        webbrowser.open(url, new=1, autoraise=True)
    except Exception:
        pass


def main() -> None:
    # В режиме без консоли stdout/stderr могут быть None -> Uvicorn падает.
    class _DummyIO(io.TextIOBase):
        def write(self, s):  # type: ignore[override]
            return len(s)

        def flush(self):  # type: ignore[override]
            pass

        def isatty(self):  # type: ignore[override]
            return False

    if sys.stdout is None:
        sys.stdout = _DummyIO()  # type: ignore[assignment]
    if sys.stderr is None:
        sys.stderr = _DummyIO()  # type: ignore[assignment]

    cfg = LaunchConfig()
    port = find_free_port(cfg.host, cfg.start_port, cfg.max_attempts)
    url = f"http://{cfg.host}:{port}"

    # Открываем браузер чуть позже, чтобы сервер успел подняться
    t = threading.Thread(target=_open_browser_later, args=(url, cfg.open_browser_delay_s), daemon=True)
    t.start()

    from facecrop.ui import launch_ui

    # inbrowser=False — открываем сами, чтобы не зависеть от настроек Gradio
    launch_ui(server_name=cfg.host, server_port=port, inbrowser=False)


if __name__ == "__main__":
    main()

