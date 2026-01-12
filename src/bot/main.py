"""Главный файл для запуска бота.

Этот файл - точка входа в программу. Отсюда всё начинается.
Когда мы запускаем бота, выполняется функция main().
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

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from bot.config import BOT_TOKEN
from bot.routers.start import start_router
from bot.routers.help import help_router
from bot.routers.echo import echo_router

# Настраиваем логирование (запись информации о работе программы)
# Логи - это как дневник бота: он записывает, что происходит
# Это помогает понять, работает ли бот правильно, и найти ошибки
# Представь, что бот ведёт дневник и записывает туда всё, что делает
logging.basicConfig(
    level=logging.INFO,  # Показывать информационные сообщения
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # Как выводить сообщения
)
logger = logging.getLogger(__name__)  # Создаём объект для записи в лог (дневник)


async def main() -> None:
    """Основная функция для запуска бота.
    
    async - это специальное слово, которое означает "асинхронная функция".
    Асинхронная функция может делать несколько дел одновременно или ждать, 
    пока что-то выполнится (например, отправка сообщения в Telegram).
    Это как готовить обед и одновременно смотреть телевизор - делаешь несколько дел сразу.
    """
    # Создаём объект бота (это наш робот для Telegram)
    # Bot - это класс из библиотеки aiogram, который умеет общаться с Telegram
    # token - это ключ от двери (токен, который мы получили от @BotFather)
    # parse_mode - как форматировать текст (HTML позволяет делать текст жирным, курсивом и т.д.)
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Создаём диспетчер (это как почтальон)
    # Диспетчер получает сообщения от пользователей и решает, 
    # какую функцию вызвать для обработки этого сообщения
    dp = Dispatcher()
    
    # Подключаем роутеры к диспетчеру
    # Порядок важен: сначала обрабатываются команды (start, help),
    # потом кнопки меню, и в конце - обычные сообщения (echo)
    dp.include_router(start_router)
    dp.include_router(help_router)
    dp.include_router(echo_router)
    
    # Устанавливаем команды меню бота
    # Это команды, которые будут видны в меню Telegram (кнопка "Меню" рядом с полем ввода)
    # Когда пользователь нажмёт на кнопку меню, он увидит список команд
    commands = [
        BotCommand(command="start", description="Запустить бота и показать меню"),
        BotCommand(command="help", description="Показать справку по использованию бота"),
    ]
    await bot.set_my_commands(commands)
    
    # Записываем в лог (дневник), что бот запустился
    logger.info("Бот запущен и готов к работе")
    
    # Запускаем polling (опрос сервера)
    # Polling - это когда бот постоянно спрашивает у сервера Telegram:
    # "Пришли мне новые сообщения, если они есть!"
    # Бот делает это снова и снова, пока работает
    # await означает "подожди, пока эта операция не закончится"
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        # Если пользователь нажал Ctrl+C, останавливаем бота
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        # Если произошла какая-то ошибка, записываем её в лог
        logger.error(f"Произошла ошибка: {e}")
    finally:
        # В любом случае закрываем соединение с Telegram (вешаем трубку)
        await bot.session.close()


if __name__ == "__main__":
    # Это условие проверяет: "запустили ли мы этот файл напрямую?"
    # Если да - запускаем функцию main()
    # Если файл импортировали в другой файл - ничего не делаем
    # asyncio.run() - это специальная функция, которая запускает асинхронную функцию
    # Она нужна, потому что main() - асинхронная (async)
    asyncio.run(main())
