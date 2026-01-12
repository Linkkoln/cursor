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
    
    def test_process_message_with_integer(self):
        """Тест: обработка целого числа.
        
        Проверяем, что если пользователь отправил целое число,
        бот возвращает это число + 1.
        """
        # Подготовка: целое число
        test_text = "5"
        
        # Действие: обрабатываем сообщение
        result = EchoService.process_message(test_text)
        
        # Проверка: результат должен быть число + 1
        assert result == "6"
    
    def test_process_message_with_negative_integer(self):
        """Тест: обработка отрицательного целого числа.
        
        Проверяем, что отрицательные числа тоже обрабатываются правильно.
        """
        # Подготовка: отрицательное целое число
        test_text = "-10"
        
        # Действие: обрабатываем сообщение
        result = EchoService.process_message(test_text)
        
        # Проверка: результат должен быть число + 1
        assert result == "-9"
    
    def test_process_message_with_zero(self):
        """Тест: обработка нуля.
        
        Проверяем, что ноль обрабатывается правильно.
        """
        # Подготовка: ноль
        test_text = "0"
        
        # Действие: обрабатываем сообщение
        result = EchoService.process_message(test_text)
        
        # Проверка: результат должен быть 1
        assert result == "1"
    
    def test_process_message_with_float(self):
        """Тест: обработка дробного числа.
        
        Проверяем, что дробные числа тоже обрабатываются правильно.
        """
        # Подготовка: дробное число
        test_text = "3.5"
        
        # Действие: обрабатываем сообщение
        result = EchoService.process_message(test_text)
        
        # Проверка: результат должен быть число + 1
        assert result == "4.5"
    
    def test_process_message_with_float_with_spaces(self):
        """Тест: обработка дробного числа с пробелами.
        
        Проверяем, что пробелы вокруг числа игнорируются.
        """
        # Подготовка: дробное число с пробелами
        test_text = "  2.7  "
        
        # Действие: обрабатываем сообщение
        result = EchoService.process_message(test_text)
        
        # Проверка: результат должен быть число + 1
        assert result == "3.7"
    
    def test_process_message_with_text_not_number(self):
        """Тест: обработка текста, который не является числом.
        
        Проверяем, что обычный текст возвращается как есть (эхо).
        """
        # Подготовка: текст, который не число
        test_text = "Привет, бот!"
        
        # Действие: обрабатываем сообщение
        result = EchoService.process_message(test_text)
        
        # Проверка: результат должен быть тот же текст (эхо)
        assert result == test_text
    
    def test_process_message_with_text_containing_number(self):
        """Тест: обработка текста, содержащего число.
        
        Проверяем, что текст с числом внутри не считается числом.
        """
        # Подготовка: текст с числом внутри
        test_text = "Мне 25 лет"
        
        # Действие: обрабатываем сообщение
        result = EchoService.process_message(test_text)
        
        # Проверка: результат должен быть тот же текст (эхо)
        assert result == test_text
