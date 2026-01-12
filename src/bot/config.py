"""Конфигурация приложения - настройки бота.

Представь, что бот - это робот, который хочет зайти в Telegram.
Токен - это как ключ от двери: без него робот не сможет войти.
Этот файл читает ключ из специального файла .env (как читать пароль из записной книжки).
"""
import os
from dotenv import load_dotenv

# Открываем файл .env и читаем из него настройки
# Это как открыть записную книжку и найти там пароль
load_dotenv()

# Ищем в файле .env строку BOT_TOKEN и читаем её значение
# Если такой строки нет, вернётся пустая строка (как будто ничего не нашли)
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

# Проверяем: а есть ли вообще токен?
# Если токена нет (пустая строка), то бот не сможет работать
# В этом случае останавливаем программу и показываем ошибку
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в переменных окружения")

# API ключ для OpenRouter (для режима ChatGPT)
# Это необязательный параметр - если его нет, режим ChatGPT не будет работать
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

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
DEFAULT_MODEL = FREE_MODELS[0] if FREE_MODELS else "meta-llama/llama-3.2-3b-instruct:free"

# URL для API OpenRouter
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Таймаут для запросов к OpenRouter (в секундах)
OPENROUTER_TIMEOUT = 60
