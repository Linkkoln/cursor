"""Тесты для клавиатур бота.

Эти тесты проверяют, что клавиатуры создаются правильно.
"""
import pytest

import sys
from pathlib import Path

# Добавляем путь к src для импортов
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from bot.keyboards.common import get_main_menu, get_echo_menu


class TestKeyboards:
    """Тесты для клавиатур."""
    
    def test_get_main_menu_returns_keyboard(self):
        """Тест: главное меню возвращает клавиатуру.
        
        Проверяем, что функция get_main_menu() возвращает объект клавиатуры.
        """
        # Действие: получаем главное меню
        keyboard = get_main_menu()
        
        # Проверка: должен быть объект клавиатуры
        assert keyboard is not None
        assert hasattr(keyboard, 'keyboard')
        assert len(keyboard.keyboard) > 0
    
    def test_get_main_menu_has_buttons(self):
        """Тест: главное меню содержит кнопки.
        
        Проверяем, что в главном меню есть нужные кнопки.
        """
        # Действие: получаем главное меню
        keyboard = get_main_menu()
        
        # Проверка: должны быть кнопки
        assert len(keyboard.keyboard) >= 3  # Минимум 3 кнопки
        
        # Проверяем, что есть кнопка "Эхо"
        all_buttons = []
        for row in keyboard.keyboard:
            for button in row:
                all_buttons.append(button.text)
        
        assert "📝 Эхо" in all_buttons
        assert "ℹ️ Помощь" in all_buttons
        assert "🔄 Обновить меню" in all_buttons
    
    def test_get_echo_menu_returns_keyboard(self):
        """Тест: меню эхо-режима возвращает клавиатуру.
        
        Проверяем, что функция get_echo_menu() возвращает объект клавиатуры.
        """
        # Действие: получаем меню эхо-режима
        keyboard = get_echo_menu()
        
        # Проверка: должен быть объект клавиатуры
        assert keyboard is not None
        assert hasattr(keyboard, 'keyboard')
        assert len(keyboard.keyboard) > 0
    
    def test_get_echo_menu_has_back_button(self):
        """Тест: меню эхо-режима содержит кнопку "Назад".
        
        Проверяем, что в меню эхо-режима есть кнопка для возврата в главное меню.
        """
        # Действие: получаем меню эхо-режима
        keyboard = get_echo_menu()
        
        # Проверка: должна быть кнопка "Назад"
        all_buttons = []
        for row in keyboard.keyboard:
            for button in row:
                all_buttons.append(button.text)
        
        assert "⬅️ Назад в меню" in all_buttons
