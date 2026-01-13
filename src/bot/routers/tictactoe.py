"""Роутер для игры Крестики-нолики.

Команда /tictactoe запускает игру против бота.
Игрок ходит первым (X), бот ходит вторым (O).

ВНИМАНИЕ: Этот файл нельзя запускать напрямую!
Запускайте бота командой: python -m src.bot
"""
import logging
import sys
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

# Защита от прямого запуска файла
if __name__ == "__main__":
    print("❌ Ошибка: Этот файл нельзя запускать напрямую!")
    print("✅ Правильный способ запуска бота:")
    print("   python -m src.bot")
    sys.exit(1)

from bot.keyboards.common import get_main_menu
from bot.keyboards.tictactoe import (
    get_game_keyboard, 
    get_game_over_keyboard,
    get_start_keyboard
)
from bot.services.tictactoe import TicTacToeService, GameResult

# Создаём логгер
logger = logging.getLogger(__name__)

# Создаём роутер для игры
tictactoe_router = Router()

# Создаём сервис игры (хранит состояния всех игр)
game_service = TicTacToeService()

# Сообщения для разных результатов игры
RESULT_MESSAGES = {
    GameResult.PLAYER_WIN: "🎉 Поздравляем! Вы победили!",
    GameResult.BOT_WIN: "🤖 Бот победил! Попробуйте ещё раз!",
    GameResult.DRAW: "🤝 Ничья! Отличная игра!",
}


@tictactoe_router.message(Command("tictactoe"))
async def cmd_tictactoe(message: Message) -> None:
    """Обработчик команды /tictactoe - запуск игры.
    
    Показывает приветственное сообщение и кнопку начала игры.
    """
    await message.answer(
        "🎮 <b>Крестики-нолики</b>\n\n"
        "Классическая игра против бота!\n\n"
        "Вы играете за ❌ (крестики)\n"
        "Бот играет за ⭕ (нолики)\n\n"
        "Нажмите кнопку, чтобы начать:",
        reply_markup=get_start_keyboard()
    )


@tictactoe_router.message(lambda message: message.text == "🎮 Крестики-нолики")
async def cmd_tictactoe_button(message: Message) -> None:
    """Обработчик кнопки "Крестики-нолики" в меню."""
    await cmd_tictactoe(message)


@tictactoe_router.callback_query(F.data == "ttt:start")
async def callback_start_game(callback: CallbackQuery) -> None:
    """Обработчик нажатия кнопки "Начать игру".
    
    Создаёт новую игру и показывает пустое поле.
    """
    user_id = callback.from_user.id
    
    # Начинаем новую игру
    game = game_service.start_game(user_id)
    
    # Обновляем сообщение с игровым полем
    await callback.message.edit_text(
        "🎮 <b>Крестики-нолики</b>\n\n"
        "Ваш ход! Нажмите на пустую клетку (⬜):",
        reply_markup=get_game_keyboard(game.board)
    )
    
    await callback.answer("Игра началась! Ваш ход.")


@tictactoe_router.callback_query(F.data == "ttt:restart")
async def callback_restart_game(callback: CallbackQuery) -> None:
    """Обработчик нажатия кнопки "Играть снова"."""
    await callback_start_game(callback)


@tictactoe_router.callback_query(F.data == "ttt:menu")
async def callback_back_to_menu(callback: CallbackQuery) -> None:
    """Обработчик нажатия кнопки "В меню".
    
    Завершает игру и возвращает в главное меню.
    """
    user_id = callback.from_user.id
    
    # Завершаем игру
    game_service.end_game(user_id)
    
    # Удаляем сообщение с игрой
    await callback.message.delete()
    
    # Отправляем сообщение о возврате в меню
    await callback.message.answer(
        "🏠 Вы вернулись в главное меню!",
        reply_markup=get_main_menu()
    )
    
    await callback.answer()


@tictactoe_router.callback_query(F.data == "ttt:noop")
async def callback_noop(callback: CallbackQuery) -> None:
    """Обработчик нажатия на занятую клетку.
    
    Просто показывает уведомление, что клетка занята.
    """
    await callback.answer("Эта клетка уже занята!")


@tictactoe_router.callback_query(F.data.startswith("ttt:move:"))
async def callback_player_move(callback: CallbackQuery) -> None:
    """Обработчик хода игрока.
    
    Когда игрок нажимает на пустую клетку:
    1. Делаем ход игрока
    2. Проверяем результат
    3. Если игра продолжается - делаем ход бота
    4. Снова проверяем результат
    5. Обновляем игровое поле
    """
    user_id = callback.from_user.id
    
    # Извлекаем номер клетки из callback_data
    # Формат: "ttt:move:5" -> cell = 5
    try:
        cell = int(callback.data.split(":")[2])
    except (IndexError, ValueError):
        await callback.answer("Ошибка: неверный ход")
        return
    
    # Проверяем, есть ли активная игра
    game = game_service.get_game(user_id)
    if not game:
        await callback.answer("Игра не найдена. Начните новую игру.")
        return
    
    # Делаем ход игрока
    result = game_service.make_player_move(user_id, cell)
    if result is None:
        await callback.answer("Невозможный ход!")
        return
    
    # Проверяем, закончилась ли игра после хода игрока
    if result != GameResult.IN_PROGRESS:
        await _show_game_result(callback, game.board, result)
        return
    
    # Делаем ход бота
    bot_move = game_service.make_bot_move(user_id)
    
    # Проверяем результат после хода бота
    result = game_service.get_game_result(user_id)
    
    if result != GameResult.IN_PROGRESS:
        await _show_game_result(callback, game.board, result)
        return
    
    # Игра продолжается - обновляем поле
    await callback.message.edit_text(
        "🎮 <b>Крестики-нолики</b>\n\n"
        "Ваш ход! Нажмите на пустую клетку (⬜):",
        reply_markup=get_game_keyboard(game.board)
    )
    
    await callback.answer()


async def _show_game_result(callback: CallbackQuery, board: list, result: GameResult) -> None:
    """Показывает результат игры.
    
    Args:
        callback: Callback query от Telegram
        board: Финальное состояние поля
        result: Результат игры
    """
    # Получаем сообщение для результата
    result_message = RESULT_MESSAGES.get(result, "Игра окончена!")
    
    # Завершаем игру
    game_service.end_game(callback.from_user.id)
    
    # Обновляем сообщение с финальным полем
    await callback.message.edit_text(
        f"🎮 <b>Крестики-нолики</b>\n\n"
        f"{result_message}",
        reply_markup=get_game_over_keyboard(board)
    )
    
    await callback.answer(result_message)
