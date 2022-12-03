from tkinter import messagebox, Button, Entry
import tkinter


class LabUI(tkinter.Tk):
    def __init__(self):
        messagebox.showinfo(
            title='Приветствие',
            message="Добро пожаловать в приложение для работы с eToken!"
        )
        super().__init__()
        # Cоздаем кнопки и текстовые поля, располагаем их на окне
        self.title("Приложение для работы с EToken")
        self.slots_list_button = Button(self, text="Информация о слотах")
        self.slots_list_button.grid(column=0, row=0, padx=15, pady=15)

        self.slot_info_button = Button(self, text="Информация о слоте")
        self.slot_info_button.grid(column=0, row=1, padx=15, pady=15)

        self.token_info_button = Button(self, text="Информация о токене")
        self.token_info_button.grid(column=0, row=2, padx=15, pady=15)

        self.open_session_button = Button(self, text="Открытие сессии")
        self.open_session_button.grid(column=1, row=0, padx=15, pady=15)

        self.generate_key_button = Button(self, text="Генерация ключа шифрования")
        self.generate_key_button.grid(column=2, row=0, padx=15, pady=15)
        self.generate_key_button["state"] = "disabled"

        self.encrypt_input = Entry(self, width=50)
        self.encrypt_input.grid(column=1, row=1)
        self.encrypt_button = Button(self, text="Шифрование")
        self.encrypt_button.grid(column=2, row=1, padx=15, pady=15)
        self.encrypt_button["state"] = "disabled"

        self.decrypt_input = Entry(self, width=50)
        self.decrypt_input.grid(column=1, row=2)
        self.decrypt_button = Button(self, text="Расшифрование")
        self.decrypt_button.grid(column=2, row=2, padx=15, pady=15)
        self.decrypt_button["state"] = "disabled"

        self.close_session_button = Button(self, text="Закрытие сессии")
        self.close_session_button.grid(column=1, row=7, padx=15, pady=15)
        self.close_session_button["state"] = "disabled"

        self.resizable(False, False)

    def move_to_foreground(self):
        """Функция, которая выводит окно на первый план"""
        self.lift()
        self.attributes('-topmost', True)
        self.after_idle(self.attributes, '-topmost', False)
