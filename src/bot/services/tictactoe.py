"""Сервис для игры Крестики-нолики.

Этот сервис содержит всю логику игры:
- Хранение состояния игрового поля
- Проверка победы
- Ход компьютера (простой AI)

Игровое поле - это список из 9 элементов (3x3):
    0 | 1 | 2
    ---------
    3 | 4 | 5
    ---------
    6 | 7 | 8

Каждая клетка может быть:
- None - пустая
- "X" - крестик (игрок)
- "O" - нолик (бот)
"""
import random
from typing import Optional, List, Dict
from dataclasses import dataclass, field
from enum import Enum


class GameResult(Enum):
    """Результат игры."""
    IN_PROGRESS = "in_progress"  # Игра продолжается
    PLAYER_WIN = "player_win"    # Победил игрок
    BOT_WIN = "bot_win"          # Победил бот
    DRAW = "draw"                # Ничья


@dataclass
class TicTacToeGame:
    """Состояние одной игры в крестики-нолики.
    
    Attributes:
        board: Игровое поле (9 клеток)
        player_symbol: Символ игрока ("X" или "O")
        bot_symbol: Символ бота ("X" или "O")
    """
    board: List[Optional[str]] = field(default_factory=lambda: [None] * 9)
    player_symbol: str = "X"
    bot_symbol: str = "O"


class TicTacToeService:
    """Сервис для управления играми в крестики-нолики.
    
    Хранит активные игры пользователей и предоставляет методы для игры.
    """
    
    # Все возможные выигрышные комбинации (индексы клеток)
    # Это как "линии", по которым можно выиграть
    WINNING_COMBINATIONS = [
        [0, 1, 2],  # Верхняя горизонталь
        [3, 4, 5],  # Средняя горизонталь
        [6, 7, 8],  # Нижняя горизонталь
        [0, 3, 6],  # Левая вертикаль
        [1, 4, 7],  # Средняя вертикаль
        [2, 5, 8],  # Правая вертикаль
        [0, 4, 8],  # Диагональ \
        [2, 4, 6],  # Диагональ /
    ]
    
    def __init__(self):
        """Инициализирует сервис игр."""
        # Хранилище активных игр: ключ - ID пользователя
        self._games: Dict[int, TicTacToeGame] = {}
    
    def start_game(self, user_id: int) -> TicTacToeGame:
        """Начинает новую игру для пользователя.
        
        Args:
            user_id: ID пользователя в Telegram
            
        Returns:
            TicTacToeGame: Новая игра
        """
        game = TicTacToeGame()
        self._games[user_id] = game
        return game
    
    def get_game(self, user_id: int) -> Optional[TicTacToeGame]:
        """Получает активную игру пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[TicTacToeGame]: Игра или None, если нет активной игры
        """
        return self._games.get(user_id)
    
    def end_game(self, user_id: int) -> None:
        """Завершает игру пользователя.
        
        Args:
            user_id: ID пользователя
        """
        if user_id in self._games:
            del self._games[user_id]
    
    def make_player_move(self, user_id: int, cell: int) -> Optional[GameResult]:
        """Делает ход игрока.
        
        Args:
            user_id: ID пользователя
            cell: Номер клетки (0-8)
            
        Returns:
            Optional[GameResult]: Результат игры после хода, или None если ход невозможен
        """
        game = self.get_game(user_id)
        if not game:
            return None
        
        # Проверяем, что клетка свободна
        if game.board[cell] is not None:
            return None
        
        # Делаем ход игрока
        game.board[cell] = game.player_symbol
        
        # Проверяем результат игры
        return self._check_game_result(game)
    
    def make_bot_move(self, user_id: int) -> Optional[int]:
        """Делает ход бота (простой AI).
        
        AI использует следующую стратегию:
        1. Если можно выиграть - выигрывает
        2. Если игрок может выиграть следующим ходом - блокирует
        3. Занимает центр, если свободен
        4. Занимает случайную свободную клетку
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[int]: Номер клетки, куда сходил бот, или None если ход невозможен
        """
        game = self.get_game(user_id)
        if not game:
            return None
        
        # Получаем список свободных клеток
        empty_cells = [i for i, cell in enumerate(game.board) if cell is None]
        if not empty_cells:
            return None
        
        # Стратегия 1: Попробовать выиграть
        winning_move = self._find_winning_move(game, game.bot_symbol)
        if winning_move is not None:
            game.board[winning_move] = game.bot_symbol
            return winning_move
        
        # Стратегия 2: Блокировать победу игрока
        blocking_move = self._find_winning_move(game, game.player_symbol)
        if blocking_move is not None:
            game.board[blocking_move] = game.bot_symbol
            return blocking_move
        
        # Стратегия 3: Занять центр
        if game.board[4] is None:
            game.board[4] = game.bot_symbol
            return 4
        
        # Стратегия 4: Занять угол
        corners = [0, 2, 6, 8]
        empty_corners = [c for c in corners if game.board[c] is None]
        if empty_corners:
            move = random.choice(empty_corners)
            game.board[move] = game.bot_symbol
            return move
        
        # Стратегия 5: Занять любую свободную клетку
        move = random.choice(empty_cells)
        game.board[move] = game.bot_symbol
        return move
    
    def get_game_result(self, user_id: int) -> GameResult:
        """Получает текущий результат игры.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            GameResult: Результат игры
        """
        game = self.get_game(user_id)
        if not game:
            return GameResult.IN_PROGRESS
        return self._check_game_result(game)
    
    def _check_game_result(self, game: TicTacToeGame) -> GameResult:
        """Проверяет результат игры.
        
        Args:
            game: Состояние игры
            
        Returns:
            GameResult: Результат игры
        """
        # Проверяем, выиграл ли игрок
        if self._check_winner(game, game.player_symbol):
            return GameResult.PLAYER_WIN
        
        # Проверяем, выиграл ли бот
        if self._check_winner(game, game.bot_symbol):
            return GameResult.BOT_WIN
        
        # Проверяем ничью (все клетки заняты)
        if all(cell is not None for cell in game.board):
            return GameResult.DRAW
        
        # Игра продолжается
        return GameResult.IN_PROGRESS
    
    def _check_winner(self, game: TicTacToeGame, symbol: str) -> bool:
        """Проверяет, выиграл ли символ.
        
        Args:
            game: Состояние игры
            symbol: Символ для проверки ("X" или "O")
            
        Returns:
            bool: True, если символ выиграл
        """
        for combo in self.WINNING_COMBINATIONS:
            if all(game.board[i] == symbol for i in combo):
                return True
        return False
    
    def _find_winning_move(self, game: TicTacToeGame, symbol: str) -> Optional[int]:
        """Находит выигрышный ход для символа.
        
        Args:
            game: Состояние игры
            symbol: Символ для проверки
            
        Returns:
            Optional[int]: Номер клетки для победы, или None
        """
        for combo in self.WINNING_COMBINATIONS:
            cells = [game.board[i] for i in combo]
            # Если два символа из трёх и одна пустая клетка
            if cells.count(symbol) == 2 and cells.count(None) == 1:
                # Возвращаем индекс пустой клетки
                empty_index = cells.index(None)
                return combo[empty_index]
        return None
