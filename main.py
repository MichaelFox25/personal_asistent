import sys
import webbrowser
import speech_recognition
import pyttsx3
from PyQt5 import QtWidgets, QtCore, QtGui
import ui_untitled
from PyQt5.QtCore import QThreadPool, pyqtSignal, QTimer

class MyPersonalAssistantApp(QtWidgets.QMainWindow, ui_untitled.Ui_PersonalAssistant):
    new_user_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.add_messg_chat("Привет, можешь задать свой вопрос.", "bot")
        self.recognizer = speech_recognition.Recognizer()
        self.microphone = speech_recognition.Microphone()
        self.ttsEngine = pyttsx3.init()
        self.setup_tts()
        self.responses = {
            "https://new.vyatsu.ru/sveden/document/": ["нормативн", "документ"],
            "https://www.vyatsu.ru/studentu-1/nauka-i-praktika.html": ["институт", "факультет", "кафедр"],
            "https://www.vyatsu.ru/contacts": ["контакт", "связ"],
            "https://www.vyatsu.ru/studentu-1/kto-est-kto-v-vyatgu.html": ["препод", "сотруд"],
            "https://new.vyatsu.ru/": ["поступлен", "прием", "абитуриент"],
            "https://www.vyatsu.ru/internet-gazeta.html": ["новост", "газет"],
            "https://www.vyatsu.ru/studentu-1/pervokursniku/adresa-i-telefonyi-uchebnyih-korpusov-fakul-tetov.html": ["корпус"],
            "https://www.vyatsu.ru/studentu-1/spravochnaya-informatsiya/raspisanie.html": ["расписани"],
            "https://www.vyatsu.ru/sotrudniku/doska/grafiki-uchebnogo-protsessa-na-2015-2016-uchebnyiy.html": ["учебн", "график"],
            "https://www.vyatsu.ru/nash-universitet/obrazovatelnaya-deyatel-nost/kolledzh.html": ["колледж"]
        }
        self.voice_button_state = False
        self.new_user_message.connect(self.receiving_user_v_messg)
        self.pushButton_4.clicked.connect(self.add_t_scroll_area)
        self.toolButton_9.clicked.connect(self.toggle_v_input)

    def toggle_v_button(self, state):
        "нажатие на кнопку голоса (визуал)"
        if state:
            self.frame_14.setStyleSheet(
                "background-color: #0D6D50; border-radius: 35px; border: 3px solid green; padding: 0px;")
            self.label_2.setStyleSheet(
                "padding: 4px; border: none;")
            self.toolButton_9.setStyleSheet(
                "background-color: rgba(255, 255, 255, 0);")
        else:
            self.frame_14.setStyleSheet(
                "border-radius: 40px; border: none;")
            self.label_2.setStyleSheet(
                "padding: 0;")
            self.toolButton_9.setStyleSheet(
                "background-color: rgba(255, 255, 255, 0);")

    def add_t_scroll_area(self):
        "добавление текста в область прокрутки (поиск и отчистка)"
        text = self.textEdit_input.toPlainText().strip()
        if text:
            self.add_messg_chat(text, "user")
            self.process_user_request(text)
            self.textEdit_input.clear()

    def receiving_user_v_messg(self, message):
        "вывод голосовых запросов пользователя"
        if not message:
            return
        self.add_messg_chat(message, "user")
        self.process_user_request(message)

    def add_messg_chat(self, message, sender):
        "стиль в зависимости от отправителя"
        if sender == "bot":
            style = "QLabel {padding: 10px; margin: 5px; border-radius: 15px; background-color: #f0f0f0; color: #333;}"
        elif sender == "user":
            style = "QLabel { padding: 10px; margin: 5px; border-radius: 15px; background-color: #fff; color: #00401E;}"
        else:
            return
        label = QtWidgets.QLabel(message, self.scrollAreaWidgetContents_7)
        label.setStyleSheet(style)
        label.setWordWrap(True)
        label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.vertical_layout.addWidget(label)
        QTimer.singleShot(0, self.scroll_bottom)

    def scroll_bottom(self):
        "прокрутка вниз"
        self.scrollAreaWidgetContents_7.updateGeometry()
        self.scrollArea.update()
        QtWidgets.QApplication.processEvents()
        sb = self.scrollArea.verticalScrollBar()
        sb.setValue(sb.maximum())

    def setup_tts(self):
        "настройка ттс (Text‑to‑Speech)"
        self.ttsEngine.setProperty('rate', 175)
        voices = self.ttsEngine.getProperty('voices')
        for voice in voices:
            if 'ru' in str(voice.languages).lower() or 'russian' in voice.name.lower():
                self.ttsEngine.setProperty('voice', voice.id)
                return
        self.add_messg_chat("Языковой файл для русского языка не найден. Проверьте настройки вашего устройства","bot")

    def play_v_assistant_speech(self, text):
        "речь ассистента"
        if text and self.voice_button_state:
            try:
                self.ttsEngine.say(str(text))
                self.ttsEngine.runAndWait()
            except Exception as e:
                print(f"TTS error: {e}")

    def toggle_v_input(self):
        "переключение голосового ввода гс активируется при 1 нажатии и отключается при повторном."
        self.voice_button_state = not self.voice_button_state
        self.toolButton_9.setChecked(self.voice_button_state)
        if self.voice_button_state:
            msg = "Голосовой ввод активирован. Чем могу помочь?"
            self.add_messg_chat(msg, "bot")
            self.play_v_assistant_speech(msg)
            QThreadPool.globalInstance().start(self.record_recognize_audio_threaded)
        else:
            self.add_messg_chat("Голосовой ввод отключен.", "bot")

    def record_recognize_audio_threaded(self):
        "запись и распознавание речи (Выполняется в отдельном потоке)"
        while self.voice_button_state:
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except speech_recognition.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"Ошибка записи: {e}")
                break
            if not self.voice_button_state:
                break
            try:
                if audio:
                    recognized = self.recognizer.recognize_google(audio, language="ru").lower()
                    if recognized:
                        recognized = recognized[0].upper() + recognized[1:]
                        if self.voice_button_state:
                            self.new_user_message.emit(recognized)
            except speech_recognition.UnknownValueError:
                pass
            except Exception as e:
                print(f"Ошибка распознавания: {e}")

    def process_user_request(self, request):
        "обработка запроса пользователя и поиск ответа."
        command = request.lower().strip()
        if command in ["привет", "здравствуйте", "добрый день"]:
            bot_response = "Чем могу помочь?"
            self.add_messg_chat(bot_response, "bot")
            self.play_v_assistant_speech(bot_response)
            return
        if command in ["пока", "до свидания", "выход", "закр", "стоп"]:
            bot_response = "До свидания"
            self.add_messg_chat(bot_response, "bot")
            self.play_v_assistant_speech(bot_response)
            if self.voice_button_state:
                self.voice_button_state = False
                self.toolButton_9.setChecked(False)
            QTimer.singleShot(750, self.close)
            return

        target_url = None
        for url, phrases in self.responses.items():
            if any(phrase in command for phrase in phrases):
                target_url = url
                break
        if target_url:
            try:
                webbrowser.open(target_url, new=2, autoraise=True)
                self.add_messg_chat("Нашел информацию. Открываю.", "bot")
                if self.voice_button_state:
                    self.voice_button_state = False
                    self.toolButton_9.setChecked(False)
            except Exception as e:
                err = f"Не удалось открыть ссылку: {target_url}. Ошибка: {e}"
                self.add_messg_chat(err, "bot")
                if self.voice_button_state:
                    self.play_v_assistant_speech(err)
                    self.voice_button_state = False
                    self.toolButton_9.setChecked(False)
        else:
            reply = "Извините, я не понял ваш запрос. Попробуйте переформулировать."
            self.add_messg_chat(reply, "bot")
            if self.voice_button_state:
                self.play_v_assistant_speech(reply)

    def close_event(self, event):
        "закрытие"
        self.voice_button_state = False
        try:
            self.ttsEngine.stop()
        except:
            pass
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyPersonalAssistantApp()
    window.show()
    sys.exit(app.exec_())