"""Точка входа для запуска бота как модуля.

Этот файл позволяет запускать бота командой:
    python -m src.bot

или

    python -m bot

(если вы находитесь в папке src)
"""
import asyncio
import logging
import sys
from pathlib import Path

# Добавляем путь к папке src в список путей, где Python ищет модули
# Это нужно, чтобы Python мог найти наши модули (bot.config, bot.routers и т.д.)
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from bot.main import main

if __name__ == "__main__":
    # Запускаем бота
    asyncio.run(main())
