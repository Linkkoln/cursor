"""Сервис для работы с LLM через OpenRouter.ai.

Этот сервис содержит бизнес-логику для общения с языковыми моделями.
Он не зависит от aiogram и Telegram, поэтому его легко тестировать.
"""
import logging
from typing import Optional, List, Dict
import aiohttp

# Создаём объект для записи логов (дневник)
logger = logging.getLogger(__name__)

# URL для API OpenRouter
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Модель по умолчанию (можно изменить на другую модель из OpenRouter)
DEFAULT_MODEL = "openai/gpt-3.5-turbo"


class LLMService:
    """Сервис для работы с языковыми моделями через OpenRouter.ai.
    
    Этот класс отправляет запросы к OpenRouter.ai и получает ответы от LLM.
    Он не знает о Telegram - это чистая бизнес-логика.
    """
    
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        """Инициализирует сервис LLM.
        
        Args:
            api_key: API ключ от OpenRouter.ai
            model: Название модели для использования (по умолчанию gpt-3.5-turbo)
        """
        self.api_key = api_key
        self.model = model
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Получает или создаёт сессию для HTTP-запросов.
        
        Returns:
            aiohttp.ClientSession: Сессия для работы с HTTP
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self) -> None:
        """Закрывает сессию HTTP-запросов."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_response(self, user_message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """Получает ответ от LLM на сообщение пользователя.
        
        Args:
            user_message: Сообщение пользователя
            conversation_history: История разговора (список сообщений)
                                Если None, создаётся новый разговор
        
        Returns:
            str: Ответ от LLM
            
        Raises:
            ValueError: Если API ключ не установлен
            Exception: Если произошла ошибка при запросе к API
        """
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY не установлен")
        
        # Подготавливаем историю разговора
        if conversation_history is None:
            messages = [{"role": "user", "content": user_message}]
        else:
            # Добавляем новое сообщение пользователя в историю
            messages = conversation_history + [{"role": "user", "content": user_message}]
        
        # Подготавливаем заголовки для запроса
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/your-repo",  # Опционально: укажите ваш репозиторий
            "X-Title": "Telegram Echo Bot"  # Опционально: название вашего приложения
        }
        
        # Подготавливаем данные для запроса
        data = {
            "model": self.model,
            "messages": messages
        }
        
        try:
            # Получаем сессию и отправляем запрос
            session = await self._get_session()
            
            async with session.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=30)  # Таймаут 30 секунд
            ) as response:
                # Проверяем статус ответа
                if response.status == 200:
                    # Парсим JSON ответ
                    result = await response.json()
                    
                    # Извлекаем текст ответа из структуры ответа OpenRouter
                    if "choices" in result and len(result["choices"]) > 0:
                        message_content = result["choices"][0]["message"]["content"]
                        return message_content
                    else:
                        logger.error(f"Неожиданная структура ответа от API: {result}")
                        return "Извините, не удалось получить ответ от AI."
                
                elif response.status == 401:
                    logger.error("Ошибка авторизации: неверный API ключ")
                    return "Ошибка: неверный API ключ OpenRouter. Проверьте настройки."
                
                elif response.status == 429:
                    logger.error("Превышен лимит запросов к API")
                    return "Извините, превышен лимит запросов. Попробуйте позже."
                
                else:
                    # Читаем текст ошибки
                    error_text = await response.text()
                    logger.error(f"Ошибка API (статус {response.status}): {error_text}")
                    return f"Ошибка при обращении к AI: статус {response.status}"
        
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети при запросе к OpenRouter: {e}")
            return "Ошибка сети при обращении к AI. Проверьте подключение к интернету."
        
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе к LLM: {e}")
            return "Произошла неожиданная ошибка при обращении к AI."
