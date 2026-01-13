"""Сервис для генерации QR-кодов.

QR-код (Quick Response Code) - это двумерный штрих-код,
который можно отсканировать камерой телефона.

Этот сервис создаёт QR-коды из текста или ссылок.
"""
import io
import qrcode
from qrcode.constants import ERROR_CORRECT_M


class QRCodeService:
    """Сервис для генерации QR-кодов.
    
    Использует библиотеку qrcode для создания изображений QR-кодов.
    """
    
    # Максимальная длина текста для QR-кода
    # Больше текста = больше точек в QR-коде = сложнее сканировать
    MAX_TEXT_LENGTH = 2000
    
    def generate_qrcode(self, text: str) -> io.BytesIO:
        """Генерирует QR-код из текста.
        
        Args:
            text: Текст или ссылка для кодирования
            
        Returns:
            io.BytesIO: Изображение QR-кода в формате PNG
            
        Raises:
            ValueError: Если текст пустой или слишком длинный
        """
        # Проверяем входные данные
        if not text or not text.strip():
            raise ValueError("Текст не может быть пустым")
        
        if len(text) > self.MAX_TEXT_LENGTH:
            raise ValueError(
                f"Текст слишком длинный. "
                f"Максимум {self.MAX_TEXT_LENGTH} символов, "
                f"у вас {len(text)}"
            )
        
        # Создаём QR-код
        # version=None - автоматически выбирает размер
        # error_correction - уровень коррекции ошибок (M = 15%)
        # box_size - размер одного квадратика в пикселях
        # border - размер белой рамки вокруг QR-кода
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        
        # Добавляем данные и создаём QR-код
        qr.add_data(text)
        qr.make(fit=True)
        
        # Создаём изображение
        # fill_color - цвет точек (чёрный)
        # back_color - цвет фона (белый)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Сохраняем изображение в байтовый поток
        # Это как сохранить картинку в файл, но в памяти
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)  # Перематываем в начало, чтобы можно было прочитать
        
        return buffer
    
    def is_valid_url(self, text: str) -> bool:
        """Проверяет, является ли текст URL-адресом.
        
        Args:
            text: Текст для проверки
            
        Returns:
            bool: True, если это URL
        """
        text = text.strip().lower()
        return text.startswith(("http://", "https://", "www."))
