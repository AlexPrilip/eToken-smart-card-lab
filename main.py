import pkcs11  # Библиотека для работы с Etoken
import binascii # используется для перевода текста в его hex вариант
from tkinter import messagebox # окошко, на котором выводится инфа по типу "Все ок", "Ошибка"
from ui import LabUI


class TokenDisconnected(Exception):
    """Исключение, которое выбрасывается, когда токен отключается."""
    pass


class EmtpyInputError(Exception):
    """
        Исключение, которое выбрасывается,
        когда поля ввода пусты и происходит
        нажатие кнопки на обработку их содержимого
     """
    pass


ui = LabUI()  # Создаем класс LabUI в глобальной области видимости, чтобы иметь к нему доступ внутри функций


class SmartCardService:
    """класс для работы со смарт-картой"""
    def __init__(self):
        self.lib = pkcs11.lib('C:\\Windows\\System32\\eTPKCS11.dll')  # инициализация библиотеки
        self.token = None # сюда будет помещен объект токена
        self.session = None # cюда будет помещен объект сессии с токеном
        self.key = None # сюда будет помещен объект ключа

    def initialize(self):  # инициализация е-токена
        try:
            self.token = self.lib.get_token(token_label='eToken')
            return self.token
        except pkcs11.exceptions.NoSuchToken:
            self.token = None
            return None

    def getSlotList(self):  # СОБИРАЕМ ИНФОРМАЦИЮ О СЛОТАХ
        if not self.is_token_active():
            raise TokenDisconnected
        slots_info = self.lib.get_slots()
        return slots_info

    def getSlotInfo(self):  # информация о слоте
        if not self.is_token_active():
            raise TokenDisconnected
        slot_info = self.token.slot
        return slot_info

    def getTokenInfo(self):  # информация о токене
        if not self.is_token_active():
            raise TokenDisconnected

        manufacturer_id = self.token.manufacturer_id
        model = self.token.model
        serial = self.token.serial.decode()
        return f'manufacturer_id: {manufacturer_id}\nmodel: {model}\nserial: {serial}'

    def is_token_active(self):
        try:
            self.token = self.lib.get_token(token_label='eToken')
            return True
        except pkcs11.exceptions.NoSuchToken:
            self.token = None
            return False

    def Login(self):
        if not self.is_token_active():
            raise TokenDisconnected
        self.session = self.token.open(rw=True, user_pin='1234567890')
        return self.session

    def generateKey(self):
        if not self.is_token_active():
            raise TokenDisconnected
        self.key = self.session.generate_key(pkcs11.KeyType.DES3)
        return self.key

    def Encrypt(self, input_data):
        if not self.is_token_active():
            raise TokenDisconnected

        cypher_text = self.key.encrypt(input_data.encode())
        hex_encrypted_data = binascii.hexlify(cypher_text)
        return hex_encrypted_data.decode()

    def Decrypt(self, hex_input_data):
        if not self.is_token_active():
            raise TokenDisconnected

        data_to_decode = binascii.unhexlify(hex_input_data.encode())
        decrypted_data = self.key.decrypt(data_to_decode)
        return decrypted_data.decode()

    def CloseSession(self):
        if not self.is_token_active():
            raise TokenDisconnected

        self.session.close()

        self.session = None
        self.key = None


class SmartCard:
    def __init__(self):
        self.slot_list = None
        self.token_info = None


def InformationAboutSlots():
    try:
        information = ''
        slots_info = smart_card_service.getSlotList()
        for i in range(len(slots_info)):
            information += f'slodId: {slots_info[i].slot_id}\ndescription: {slots_info[i].slot_description}\n'
        messagebox.showinfo(title=None, message=f'{information}')
    except TokenDisconnected:
        messagebox.showinfo(title=None, message='eToken не найден!')


def InformationAboutSlot():
    try:
        information = smart_card_service.getSlotInfo()
        messagebox.showinfo(title=None, message=f'{information}')
    except TokenDisconnected:
        messagebox.showinfo(title=None, message='eToken не найден!')


def InformationAboutToken():
    try:
        token_info = smart_card_service.getTokenInfo()
        messagebox.showinfo(title=None, message=token_info)
    except TokenDisconnected:
        messagebox.showinfo(title=None, message='eToken не найден!')


def OpenSession():
    try:
        session = smart_card_service.Login()
        messagebox.showinfo(title=None,
                            message='Сессия открыта. Теперь вам доступны кнопки генерации ключа шифрования и закрытия сессии.')
        ui.generate_key_button["state"] = "normal"
        ui.close_session_button["state"] = "normal"
        ui.open_session_button["state"] = "disabled"
    except TokenDisconnected:
        messagebox.showinfo(title=None, message='eToken не найден!')


def KeyGeneration():
    try:
        smart_card_service.generateKey()
        messagebox.showinfo(title=None,
                            message='Ключ шифрования сгенерирован. Теперь вам доступны кнопки шифрования и расшифрования.')
        ui.encrypt_button["state"] = "normal"
        ui.decrypt_button["state"] = "normal"
    except TokenDisconnected:
        messagebox.showinfo(title=None, message='eToken не найден!')


def Encryption():
    try:
        input_data = ui.encrypt_input.get()
        if not input_data:
            raise EmtpyInputError
        hex_encrypted_data = smart_card_service.Encrypt(input_data)
        messagebox.showinfo(title=None, message=hex_encrypted_data)
        ui.clipboard_clear()
        ui.clipboard_append(hex_encrypted_data)
    except TokenDisconnected:
        messagebox.showinfo(title=None, message='eToken не найден!')
    except EmtpyInputError:
        messagebox.showinfo(title=None, message="Нельзя зашифровать пустую строку")


def Decryption():
    try:
        hex_input_data = ui.decrypt_input.get()
        if not hex_input_data:
            raise EmtpyInputError
        decrypted_data = smart_card_service.Decrypt(hex_input_data)
        messagebox.showinfo(title=None, message=decrypted_data)
        ui.clipboard_clear()
        ui.clipboard_append(decrypted_data)
    except TokenDisconnected:
        messagebox.showinfo(title=None, message='eToken не найден!')
    except EmtpyInputError:
        messagebox.showinfo(title=None, message="Нельзя расшифровать пустую строку")
    except binascii.Error:
        messagebox.showinfo(title=None, message="Неправильный шифртекст")


def CloseSession():
    try:
        smart_card_service.CloseSession()
        messagebox.showinfo(title=None,
                            message='Сессия закрыта. Теперь вам не доступны кнопки закрытия сессии, генерации ключа, шифрования и расшифрования. Кнопка открыия сессии вновь доступна.')
        ui.open_session_button["state"] = "normal"
        ui.generate_key_button["state"] = "disabled"
        ui.encrypt_button["state"] = "disabled"
        ui.decrypt_button["state"] = "disabled"
        ui.close_session_button["state"] = "disabled"
    except TokenDisconnected:
        messagebox.showinfo(title=None, message='eToken не найден!')


def SetCommandsToButtons(ui: LabUI):
    ui.slots_list_button["command"] = InformationAboutSlots
    ui.slot_info_button["command"] = InformationAboutSlot
    ui.token_info_button["command"] = InformationAboutToken
    ui.open_session_button["command"] = OpenSession
    ui.generate_key_button["command"] = KeyGeneration
    ui.encrypt_button["command"] = Encryption
    ui.decrypt_button["command"] = Decryption
    ui.close_session_button["command"] = CloseSession


if __name__ == '__main__':
    smart_card_service = SmartCardService()
    smart_card_service.initialize()
    SetCommandsToButtons(ui)
    ui.move_to_foreground()
    ui.mainloop()
