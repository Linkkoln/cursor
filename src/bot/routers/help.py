"""Роутер для команды /help - справка по использованию бота.

Когда пользователь просит помощь, бот показывает инструкцию,
как пользоваться ботом.
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

# Создаём роутер для обработки команды /help
help_router = Router()


@help_router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Обработчик команды /help - показывает справку.
    
    Когда пользователь пишет /help или нажимает кнопку "Помощь",
    вызывается эта функция.
    """
    try:
        # Получаем текст справки из сервиса
        help_text = MessageService.get_help_message()
        
        # Отправляем справку вместе с главным меню
        await message.answer(
            help_text,
            reply_markup=get_main_menu()
        )
    except (TelegramNetworkError, TelegramAPIError) as e:
        logger.error(f"Не удалось отправить сообщение: {e}")


@help_router.message(lambda message: message.text == "ℹ️ Помощь")
async def cmd_help_button(message: Message) -> None:
    """Обработчик кнопки "Помощь" в меню.
    
    Когда пользователь нажимает кнопку "Помощь",
    вызывается та же функция, что и для команды /help.
    """
    # Вызываем ту же функцию, что и для команды /help
    await cmd_help(message)
