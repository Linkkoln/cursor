"""Клавиатуры для игры Крестики-нолики.

Игровое поле отображается как сетка 3x3 из inline кнопок.
Каждая кнопка показывает текущее состояние клетки:
- ⬜ (пустая клетка) - можно нажать
- ❌ (крестик) - уже занята игроком
- ⭕ (нолик) - уже занята ботом
"""
from typing import List, Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Символы для отображения на кнопках
CELL_SYMBOLS = {
    None: "⬜",  # Пустая клетка
    "X": "❌",   # Крестик (игрок)
    "O": "⭕",   # Нолик (бот)
}


def get_game_keyboard(board: List[Optional[str]], game_over: bool = False) -> InlineKeyboardMarkup:
    """Создаёт игровое поле в виде inline клавиатуры.
    
    Args:
        board: Список из 9 элементов (состояние поля)
        game_over: Если True, кнопки будут неактивными
        
    Returns:
        InlineKeyboardMarkup: Игровое поле с кнопками
    """
    builder = InlineKeyboardBuilder()
    
    # Создаём 9 кнопок (3 ряда по 3 кнопки)
    for i, cell in enumerate(board):
        # Получаем символ для отображения
        symbol = CELL_SYMBOLS.get(cell, "⬜")
        
        # Если игра окончена или клетка занята - кнопка неактивна
        # callback_data "noop" означает "ничего не делать"
        if game_over or cell is not None:
            callback_data = "ttt:noop"
        else:
            callback_data = f"ttt:move:{i}"
        
        builder.add(InlineKeyboardButton(
            text=symbol,
            callback_data=callback_data
        ))
    
    # Располагаем кнопки 3x3
    builder.adjust(3, 3, 3)
    
    return builder.as_markup()


def get_game_over_keyboard(board: List[Optional[str]]) -> InlineKeyboardMarkup:
    """Создаёт клавиатуру после окончания игры.
    
    Показывает финальное состояние поля и кнопки управления.
    
    Args:
        board: Финальное состояние поля
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с полем и кнопками
    """
    builder = InlineKeyboardBuilder()
    
    # Создаём игровое поле (неактивное)
    for cell in board:
        symbol = CELL_SYMBOLS.get(cell, "⬜")
        builder.add(InlineKeyboardButton(
            text=symbol,
            callback_data="ttt:noop"
        ))
    
    # Добавляем кнопки управления
    builder.add(InlineKeyboardButton(
        text="🔄 Играть снова",
        callback_data="ttt:restart"
    ))
    builder.add(InlineKeyboardButton(
        text="🏠 В меню",
        callback_data="ttt:menu"
    ))
    
    # Располагаем: 3x3 поле, затем 2 кнопки в ряд
    builder.adjust(3, 3, 3, 2)
    
    return builder.as_markup()


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Создаёт клавиатуру для начала игры.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой начала игры
    """
    builder = InlineKeyboardBuilder()
    
    builder.add(InlineKeyboardButton(
        text="🎮 Начать игру",
        callback_data="ttt:start"
    ))
    builder.add(InlineKeyboardButton(
        text="🏠 В меню",
        callback_data="ttt:menu"
    ))
    
    builder.adjust(1, 1)
    
    return builder.as_markup()
