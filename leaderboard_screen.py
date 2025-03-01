import customtkinter as ctk
import requests
from PIL import Image, ImageTk
import base64
import io

class LeaderboardScreen(ctk.CTkFrame):
    def __init__(self, master, on_back_click):
        super().__init__(master)

        self.on_back_click = on_back_click
        self.master = master  # Сохраняем ссылку на родительский виджет

        # Заголовок таблицы лидеров
        title_label = ctk.CTkLabel(self, text="Таблица лидеров", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        # Создаем скроллируемую область
        scrollable_frame = ctk.CTkScrollableFrame(self, width=760, height=450)
        scrollable_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Получаем данные с сервера
        try:
            response = requests.get("http://127.0.0.1:5000/leaderboard")
            if response.status_code == 200:
                r_json = response.json()  # Данные о лидерах
                leaders = r_json.get("results", [])
                leaders.sort(key=lambda l: l["win_rate"], reverse=True)
                self.populate_leaderboard(scrollable_frame, leaders)
            else:
                error_message = response.json().get("message", "Ошибка при получении данных")
                self.show_error_message(error_message)
        except Exception as e:
            self.show_error_message(f"Ошибка соединения: {str(e)}")

        # Кнопка "Вернуться в меню"
        back_button = ctk.CTkButton(self, text="Вернуться в меню", command=self.return_to_main_menu)
        back_button.pack(pady=20)

    def populate_leaderboard(self, frame, leaders):
        """Заполняет таблицу лидеров данными"""
        for i, leader in enumerate(leaders):
            # Извлекаем данные
            avatar_base64 = leader.get("avatar", None)  # Base64 аватарки
            nickname = leader.get("nickname", "Аноним")  # Никнейм игрока
            wins = leader.get("wins", 0)  # Количество побед
            losses = leader.get("losses", 0)  # Количество поражений
            winrate = leader.get("win_rate", 0)  # Винрейт

            # Создаем фрейм для каждого игрока
            player_frame = ctk.CTkFrame(frame, border_width=1, border_color="gray")
            player_frame.pack(fill="x", pady=5, padx=10)

            # Аватарка игрока
            if avatar_base64:
                try:
                    # Декодируем Base64 в изображение
                    image_data = base64.b64decode(avatar_base64)
                    avatar_image = Image.open(io.BytesIO(image_data))
                    avatar_image = avatar_image.resize((50, 50))
                    avatar_photo = ImageTk.PhotoImage(avatar_image)

                    avatar_label = ctk.CTkLabel(player_frame, image=avatar_photo, text="")
                    avatar_label.image = avatar_photo  # Сохраняем ссылку на изображение
                    avatar_label.grid(row=0, column=0, padx=10, pady=5)
                except Exception as e:
                    avatar_label = ctk.CTkLabel(player_frame, text="Аватарка", width=50, height=50)
                    avatar_label.grid(row=0, column=0, padx=10, pady=5)
            else:
                avatar_label = ctk.CTkLabel(player_frame, text="Аватарка", width=50, height=50)
                avatar_label.grid(row=0, column=0, padx=10, pady=5)

            # Информация об игроке
            info_label = ctk.CTkLabel(
                player_frame,
                text=f"Ник: {nickname}\nПобед: {wins}\nПоражений: {losses}\nВинрейт: {winrate:.2f}%",
                font=ctk.CTkFont(size=14),
                justify="left"
            )
            info_label.grid(row=0, column=1, padx=10, pady=5)

    def show_error_message(self, message):
        """Показывает сообщение об ошибке"""
        error_label = ctk.CTkLabel(self, text=message, text_color="red", font=ctk.CTkFont(size=16))
        error_label.pack(pady=20)

    def return_to_main_menu(self):
        """Возвращает пользователя в главное меню"""
        # Скрываем текущий экран (не уничтожаем)
        # self.master.geometry("800x600")
        self.destroy()
        # Вызываем коллбэк для возврата в главное меню
        self.on_back_click()