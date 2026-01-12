"""Тесты для сервиса сообщений.

Эти тесты проверяют, что сервис правильно возвращает тексты сообщений.
"""
import pytest

import sys
from pathlib import Path

# Добавляем путь к src для импортов
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from bot.services.message import MessageService


class TestMessageService:
    """Тесты для класса MessageService."""
    
    def test_get_welcome_message(self):
        """Тест: получение приветственного сообщения.
        
        Проверяем, что метод возвращает непустое приветственное сообщение.
        """
        # Действие: получаем приветственное сообщение
        message = MessageService.get_welcome_message()
        
        # Проверка: сообщение не должно быть пустым
        assert message is not None
        assert len(message) > 0
        assert "Привет" in message or "эхо-бот" in message
    
    def test_get_help_message(self):
        """Тест: получение справки.
        
        Проверяем, что метод возвращает непустое сообщение со справкой.
        """
        # Действие: получаем справку
        message = MessageService.get_help_message()
        
        # Проверка: сообщение не должно быть пустым
        assert message is not None
        assert len(message) > 0
        assert "Справка" in message or "помощь" in message.lower()
    
    def test_get_echo_mode_message(self):
        """Тест: получение сообщения об эхо-режиме.
        
        Проверяем, что метод возвращает сообщение об эхо-режиме.
        """
        # Действие: получаем сообщение об эхо-режиме
        message = MessageService.get_echo_mode_message()
        
        # Проверка: сообщение не должно быть пустым
        assert message is not None
        assert len(message) > 0
        assert "Эхо" in message or "эхо" in message.lower()
    
    def test_get_back_to_menu_message(self):
        """Тест: получение сообщения о возврате в меню.
        
        Проверяем, что метод возвращает сообщение о возврате в меню.
        """
        # Действие: получаем сообщение о возврате в меню
        message = MessageService.get_back_to_menu_message()
        
        # Проверка: сообщение не должно быть пустым
        assert message is not None
        assert len(message) > 0
        assert "меню" in message.lower()
    
    def test_get_menu_refreshed_message(self):
        """Тест: получение сообщения об обновлении меню.
        
        Проверяем, что метод возвращает сообщение об обновлении меню.
        """
        # Действие: получаем сообщение об обновлении меню
        message = MessageService.get_menu_refreshed_message()
        
        # Проверка: сообщение не должно быть пустым
        assert message is not None
        assert len(message) > 0
        assert "меню" in message.lower() or "обновлено" in message.lower()
