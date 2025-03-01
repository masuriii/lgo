import customtkinter as ctk

from account_screen import AccountScreen
from game_screen import GameScreen
from leaderboard_screen import LeaderboardScreen


class MainMenu(ctk.CTkFrame):
    def __init__(self, master, on_logout_click):
        super().__init__(master)

        self.on_logout_click = on_logout_click
        self.master = master  # Сохраняем ссылку на родительский виджет
        self.master.title('Ai КМН')
        # Устанавливаем начальный размер окна
        self.set_window_size(400, 300)

        # Заголовок
        label = ctk.CTkLabel(self, text="Главное меню", font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=12, padx=10)

        # Кнопка "Играть"
        play_button = ctk.CTkButton(self, text="Играть", command=self.start_game)
        play_button.pack(pady=12, padx=10)

        # Кнопка "Таблица лидеров"
        leaderboard_button = ctk.CTkButton(self, text="Таблица лидеров", command=self.show_leaderboard)
        leaderboard_button.pack(pady=12, padx=10)

        # Кнопка "Аккаунт"
        account_button = ctk.CTkButton(self, text="Аккаунт", command=self.show_account)
        account_button.pack(pady=12, padx=10)

        # Кнопка "Выйти из аккаунта"
        logout_button = ctk.CTkButton(self, text="Выйти из аккаунта", command=self.on_logout_click)
        logout_button.pack(pady=12, padx=10)

    def show_account(self):
        """Обработка нажатия кнопки 'Аккаунт'"""
        self.pack_forget()
        account_screen = AccountScreen(self.master, self.return_to_main_menu, self.master.login)
        account_screen.pack(fill="both", expand=True)
    def set_window_size(self, width, height):
        """Устанавливает размер окна"""
        self.master.geometry(f"{width}x{height}")

    def start_game(self):
        """Начинает игру и показывает экран выбора камеры"""
        self.pack_forget()
        self.set_window_size(800, 600)
        game_screen = GameScreen(self.master, self.return_to_main_menu)
        game_screen.pack(pady=20, padx=20, fill="both", expand=True)

    def return_to_main_menu(self):
        """Возвращает пользователя в главное меню"""
        # Скрываем или уничтожаем текущий экран (например, GameScreen)
        # for widget in self.master.winfo_children():
        #     if isinstance(widget, GameScreen):
        #         widget.destroy()  # Уничтожаем экран игры


        self.set_window_size(400, 300)
        self.pack(pady=20, padx=20, fill="both", expand=True)

    def show_leaderboard(self):
        """Обработка нажатия кнопки 'Таблица лидеров'"""
        # Скрываем текущий экран
        self.pack_forget()
        # Создаем экран таблицы лидеров
        # self.master.geometry("800x600")
        self.set_window_size(800, 700)
        leaderboard_screen = LeaderboardScreen(self.master, self.return_to_main_menu)
        leaderboard_screen.pack(fill="both", expand=True)