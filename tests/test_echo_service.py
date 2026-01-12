"""Тесты для сервиса эхо-функциональности.

Эти тесты проверяют, что сервис правильно обрабатывает сообщения.
"""
import sys
from pathlib import Path
import pytest

# Добавляем путь к src для импортов
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from bot.services.echo import EchoService


class TestEchoService:
    """Тесты для класса EchoService."""
    
    def test_process_message_with_text(self):
        """Тест: обработка сообщения с текстом.
        
        Проверяем, что сервис возвращает тот же текст, который получил.
        """
        # Подготовка: создаём тестовое сообщение
        test_text = "Привет, бот!"
        
        # Действие: обрабатываем сообщение
        result = EchoService.process_message(test_text)
        
        # Проверка: результат должен быть равен исходному тексту
        assert result == test_text
    
    def test_process_message_with_empty_string(self):
        """Тест: обработка пустого сообщения.
        
        Проверяем, что сервис возвращает сообщение об ошибке для пустой строки.
        """
        # Подготовка: пустая строка
        test_text = ""
        
        # Действие: обрабатываем сообщение
        result = EchoService.process_message(test_text)
        
        # Проверка: должен вернуться текст об ошибке
        assert result == "Получено сообщение, но я могу повторять только текстовые сообщения."
    
    def test_process_message_with_whitespace_only(self):
        """Тест: обработка сообщения только с пробелами.
        
        Проверяем, что сервис считает сообщение с одними пробелами пустым.
        """
        # Подготовка: строка только с пробелами
        test_text = "   "
        
        # Действие: обрабатываем сообщение
        result = EchoService.process_message(test_text)
        
        # Проверка: должен вернуться текст об ошибке
        assert result == "Получено сообщение, но я могу повторять только текстовые сообщения."
    
    def test_process_message_with_none(self):
        """Тест: обработка сообщения без текста (None).
        
        Проверяем, что сервис правильно обрабатывает None.
        """
        # Подготовка: None вместо текста
        test_text = None
        
        # Действие: обрабатываем сообщение
        result = EchoService.process_message(test_text)
        
        # Проверка: должен вернуться текст об ошибке
        assert result == "Получено сообщение, но я могу повторять только текстовые сообщения."
    
    def test_is_text_message_with_text(self):
        """Тест: проверка текстового сообщения с текстом.
        
        Проверяем, что метод правильно определяет текстовое сообщение.
        """
        # Подготовка: сообщение с текстом
        test_text = "Привет!"
        
        # Действие: проверяем, является ли сообщение текстовым
        result = EchoService.is_text_message(test_text)
        
        # Проверка: должно быть True
        assert result is True
    
    def test_is_text_message_with_empty_string(self):
        """Тест: проверка пустого сообщения.
        
        Проверяем, что пустая строка не считается текстовым сообщением.
        """
        # Подготовка: пустая строка
        test_text = ""
        
        # Действие: проверяем, является ли сообщение текстовым
        result = EchoService.is_text_message(test_text)
        
        # Проверка: должно быть False
        assert result is False
    
    def test_is_text_message_with_whitespace(self):
        """Тест: проверка сообщения только с пробелами.
        
        Проверяем, что строка только с пробелами не считается текстовым сообщением.
        """
        # Подготовка: строка только с пробелами
        test_text = "   "
        
        # Действие: проверяем, является ли сообщение текстовым
        result = EchoService.is_text_message(test_text)
        
        # Проверка: должно быть False
        assert result is False
    
    def test_is_text_message_with_none(self):
        """Тест: проверка None как текстового сообщения.
        
        Проверяем, что None не считается текстовым сообщением.
        """
        # Подготовка: None
        test_text = None
        
        # Действие: проверяем, является ли сообщение текстовым
        result = EchoService.is_text_message(test_text)
        
        # Проверка: должно быть False
        assert result is False
