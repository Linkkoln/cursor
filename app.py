"""Точка входа для запуска бота на Amvera.

Этот файл нужен для деплоя на Amvera.
Он просто запускает основную функцию бота.
"""
import asyncio
import sys
from pathlib import Path

# Добавляем путь к папке src в список путей, где Python ищет модули
# Это нужно, чтобы Python мог найти наши модули (bot.config, bot.routers и т.д.)
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from bot.main import main

if __name__ == "__main__":
    # Запускаем бота
    asyncio.run(main())
