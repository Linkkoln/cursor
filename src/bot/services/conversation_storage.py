"""Сервис для хранения истории разговоров.

Этот сервис отвечает за хранение и управление историей разговоров пользователей.
Он не зависит от Telegram и может быть легко заменён на базу данных.
"""
from typing import Dict, List, Optional


class ConversationStorage:
    """Хранилище истории разговоров пользователей.
    
    Этот класс управляет историей разговоров для каждого пользователя.
    В будущем можно заменить на базу данных без изменения интерфейса.
    """
    
    def __init__(self):
        """Инициализирует хранилище разговоров."""
        # Внутреннее хранилище: ключ - ID пользователя, значение - история разговора
        self._conversations: Dict[int, List[Dict[str, str]]] = {}
    
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
        """Очищает историю разговора для пользователя.
        
        Args:
            user_id: ID пользователя
        """
        if user_id in self._conversations:
            del self._conversations[user_id]
    
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
