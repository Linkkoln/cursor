"""Роутер для команды /start и главного меню.

Когда пользователь запускает бота командой /start,
бот показывает приветствие и главное меню с кнопками.
"""
import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramNetworkError, TelegramAPIError

from bot.keyboards.common import get_main_menu
from bot.services.message import MessageService

# Создаём объект для записи логов (дневник)
logger = logging.getLogger(__name__)

# Создаём роутер для обработки команды /start
start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Обработчик команды /start - приветствие и показ главного меню.
    
    Когда пользователь пишет /start, вызывается эта функция.
    Бот отправляет приветственное сообщение и показывает меню с кнопками.
    """
    try:
        # Получаем текст приветствия из сервиса
        # Сервис содержит бизнес-логику, роутер только отправляет сообщения
        welcome_text = MessageService.get_welcome_message()
        
        # Отправляем приветствие вместе с клавиатурой (меню)
        # reply_markup - это клавиатура, которая появится вместо обычной клавиатуры
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu()
        )
    except (TelegramNetworkError, TelegramAPIError) as e:
        # Если не получилось отправить сообщение, записываем ошибку в лог
        logger.error(f"Не удалось отправить сообщение: {e}")


@start_router.message(lambda message: message.text == "🔄 Обновить меню")
async def cmd_refresh_menu(message: Message) -> None:
    """Обработчик кнопки "Обновить меню".
    
    Когда пользователь нажимает эту кнопку, бот снова показывает главное меню.
    """
    try:
        # Получаем текст сообщения из сервиса
        refresh_text = MessageService.get_menu_refreshed_message()
        
        await message.answer(
            refresh_text,
            reply_markup=get_main_menu()
        )
    except (TelegramNetworkError, TelegramAPIError) as e:
        logger.error(f"Не удалось отправить сообщение: {e}")
