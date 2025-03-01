import customtkinter as ctk
import requests

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_login_success, on_registration_click):
        super().__init__(master)

        self.on_login_success = on_login_success
        self.on_registration_click = on_registration_click

        # Заголовок
        label = ctk.CTkLabel(self, text="Вход в аккаунт", font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=12, padx=10)

        # Поле логина
        self.login_entry = ctk.CTkEntry(self, placeholder_text="Логин")
        self.login_entry.pack(pady=6, padx=10)

        # Поле пароля
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Пароль", show="*")
        self.password_entry.pack(pady=6, padx=10)

        # Кнопка входа
        login_button = ctk.CTkButton(self, text="Войти", command=self.login)
        login_button.pack(pady=12, padx=10)

        # Кнопка регистрации
        registration_button = ctk.CTkButton(self, text="Зарегистрироваться", command=self.on_registration_click)
        registration_button.pack(pady=12, padx=10)

    def clear_password(self):
        """Очищает поле пароля"""
        self.password_entry.delete(0, ctk.END)

    def show_error_window(self, message):
        """Показывает окно с сообщением об ошибке"""
        # Создаем новое окно ошибки
        error_window = ctk.CTkToplevel(self)  # Указываем self (родительский виджет)
        error_window.title("Ошибка")
        error_window.geometry("300x100")

        # Делаем окно модальным
        error_window.grab_set()  # Захватываем фокус
        error_window.focus_force()  # Принудительно переключаем фокус на это окно

        # Метка с текстом ошибки
        error_label = ctk.CTkLabel(error_window, text=message, text_color="red", wraplength=250)
        error_label.pack(pady=10, padx=10)

        # Кнопка закрытия окна
        ok_button = ctk.CTkButton(error_window, text="OK", command=error_window.destroy)
        ok_button.pack(pady=10)

        # Устанавливаем положение окна ошибки по центру относительно родительского окна
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        window_width = 300
        window_height = 100

        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2)

        error_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def login(self):
        """Обработка входа в аккаунт"""
        login = self.login_entry.get()
        password = self.password_entry.get()
        if login and password:
            try:
                response = requests.post("http://127.0.0.1:5000/login", json={"nickname": login, "password": password})
                if response.status_code == 200:
                    self.on_login_success(login)  # Передаем ID пользователя в главный класс
                else:
                    error_message = response.json().get("error", "Неизвестная ошибка")
                    self.clear_password()  # Очищаем поле пароля
                    self.show_error_window(error_message)  # Показываем окно с ошибкой
            except Exception as e:
                self.clear_password()  # Очищаем поле пароля
                self.show_error_window(f"Ошибка соединения с сервером")
