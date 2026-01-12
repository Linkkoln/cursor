"""Роутер для команды /chatgpt - режим ChatGPT.

Когда пользователь активирует режим ChatGPT, бот начинает отвечать
на вопросы как языковая модель через OpenRouter.ai.
"""
import logging
from typing import Optional, Dict, List
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramNetworkError, TelegramAPIError

from bot.keyboards.common import get_main_menu, get_chatgpt_menu
from bot.services.llm import LLMService
from bot.config import OPENROUTER_API_KEY

# Создаём объект для записи логов (дневник)
logger = logging.getLogger(__name__)

# Создаём роутер для обработки команды /chatgpt
chatgpt_router = Router()

# Словарь для хранения истории разговоров пользователей
# Ключ - ID пользователя, значение - список сообщений
conversation_history: Dict[int, List[dict]] = {}

# Создаём экземпляр сервиса LLM (если API ключ установлен)
llm_service: Optional[LLMService] = None
if OPENROUTER_API_KEY:
    llm_service = LLMService(api_key=OPENROUTER_API_KEY)
else:
    logger.warning("OPENROUTER_API_KEY не установлен. Режим ChatGPT не будет работать.")


@chatgpt_router.message(Command("chatgpt"))
async def cmd_chatgpt(message: Message) -> None:
    """Обработчик команды /chatgpt - активация режима ChatGPT.
    
    Когда пользователь пишет /chatgpt, вызывается эта функция.
    Бот активирует режим ChatGPT и очищает историю разговора.
    """
    try:
        # Проверяем, установлен ли API ключ
        if not llm_service:
            await message.answer(
                "❌ Режим ChatGPT недоступен.\n\n"
                "Для работы режима ChatGPT необходимо установить OPENROUTER_API_KEY в файле .env\n\n"
                "Получите API ключ на https://openrouter.ai/",
                reply_markup=get_main_menu()
            )
            return
        
        # Очищаем историю разговора для этого пользователя
        user_id = message.from_user.id
        conversation_history[user_id] = []
        
        # Отправляем сообщение об активации режима
        await message.answer(
            "🤖 Режим ChatGPT активирован!\n\n"
            "Теперь я буду отвечать на ваши вопросы как языковая модель.\n"
            "Отправьте мне любой вопрос, и я постараюсь на него ответить.\n\n"
            "Для выхода из режима используйте кнопку 'Назад в меню'.",
            reply_markup=get_chatgpt_menu()
        )
    except (TelegramNetworkError, TelegramAPIError) as e:
        logger.error(f"Не удалось отправить сообщение: {e}")


@chatgpt_router.message(lambda message: message.text == "🤖 ChatGPT")
async def cmd_chatgpt_button(message: Message) -> None:
    """Обработчик кнопки "ChatGPT" в меню.
    
    Когда пользователь нажимает кнопку "ChatGPT",
    вызывается та же функция, что и для команды /chatgpt.
    """
    # Вызываем ту же функцию, что и для команды /chatgpt
    await cmd_chatgpt(message)


@chatgpt_router.message(lambda message: message.text == "⬅️ Назад в меню" and message.from_user.id in conversation_history)
async def cmd_back_from_chatgpt(message: Message) -> None:
    """Обработчик кнопки "Назад в меню" из режима ChatGPT.
    
    Когда пользователь нажимает эту кнопку в режиме ChatGPT,
    бот возвращается в главное меню и очищает историю разговора.
    """
    try:
        # Очищаем историю разговора для этого пользователя
        user_id = message.from_user.id
        if user_id in conversation_history:
            del conversation_history[user_id]
        
        await message.answer(
            "🏠 Вы вернулись в главное меню!",
            reply_markup=get_main_menu()
        )
    except (TelegramNetworkError, TelegramAPIError) as e:
        logger.error(f"Не удалось отправить сообщение: {e}")


@chatgpt_router.message()
async def chatgpt_handler(message: Message) -> None:
    """Обработчик сообщений в режиме ChatGPT.
    
    Эта функция обрабатывает все сообщения, когда пользователь находится в режиме ChatGPT.
    Она отправляет сообщение в LLM и возвращает ответ.
    """
    # Проверяем, что пользователь находится в режиме ChatGPT
    user_id = message.from_user.id
    if user_id not in conversation_history:
        # Если пользователь не в режиме ChatGPT, игнорируем сообщение
        return
    
    # Проверяем, что есть текст в сообщении
    if not message.text or message.text.strip() == "":
        await message.answer(
            "Пожалуйста, отправьте текстовое сообщение.",
            reply_markup=get_chatgpt_menu()
        )
        return
    
    # Проверяем, что сервис LLM доступен
    if not llm_service:
        await message.answer(
            "❌ Режим ChatGPT недоступен. Проверьте настройки.",
            reply_markup=get_main_menu()
        )
        return
    
    # Отправляем сообщение "Думаю..." пока обрабатывается запрос
    thinking_message = await message.answer("🤔 Думаю...")
    
    try:
        # Получаем историю разговора для этого пользователя
        history = conversation_history.get(user_id, [])
        
        # Отправляем запрос к LLM
        response = await llm_service.get_response(
            user_message=message.text,
            conversation_history=history
        )
        
        # Обновляем историю разговора
        # Добавляем сообщение пользователя и ответ бота
        conversation_history[user_id] = history + [
            {"role": "user", "content": message.text},
            {"role": "assistant", "content": response}
        ]
        
        # Удаляем сообщение "Думаю..." и отправляем ответ
        await thinking_message.delete()
        await message.answer(
            response,
            reply_markup=get_chatgpt_menu()
        )
    
    except Exception as e:
        # Удаляем сообщение "Думаю..." в случае ошибки
        try:
            await thinking_message.delete()
        except:
            pass
        
        # Логируем полную информацию об ошибке для отладки
        logger.error(f"Ошибка при обработке запроса к LLM: {e}", exc_info=True)
        
        # Формируем понятное сообщение об ошибке
        error_message = str(e)
        if "лимит" in error_message.lower() or "limit" in error_message.lower():
            # Если это ошибка лимита, сообщение уже содержит детали
            user_message = error_message
        else:
            # Для других ошибок показываем общее сообщение
            user_message = (
                f"❌ Произошла ошибка при обращении к AI.\n\n"
                f"Детали: {error_message}\n\n"
                "Попробуйте еще раз или вернитесь в главное меню."
            )
        
        await message.answer(
            user_message,
            reply_markup=get_chatgpt_menu()
        )
