import customtkinter as ctk
import requests
from PIL import Image, ImageTk
import base64
import io

class AccountScreen(ctk.CTkFrame):
    def __init__(self, master, on_back_click, login):
        super().__init__(master)

        self.on_back_click = on_back_click
        self.master = master  # Сохраняем ссылку на родительский виджет
        self.login = login

        # Изменяем размер окна
        self.master.geometry("600x400")

        # Заголовок
        title_label = ctk.CTkLabel(self, text="Аккаунт", font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        # Контейнер для данных пользователя
        user_data_frame = ctk.CTkFrame(self, border_width=2, border_color="gray")
        user_data_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Получаем данные пользователя с сервера
        try:
            response = requests.get(f"http://127.0.0.1:5000/search", params={"nickname": self.login})
            if response.status_code == 200:
                r_json = response.json()  # Данные пользователя
                results = r_json["results"]
                res = results[0]
                self.populate_user_data(user_data_frame, res)
            else:
                error_message = response.json().get("error", "Ошибка при получении данных")
                self.show_error_message(error_message)
        except Exception as e:
            self.show_error_message(f"Ошибка соединения")

        # Кнопка "Вернуться в меню"
        back_button = ctk.CTkButton(self, text="Вернуться в меню", command=self.return_to_main_menu)
        back_button.pack(pady=20)

    def populate_user_data(self, frame, user_data):
        """Заполняет данные пользователя"""
        # Извлекаем данные
        avatar_base64 = user_data.get("avatar", None)  # Base64 аватарки
        nickname = user_data.get("nickname", "Аноним")  # Никнейм игрока
        wins = user_data.get("wins", 0)  # Количество побед
        losses = user_data.get("losses", 0)  # Количество поражений
        winrate = user_data.get("win_rate", 0)  # Винрейт

        # Аватарка игрока
        if avatar_base64:
            try:
                image_data = base64.b64decode(avatar_base64)
                avatar_image = Image.open(io.BytesIO(image_data))
                avatar_image = avatar_image.resize((150, 150))
                avatar_photo = ImageTk.PhotoImage(avatar_image)

                avatar_label = ctk.CTkLabel(frame, image=avatar_photo, text="")
                avatar_label.image = avatar_photo
                avatar_label.grid(row=0, column=0, padx=20, pady=20)
            except Exception as e:
                avatar_label = ctk.CTkLabel(frame, text="Аватарка", width=150, height=150)
                avatar_label.grid(row=0, column=0, padx=20, pady=20)
        else:
            avatar_label = ctk.CTkLabel(frame, text="Аватарка", width=150, height=150)
            avatar_label.grid(row=0, column=0, padx=20, pady=20)

        # Информация об игроке
        info_label = ctk.CTkLabel(
            frame,
            text=f"Ник: {nickname}\nПобед: {wins}\nПоражений: {losses}\nВинрейт: {winrate:.2f}%",
            font=ctk.CTkFont(size=18),
            justify="left"
        )
        info_label.grid(row=0, column=1, padx=20, pady=20)

    def show_error_message(self, message):
        """Показывает сообщение об ошибке"""
        error_label = ctk.CTkLabel(self, text=message, text_color="red", font=ctk.CTkFont(size=16))
        error_label.pack(pady=20)

    def return_to_main_menu(self):
        """Возвращает пользователя в главное меню"""
        # Очищаем текущее окно
        self.destroy()

        # Вызываем коллбэк для возврата в главное меню
        self.on_back_click()