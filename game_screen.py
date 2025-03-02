import random

import customtkinter as ctk
import cv2
import numpy as np
import requests
from PIL import Image, ImageTk
from tensorflow.keras.models import load_model

class GameScreen(ctk.CTkFrame):
    def __init__(self, master, on_back_click):
        super().__init__(master)

        self.on_back_click = on_back_click
        self.master = master  # Сохраняем ссылку на родительский виджет
        self.cap = None  # Камера
        self.available_cameras = []  # Список доступных камер
        self.preview_labels = []  # Список меток для превью камер
        self.current_player_choice = None
        self.computer_score = 0
        self.player_score = 0

        self.model = None
        self.player_prediction_label = None  # Метка для вывода предсказания
        self.left_frame = None
        self.right_frame = None
        self.computer_choice_image_label = None
        # Увеличиваем размер окна
        self.master.geometry("800x600")

        # Заголовок
        label = ctk.CTkLabel(self, text="Выбор камеры", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=20, padx=10)

        # Кнопка "Назад"
        back_button = ctk.CTkButton(self, text="Назад", command=self.close_camera_and_return)
        back_button.pack(pady=10, padx=10, anchor="w")

        # Проверяем наличие камер
        self.find_available_cameras()

        if not self.available_cameras:
            # Если камер нет, показываем ошибку
            error_label = ctk.CTkLabel(self, text="Веб-камера не найдена", text_color="red", font=ctk.CTkFont(size=16))
            error_label.pack(pady=30)
        else:
            # Если камеры есть, показываем выпадающий список и превью
            self.create_camera_selection()
            self.create_camera_previews()

    def find_available_cameras(self):
        """Находит доступные камеры"""
        self.available_cameras = []
        index = 0

        while True:
            cap = cv2.VideoCapture(index)
            if not cap.read()[0]:  # Если камера не открывается
                break
            self.available_cameras.append(index)
            cap.release()  # Важно освободить камеру после проверки
            index += 1

    def create_camera_selection(self):
        """Создает выпадающий список для выбора камеры"""
        camera_label = ctk.CTkLabel(self, text="Выберите камеру:", font=ctk.CTkFont(size=18))
        camera_label.pack(pady=10)

        camera_variable = ctk.StringVar(value=f"Камера {self.available_cameras[0]}")
        camera_menu = ctk.CTkOptionMenu(
            self,
            values=[f"Камера {i}" for i in self.available_cameras],
            variable=camera_variable
        )
        camera_menu.pack(pady=10)

        # Кнопка подтверждения выбора
        confirm_button = ctk.CTkButton(
            self,
            text="Подтвердить",
            command=lambda: self.open_selected_camera(camera_variable.get())
        )
        confirm_button.pack(pady=10)

    def create_camera_previews(self):
        """Создает превью для каждой доступной камеры"""
        # Создаем контейнер для превью
        preview_frame = ctk.CTkFrame(self, border_width=2, border_color="gray")
        preview_frame.pack(pady=20, fill="both", expand=True)

        # Очищаем список предыдущих превью
        self.preview_labels.clear()

        for i, camera_index in enumerate(self.available_cameras):
            cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            if cap.isOpened():
                label = ctk.CTkLabel(preview_frame, text=f"Камера {camera_index}", font=ctk.CTkFont(size=14))
                label.grid(row=i, column=0, padx=10, pady=5, sticky="w")

                preview_label = ctk.CTkLabel(preview_frame, text="")
                preview_label.grid(row=i, column=1, padx=10, pady=5)
                self.preview_labels.append((cap, preview_label))

                # Запускаем обновление превью
                self.update_preview(cap, preview_label)
            else:
                cap.release()

    def update_preview(self, cap, preview_label):
        """Обновляет превью камеры в реальном времени"""
        if not cap.isOpened():  # Проверяем, открыта ли камера
            return

        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (200, 150))  # Уменьшаем размер изображения
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image=image)
            preview_label.configure(image=photo)
            preview_label.image = photo

        # Повторяем через 10 мс
        preview_label.after(10, lambda: self.update_preview(cap, preview_label))

    def open_selected_camera(self, selected_camera):
        """Открывает выбранную камеру и показывает инструкцию"""
        try:
            camera_index = int(selected_camera.split()[-1])  # Получаем индекс камеры
            self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                raise ValueError("Не удалось открыть камеру")

            # Показываем окно с инструкцией
            self.show_instruction_window()

            # Модифицируем основное окно
            self.modify_main_window()

        except Exception as e:
            error_label = ctk.CTkLabel(self, text=f"Ошибка: {str(e)}", text_color="red", font=ctk.CTkFont(size=16))
            error_label.pack(pady=20)

    def show_instruction_window(self):
        """Показывает окно с инструкцией"""
        instruction_window = ctk.CTkToplevel(self.master)
        instruction_window.title("Инструкция")
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        window_width = 400
        window_height = 350

        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2)

        instruction_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        instruction_window.grab_set()
        instruction_window.focus_force()

        # Текст инструкции
        instruction_text = (
            "Добро пожаловать в игру!\n\n"
            "1. Подготовьте свою камеру.\n"
            "2. Когда будете готовы, нажмите 'Начать игру'.\n"
            "3. Показывайте в прямоугольник на камере жест и нажимайте \"Сделать ход\" или пробел\n\n"
            "Удачи!"
        )
        instruction_label = ctk.CTkLabel(instruction_window, text=instruction_text, font=ctk.CTkFont(size=14))
        instruction_label.pack(pady=20, padx=20)

        # Кнопка закрытия окна
        close_button = ctk.CTkButton(instruction_window, text="Закрыть", command=instruction_window.destroy)
        close_button.pack(pady=10)
    def load_model(self):
        """Загружает модель компьютерного зрения"""
        try:
            self.model = load_model("rps42.h5")
            print("Модель успешно загружена!")
        except Exception as e:
            print(f"Ошибка при загрузке модели: {str(e)}")

    def show_round_result(self, player_choice, computer_choice, result):
        """Показывает результат раунда в отдельном окне"""
        result_window = ctk.CTkToplevel(self.master)
        result_window.title("Результат раунда")
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        window_width = 400
        window_height = 350

        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2)

        result_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        result_window.grab_set()
        result_window.focus_force()

        # Текст результата
        result_text = (
            f"Ваш выбор: {player_choice}\n"
            f"Выбор компьютера: {computer_choice}\n\n"
            f"Результат: {result.capitalize()}"
        )
        result_label = ctk.CTkLabel(result_window, text=result_text, font=ctk.CTkFont(size=16))
        result_label.pack(pady=20, padx=20)

        # Кнопка закрытия окна
        close_button = ctk.CTkButton(result_window, text="Продолжить", command=result_window.destroy)
        close_button.pack(pady=10)
        result_window.bind("<space>", lambda event: result_window.destroy())
    def show_computer_choice(self, choice):
        """Отображает выбор компьютера вместо надписи 'Готов'"""
        # Удаляем старую метку "Готов"
        for widget in self.right_frame.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and widget.cget("text") == "Готов":
                widget.pack_forget()
        image_path = {
            "камень": "rock.jpg",
            "ножницы": "scissors.jpg",
            "бумага": "paper.jpg",
        }.get(choice, "paper.png")

        try:
            image = Image.open(image_path)
            image = image.resize((200, 200))
            photo = ImageTk.PhotoImage(image)

            if not self.computer_choice_image_label:
                # Создаем новую метку для картинки
                self.computer_choice_image_label = ctk.CTkLabel(self.right_frame, image=photo, text="")
            else:
                self.computer_choice_image_label.configure(image=photo)
            self.computer_choice_image_label.image = photo
            self.computer_choice_image_label.pack(expand=True)
        except Exception as e:
            print(f"Ошибка при загрузке изображения: {str(e)}")

    def end_game(self, player_choice, computer_choice, result):
        """Завершает игру и показывает победителя"""
        winner = "Игрок" if self.player_score == 3 else "Компьютер"
        result_window = ctk.CTkToplevel(self.master)
        result_window.title("Конец игры")
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()

        window_width = 400
        window_height = 400

        x = parent_x + (parent_width // 2) - (window_width // 2)
        y = parent_y + (parent_height // 2) - (window_height // 2)
        current_wins = None
        current_losses = None
        try:
            response = requests.get("http://127.0.0.1:5000/search", params={"nickname": self.master.login})
            if response.status_code == 200:
                r_json = response.json()
                results = r_json["results"]
                n_res = results[0]
                current_wins = n_res["wins"]
                current_losses = n_res["losses"]
            else:
                ...
        except Exception as e:
            print(e)
            ...

        result_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        result_window.grab_set()
        result_window.focus_force()
        result_text = (
            f"Ваш выбор: {player_choice}\n"
            f"Выбор компьютера: {computer_choice}\n\n"
            f"Результат: {result.capitalize()}\n\n"
            f"Игра окончена!\n{winner} выиграл!"
        )
        if current_wins is not None and current_losses is not None:
            if winner == "Игрок":
                current_wins += 1
            else:
                current_losses += 1
            try:
                requests.post("http://127.0.0.1:5000/update_stats", json={"nickname": self.master.login, "wins": current_wins, "losses": current_losses})
            except Exception as e:
                print(e)
                ...
            result_text += f"\n\nВаша статистика:\nПобед: {current_wins}\nПоражений: {current_losses}"
        result_label = ctk.CTkLabel(result_window, text=result_text, font=ctk.CTkFont(size=20, weight="bold"))
        result_label.pack(pady=20, padx=20)

        # Кнопка возврата в главное меню
        menu_button = ctk.CTkButton(
            result_window,
            text="Вернуться в меню",
            command=lambda: [result_window.destroy(), self.close_camera_and_return()]
        )
        menu_button.pack(pady=10)
    def make_move(self):
        player_choice = self.current_player_choice
        if player_choice == 0:
            return
        label_russian_names = ["ничего", "бумага", "камень", "ножницы"]
        player_choice_name = label_russian_names[player_choice]

        # Генерируем случайный выбор компьютера
        computer_choice = random.randint(1, 3)  # 1: камень, 2: ножницы, 3: бумага
        computer_choice_name = label_russian_names[computer_choice]
        if player_choice == computer_choice:
            result = "ничья"
        elif (player_choice == 1 and computer_choice == 3) or \
                (player_choice == 2 and computer_choice == 1) or \
                (player_choice == 3 and computer_choice == 2):
            result = "компьютер"
            self.computer_score += 1
        else:
            result = "игрок"
            self.player_score += 1
        self.player_score_label.configure(text=f"Счет: {self.player_score}")
        self.computer_score_label.configure(text=f"Счет: {self.computer_score}")
        self.show_computer_choice(computer_choice_name)
        if self.player_score == 3 or self.computer_score == 3:
            self.end_game(player_choice_name, computer_choice_name, result)
        else:
            self.show_round_result(player_choice_name, computer_choice_name, result)
    def start_game(self):
        self.load_model()
        self.start_button.configure(text="Сделать ход", command=self.make_move, fg_color="green",  # Зеленый цвет кнопки
        hover_color="#006400")
        self.master.bind("<space>", lambda event: self.make_move())

    def modify_main_window(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.master.geometry("1000x600")
        self.left_frame = ctk.CTkFrame(self, border_width=2, border_color="gray")
        self.left_frame.place(relx=0.05, rely=0.1, relwidth=0.4, relheight=0.8)

        self.right_frame = ctk.CTkFrame(self, border_width=2, border_color="gray")
        self.right_frame.place(relx=0.55, rely=0.1, relwidth=0.4, relheight=0.8)
        self.player_score = 0
        self.player_score_label = ctk.CTkLabel(
            self.left_frame,
            text=f"Счет: {self.player_score}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="green"
        )
        self.player_score_label.pack(pady=(10, 5))
        player_label = ctk.CTkLabel(self.left_frame, text="Игрок", font=ctk.CTkFont(size=20, weight="bold"))
        player_label.pack(pady=5)
        self.player_prediction_label = ctk.CTkLabel(
            self.left_frame,
            text="",
            font=ctk.CTkFont(size=16),
            text_color="green"
        )
        self.player_prediction_label.pack(pady=(0, 10))
        video_label = ctk.CTkLabel(self.left_frame, text="")
        video_label.pack(fill="both", expand=True)
        label_russian_names = ["ничего", "бумага", "камень", "ножницы"]
        def update_camera_feed():
            ret, frame = self.cap.read()
            if ret:
                box_size = 234
                width = int(self.cap.get(3))
                frame = cv2.flip(frame, 1)
                frame_copy = frame.copy()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                cv2.rectangle(frame, (width - box_size, 0), (width, box_size), (0, 250, 150), 2)

                image = Image.fromarray(frame)
                photo = ImageTk.PhotoImage(image=image)
                video_label.configure(image=photo)
                video_label.image = photo

                if self.player_prediction_label and self.model:
                    roi = frame_copy[5: box_size - 5, width - box_size + 5: width - 5]
                    roi = np.array([roi]).astype('float64') / 255.0
                    pred = self.model.predict(roi)
                    target_index = np.argmax(pred[0])
                    self.current_player_choice = target_index
                    prob = np.max(pred[0])
                    self.player_prediction_label.configure(
                        text=f"Вы показываете: {label_russian_names[target_index]} ({prob * 100:.2f}%)")

            video_label.after(25, update_camera_feed)

        update_camera_feed()
        self.computer_score = 0
        self.computer_score_label = ctk.CTkLabel(
            self.right_frame,
            text=f"Счет: {self.computer_score}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="blue"
        )
        self.computer_score_label.pack(pady=(10, 5))
        computer_label = ctk.CTkLabel(self.right_frame, text="Компьютер", font=ctk.CTkFont(size=20, weight="bold"))
        computer_label.pack(pady=10)
        self.ready_label = ctk.CTkLabel(self.right_frame, text="Готов", font=ctk.CTkFont(size=40, weight="bold"))
        self.ready_label.pack(expand=True)
        button_frame = ctk.CTkFrame(self)
        button_frame.place(relx=0.3, rely=0.9, relwidth=0.4, relheight=0.1)

        self.start_button = ctk.CTkButton(
            button_frame,
            text="Начать игру",
            command=self.start_game,
            fg_color="green",
            hover_color="#006400"
        )
        self.start_button.pack(side="left", padx=10)

        menu_button = ctk.CTkButton(button_frame, text="Вернуться в меню", command=self.close_camera_and_return)
        menu_button.pack(side="right", padx=10)

    def close_camera_and_return(self):
        """Закрывает камеру и возвращает пользователя в главное меню"""
        # Освобождаем все открытые камеры
        for cap, _ in self.preview_labels:
            if cap.isOpened():
                cap.release()

        # Удаляем ссылки на камеры и метки превью
        self.preview_labels.clear()

        # Закрываем основную камеру, если она открыта
        if self.cap:
            self.cap.release()
            self.cap = None

        # Уничтожаем текущий экран
        self.destroy()

        # Вызываем коллбэк для возврата в главное меню
        self.on_back_click()