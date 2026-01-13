"""Роутер для генерации QR-кодов.

Команда /qrcode позволяет создать QR-код из текста или ссылки.
Пользователь отправляет текст, бот отвечает картинкой с QR-кодом.

ВНИМАНИЕ: Этот файл нельзя запускать напрямую!
Запускайте бота командой: python -m src.bot
"""
import logging
import sys
from typing import Dict
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Защита от прямого запуска файла
if __name__ == "__main__":
    print("❌ Ошибка: Этот файл нельзя запускать напрямую!")
    print("✅ Правильный способ запуска бота:")
    print("   python -m src.bot")
    sys.exit(1)

from bot.keyboards.common import get_main_menu
from bot.services.qrcode_service import QRCodeService

# Создаём логгер
logger = logging.getLogger(__name__)

# Создаём роутер для QR-кодов
qrcode_router = Router()

# Создаём сервис для генерации QR-кодов
qr_service = QRCodeService()

# Храним состояния пользователей (ожидаем ли от них текст)
# Ключ - ID пользователя, значение - True, если ждём текст
_waiting_for_text: Dict[int, bool] = {}


@qrcode_router.message(Command("qrcode"))
async def cmd_qrcode(message: Message) -> None:
    """Обработчик команды /qrcode.
    
    Просит пользователя отправить текст или ссылку для создания QR-кода.
    """
    user_id = message.from_user.id
    
    # Запоминаем, что ждём от пользователя текст
    _waiting_for_text[user_id] = True
    
    await message.answer(
        "📱 <b>QR-код генератор</b>\n\n"
        "Отправьте мне текст или ссылку, и я создам QR-код.\n\n"
        "Примеры:\n"
        "• https://telegram.org\n"
        "• Привет, мир!\n"
        "• +7 999 123-45-67\n\n"
        "Отправьте /cancel для отмены."
    )


@qrcode_router.message(lambda message: message.text == "📱 QR-код")
async def cmd_qrcode_button(message: Message) -> None:
    """Обработчик кнопки "QR-код" в меню."""
    await cmd_qrcode(message)


@qrcode_router.message(Command("cancel"))
async def cmd_cancel(message: Message) -> None:
    """Обработчик команды /cancel - отмена ожидания текста."""
    user_id = message.from_user.id
    
    if user_id in _waiting_for_text:
        del _waiting_for_text[user_id]
    
    await message.answer(
        "❌ Операция отменена.\n\n"
        "Вы вернулись в главное меню.",
        reply_markup=get_main_menu()
    )


def _is_waiting_for_qrcode(message: Message) -> bool:
    """Проверяет, ожидаем ли мы текст для QR-кода от этого пользователя.
    
    Используется как фильтр, чтобы не перехватывать сообщения других режимов.
    """
    return _waiting_for_text.get(message.from_user.id, False)


@qrcode_router.message(F.text, _is_waiting_for_qrcode)
async def handle_text_for_qrcode(message: Message) -> None:
    """Обработчик текста для создания QR-кода.
    
    Срабатывает ТОЛЬКО если пользователь находится в режиме ожидания текста.
    Создаёт QR-код и отправляет картинку.
    """
    user_id = message.from_user.id
    
    # Убираем из списка ожидающих
    del _waiting_for_text[user_id]
    
    text = message.text.strip()
    
    # Проверяем, что текст не пустой
    if not text:
        await message.answer(
            "❌ Текст не может быть пустым.\n"
            "Попробуйте ещё раз: /qrcode"
        )
        return
    
    try:
        # Генерируем QR-код
        qr_image = qr_service.generate_qrcode(text)
        
        # Создаём файл для отправки
        # BufferedInputFile - это способ отправить файл из памяти (не с диска)
        photo = BufferedInputFile(
            file=qr_image.read(),
            filename="qrcode.png"
        )
        
        # Определяем тип контента
        if qr_service.is_valid_url(text):
            content_type = "🔗 Ссылка"
        else:
            content_type = "📝 Текст"
        
        # Отправляем QR-код как фото
        await message.answer_photo(
            photo=photo,
            caption=(
                f"✅ QR-код создан!\n\n"
                f"{content_type}: <code>{text[:100]}{'...' if len(text) > 100 else ''}</code>\n\n"
                f"Отсканируйте камерой телефона."
            )
        )
        
        # Возвращаем главное меню
        await message.answer(
            "Создать ещё один QR-код? Используйте /qrcode",
            reply_markup=get_main_menu()
        )
        
    except ValueError as e:
        # Ошибка валидации (текст слишком длинный и т.д.)
        await message.answer(
            f"❌ Ошибка: {e}\n\n"
            "Попробуйте ещё раз: /qrcode"
        )
    except Exception as e:
        # Неожиданная ошибка
        logger.error(f"Ошибка при создании QR-кода: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при создании QR-кода.\n"
            "Попробуйте позже."
        )
