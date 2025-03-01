import customtkinter as ctk
from login_screen import LoginScreen
from registration_screen import RegistrationScreen
from main_menu import MainMenu

# Настройка внешнего вида
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Вход в аккаунт")
        self.geometry("400x300")
        self.resizable(False, False)

        # Переменная для хранения ID пользователя
        self.login = None

        # Создание экрана входа
        self.current_screen = None
        # self.show_login_screen()
        self.show_main_menu("dfsfddf")

    def show_login_screen(self):
        """Показывает экран входа"""
        if self.current_screen:
            self.current_screen.pack_forget()
        self.current_screen = LoginScreen(self, self.show_main_menu, self.show_registration_screen)
        self.current_screen.pack(pady=20, padx=20, fill="both", expand=True)

    def show_registration_screen(self):
        """Показывает экран регистрации"""
        if self.current_screen:
            self.current_screen.pack_forget()
        self.current_screen = RegistrationScreen(self, self.show_login_screen)
        self.current_screen.pack(pady=20, padx=20, fill="both", expand=True)

    def show_main_menu(self, login):
        """Показывает главное меню"""
        if self.current_screen:
            self.current_screen.pack_forget()
        self.login = login
        self.current_screen = MainMenu(self, self.logout)
        self.current_screen.pack(pady=20, padx=20, fill="both", expand=True)

    def logout(self):
        """Обработка выхода из аккаунта"""
        self.login = None
        self.show_login_screen()

if __name__ == "__main__":
    app = App()
    app.mainloop()