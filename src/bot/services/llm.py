"""Сервис для работы с LLM через OpenRouter.ai.

Этот сервис содержит бизнес-логику для общения с языковыми моделями.
Он не зависит от aiogram и Telegram, поэтому его легко тестировать.
"""
import logging
import asyncio
from typing import Optional, List, Dict
import aiohttp

# Создаём объект для записи логов (дневник)
logger = logging.getLogger(__name__)

# URL для API OpenRouter
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Список бесплатных моделей для использования (fallback при превышении лимита)
# Вариант :free означает бесплатную модель с низкими лимитами запросов
# Модели перечислены в порядке приоритета использования
FREE_MODELS = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "deepseek/deepseek-chat:free",
    "google/gemma-2-2b-it:free",
    "qwen/qwen-2-7b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
]

# Модель по умолчанию (первая из списка бесплатных)
DEFAULT_MODEL = FREE_MODELS[0]


class LLMService:
    """Сервис для работы с языковыми моделями через OpenRouter.ai.
    
    Этот класс отправляет запросы к OpenRouter.ai и получает ответы от LLM.
    Он не знает о Telegram - это чистая бизнес-логика.
    """
    
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        """Инициализирует сервис LLM.
        
        Args:
            api_key: API ключ от OpenRouter.ai
            model: Название модели для использования (по умолчанию первая бесплатная)
        """
        self.api_key = api_key
        self.model = model
        # Определяем индекс текущей модели в списке бесплатных
        try:
            self.current_model_index = FREE_MODELS.index(model) if model in FREE_MODELS else 0
        except ValueError:
            self.current_model_index = 0
            self.model = FREE_MODELS[0]
        self.session: Optional[aiohttp.ClientSession] = None
    
    def _get_next_model(self) -> Optional[str]:
        """Получает следующую доступную модель из списка бесплатных.
        
        Returns:
            Optional[str]: Следующая модель или None, если все модели исчерпаны
        """
        self.current_model_index += 1
        if self.current_model_index < len(FREE_MODELS):
            return FREE_MODELS[self.current_model_index]
        return None
    
    def _reset_to_first_model(self) -> str:
        """Сбрасывает индекс модели на первую в списке.
        
        Returns:
            str: Первая модель из списка
        """
        self.current_model_index = 0
        self.model = FREE_MODELS[0]
        return self.model
    
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
        
        При превышении лимита запросов (429) автоматически переключается на следующую бесплатную модель.
        
        Args:
            user_message: Сообщение пользователя
            conversation_history: История разговора (список сообщений)
                                Если None, создаётся новый разговор
        
        Returns:
            str: Ответ от LLM
            
        Raises:
            ValueError: Если API ключ не установлен
            Exception: Если произошла ошибка при запросе к API и все модели исчерпаны
        """
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY не установлен")
        
        # Подготавливаем историю разговора
        if conversation_history is None:
            messages = [{"role": "user", "content": user_message}]
        else:
            # Добавляем новое сообщение пользователя в историю
            messages = conversation_history + [{"role": "user", "content": user_message}]
        
        # Пробуем запросить ответ, при ошибке 429 переключаемся на другую модель
        max_attempts = len(FREE_MODELS)
        attempt = 0
        
        while attempt < max_attempts:
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
                attempt += 1
                result = await self._make_request(headers, data)
                
                # Если запрос успешен, возвращаем результат и сбрасываем индекс модели
                # Это позволяет при следующем запросе начать с первой модели
                if result is not None and not result.startswith("⏱") and not result.startswith("❌"):
                    # Сбрасываем индекс на первую модель для следующего запроса
                    self._reset_to_first_model()
                    return result
                
                # Если результат None, значит была ошибка 429, пробуем следующую модель
                next_model = self._get_next_model()
                if next_model:
                    logger.info(f"Переключаемся на модель: {next_model}")
                    self.model = next_model
                    continue
                else:
                    # Все модели исчерпаны
                    return (
                        "⏱ Превышен лимит запросов для всех доступных бесплатных моделей.\n\n"
                        "Попробуйте позже или пополните баланс на https://openrouter.ai/"
                    )
            
            except Exception as e:
                # Если это не ошибка 429, пробрасываем дальше
                if "429" not in str(e) and "лимит" not in str(e).lower():
                    raise
                
                # Ошибка 429 - пробуем следующую модель
                next_model = self._get_next_model()
                if next_model:
                    logger.info(f"Переключаемся на модель: {next_model} из-за лимита")
                    self.model = next_model
                    continue
                else:
                    # Все модели исчерпаны
                    return (
                        "⏱ Превышен лимит запросов для всех доступных бесплатных моделей.\n\n"
                        "Попробуйте позже или пополните баланс на https://openrouter.ai/"
                    )
        
        # Если дошли сюда, все попытки исчерпаны
        return (
            "⏱ Превышен лимит запросов для всех доступных бесплатных моделей.\n\n"
            "Попробуйте позже или пополните баланс на https://openrouter.ai/"
        )
    
    async def _make_request(self, headers: Dict[str, str], data: Dict) -> Optional[str]:
        """Выполняет HTTP-запрос к OpenRouter API.
        
        Args:
            headers: Заголовки HTTP-запроса
            data: Данные для отправки
            
        Returns:
            Optional[str]: Ответ от LLM или None, если была ошибка 429
        """
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
                    # Превышен лимит запросов (rate limit) - возвращаем None для переключения модели
                    retry_after = response.headers.get("Retry-After", None)
                    rate_limit_info = {
                        "retry_after": retry_after,
                        "status": response.status,
                        "current_model": self.model
                    }
                    
                    # Пытаемся прочитать детали ошибки из тела ответа
                    try:
                        error_data = await response.json()
                        if "error" in error_data:
                            error_message = error_data["error"].get("message", "")
                            rate_limit_info["error_message"] = error_message
                            logger.warning(
                                f"Превышен лимит для модели {self.model}: {error_message}. Переключаемся на следующую.",
                                extra=rate_limit_info
                            )
                        else:
                            logger.warning(
                                f"Превышен лимит для модели {self.model}. Переключаемся на следующую.",
                                extra=rate_limit_info
                            )
                    except:
                        logger.warning(
                            f"Превышен лимит для модели {self.model}. Переключаемся на следующую.",
                            extra=rate_limit_info
                        )
                    
                    # Возвращаем None, чтобы вызвающий код переключился на следующую модель
                    return None
                
                else:
                    # Читаем текст ошибки для детальной информации
                    try:
                        error_text = await response.text()
                        
                        # Пытаемся распарсить JSON с ошибкой
                        error_json = None
                        if response.content_type == 'application/json':
                            try:
                                error_json = await response.json()
                            except:
                                pass
                        
                        # Логируем полную информацию об ошибке
                        if error_json and "error" in error_json:
                            error_message = error_json["error"].get("message", "Неизвестная ошибка")
                            error_type = error_json["error"].get("type", "unknown")
                            logger.error(
                                f"Ошибка API OpenRouter (статус {response.status}, тип: {error_type}): {error_message}",
                                extra={"status": response.status, "error_json": error_json}
                            )
                            return f"Ошибка при обращении к AI: {error_message}"
                        else:
                            logger.error(
                                f"Ошибка API OpenRouter (статус {response.status}): {error_text}",
                                extra={"status": response.status}
                            )
                            return f"Ошибка при обращении к AI: статус {response.status}"
                    except Exception as parse_error:
                        logger.error(f"Не удалось прочитать ошибку от API: {parse_error}", exc_info=True)
                        return f"Ошибка при обращении к AI: статус {response.status}"
        
        except aiohttp.ClientError as e:
            # Ошибка сети (нет интернета, таймаут и т.д.)
            logger.error(f"Ошибка сети при запросе к OpenRouter: {e}", exc_info=True)
            return "Ошибка сети при обращении к AI. Проверьте подключение к интернету."
        
        except asyncio.TimeoutError as e:
            # Превышен таймаут запроса
            logger.error(f"Таймаут при запросе к OpenRouter: {e}", exc_info=True)
            return "Превышено время ожидания ответа от AI. Попробуйте позже."
        
        except Exception as e:
            # Любая другая неожиданная ошибка
            # exc_info=True выводит полный traceback для отладки
            logger.error(f"Неожиданная ошибка при запросе к LLM: {e}", exc_info=True)
            return f"Произошла ошибка при обращении к AI: {str(e)}"
