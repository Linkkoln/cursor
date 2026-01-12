"""Сервис для выбора и переключения моделей LLM.

Этот сервис отвечает за управление списком моделей и переключение между ними.
Он следует принципу Single Responsibility - только управление моделями.
"""
from typing import Optional, List
from bot.config import FREE_MODELS


class ModelSelector:
    """Сервис для выбора и переключения между моделями LLM.
    
    Этот класс управляет списком доступных моделей и переключением между ними.
    Он не знает о том, как делаются запросы к API - только управляет моделями.
    """
    
    def __init__(self, models: Optional[List[str]] = None):
        """Инициализирует селектор моделей.
        
        Args:
            models: Список моделей для использования. Если None, используется список из config.
        """
        self.models = models if models is not None else FREE_MODELS.copy()
        self.current_index = 0
    
    def get_current_model(self) -> str:
        """Получает текущую модель.
        
        Returns:
            str: Название текущей модели
        """
        return self.models[self.current_index]
    
    def get_next_model(self) -> Optional[str]:
        """Переключается на следующую модель в списке.
        
        Returns:
            Optional[str]: Следующая модель или None, если все модели исчерпаны
        """
        self.current_index += 1
        if self.current_index < len(self.models):
            return self.models[self.current_index]
        return None
    
    def reset_to_first(self) -> str:
        """Сбрасывает селектор на первую модель.
        
        Returns:
            str: Первая модель из списка
        """
        self.current_index = 0
        return self.models[0]
    
    def get_all_models(self) -> List[str]:
        """Получает список всех доступных моделей.
        
        Returns:
            List[str]: Список всех моделей
        """
        return self.models.copy()
    
    def has_more_models(self) -> bool:
        """Проверяет, есть ли ещё модели для переключения.
        
        Returns:
            bool: True, если есть ещё модели после текущей
        """
        return self.current_index + 1 < len(self.models)
