"""Сервис для хранения истории разговоров.

Этот сервис отвечает за хранение и управление историей разговоров пользователей.
Он не зависит от Telegram и может быть легко заменён на базу данных.
"""
from typing import Dict, List, Optional
from enum import Enum


class ChatMode(Enum):
    """Режимы работы ChatGPT.
    
    Каждый режим определяет, как бот будет отвечать на сообщения пользователя.
    """
    ASSISTANT = "assistant"  # Обычный режим - бот отвечает как ассистент
    ASCII_ART = "ascii_art"  # ASCII-арт режим - бот рисует картинки символами
    TRANSLATOR = "translator"  # Режим перевода - переводит с русского на английский


class ConversationStorage:
    """Хранилище истории разговоров пользователей.
    
    Этот класс управляет историей разговоров для каждого пользователя.
    В будущем можно заменить на базу данных без изменения интерфейса.
    """
    
    def __init__(self):
        """Инициализирует хранилище разговоров."""
        # Внутреннее хранилище: ключ - ID пользователя, значение - история разговора
        self._conversations: Dict[int, List[Dict[str, str]]] = {}
        # Хранилище режимов работы: ключ - ID пользователя, значение - режим ChatGPT
        self._modes: Dict[int, ChatMode] = {}
    
    def get_history(self, user_id: int) -> List[Dict[str, str]]:
        """Получает историю разговора для пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            List[Dict[str, str]]: История разговора (список сообщений)
        """
        return self._conversations.get(user_id, [])
    
    def add_message(self, user_id: int, role: str, content: str) -> None:
        """Добавляет сообщение в историю разговора.
        
        Args:
            user_id: ID пользователя
            role: Роль отправителя ("user" или "assistant")
            content: Содержимое сообщения
        """
        if user_id not in self._conversations:
            self._conversations[user_id] = []
        
        self._conversations[user_id].append({
            "role": role,
            "content": content
        })
    
    def clear_history(self, user_id: int) -> None:
        """Очищает историю разговора и режим работы для пользователя.
        
        Args:
            user_id: ID пользователя
        """
        if user_id in self._conversations:
            del self._conversations[user_id]
        # Также очищаем режим работы при выходе из ChatGPT
        self.clear_mode(user_id)
    
    def has_conversation(self, user_id: int) -> bool:
        """Проверяет, есть ли активный разговор у пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            bool: True, если у пользователя есть активный разговор
        """
        return user_id in self._conversations
    
    def update_history(self, user_id: int, history: List[Dict[str, str]]) -> None:
        """Обновляет всю историю разговора для пользователя.
        
        Args:
            user_id: ID пользователя
            history: Новая история разговора
        """
        self._conversations[user_id] = history
    
    def get_mode(self, user_id: int) -> Optional[ChatMode]:
        """Получает текущий режим работы ChatGPT для пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[ChatMode]: Режим работы или None, если не установлен
        """
        return self._modes.get(user_id)
    
    def set_mode(self, user_id: int, mode: ChatMode) -> None:
        """Устанавливает режим работы ChatGPT для пользователя.
        
        Args:
            user_id: ID пользователя
            mode: Режим работы ChatGPT
        """
        self._modes[user_id] = mode
    
    def clear_mode(self, user_id: int) -> None:
        """Очищает режим работы для пользователя.
        
        Args:
            user_id: ID пользователя
        """
        if user_id in self._modes:
            del self._modes[user_id]
