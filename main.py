import sys
import webbrowser
import speech_recognition
import pyttsx3
from PyQt5 import QtWidgets, QtCore, QtGui
import ui_untitled
from PyQt5.QtCore import QThreadPool

class MyPersonalAssistantApp(QtWidgets.QMainWindow, ui_untitled.Ui_PersonalAssistant):
    def __init__(self):
        super(MyPersonalAssistantApp, self).__init__()
        self.setupUi(self)
        self.add_message_to_chat("Привет! Чем могу помочь?", "bot")
        self.recognizer = speech_recognition.Recognizer()
        self.microphone = speech_recognition.Microphone()
        self.ttsEngine = pyttsx3.init()
        self.setup_tts()
        self.responses = {
            "https://new.vyatsu.ru/sveden/document/": ["нормативные", "документы"],
            "https://www.vyatsu.ru/studentu-1/nauka-i-praktika.html": ["институты", "факультеты", "кафедры"],
            "https://www.vyatsu.ru/contacts": ["контакты", "связ"],
            "https://www.vyatsu.ru/studentu-1/kto-est-kto-v-vyatgu.html": ["преподаватели", "сотрудники"],
            "https://new.vyatsu.ru/": ["поступление", "приемная", "абитуриентам"],
            "https://www.vyatsu.ru/internet-gazeta.html": ["новости", "газета"],
            "https://www.vyatsu.ru/studentu-1/pervokursniku/adresa-i-telefonyi-uchebnyih-korpusov-fakul-tetov.html": ["корпус"],
            "https://www.vyatsu.ru/studentu-1/spravochnaya-informatsiya/raspisanie.html": ["расписание"],
            "https://www.vyatsu.ru/sotrudniku/doska/grafiki-uchebnogo-protsessa-na-2015-2016-uchebnyiy.html": ["учебный", "график"],
            "https://www.vyatsu.ru/nash-universitet/obrazovatelnaya-deyatel-nost/kolledzh.html": ["колледж"]
        }
        self.voice_button_state = False

    def connect_input_actions(self):
        "Сигналы нажатия кнопок."
        self.pushButton_4.clicked.connect(self.add_text_to_scroll_area)
        self.toolButton_9.clicked.connect(self.toggle_voice_input)

    def adjust_input_height(self):
        "Регулятор высоты QTextEdit_input в зависимости от количества строк. Ограничение высоты между minimumHeight() и maximumHeight(), затем прокрутка."
        doc = self.textEdit_input.document()
        content_height = doc.size().height()
        font_metrics = QtGui.QFontMetrics(self.textEdit_input.font())
        line_height = font_metrics.height()
        new_height = content_height
        min_height = self.textEdit_input.minimumHeight()
        max_height = self.textEdit_input.maximumHeight()
        if content_height > max_height:
            new_height = max_height
            if self.textEdit_input.verticalScrollBarPolicy() != QtCore.Qt.ScrollBarAsNeeded:
                self.textEdit_input.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        elif content_height < min_height:
            new_height = min_height
            if self.textEdit_input.verticalScrollBarPolicy() != QtCore.Qt.ScrollBarAlwaysOff:
                self.textEdit_input.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        else:
            if self.textEdit_input.verticalScrollBarPolicy() != QtCore.Qt.ScrollBarAlwaysOff:
                self.textEdit_input.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit_input.setFixedHeight(new_height)
        self.adjust_send_button_position()

    def adjust_send_button_position(self):
        "Позиция кнопки отправки и связанных элементов. На одном уровне с inputText."
        input_rect = self.textEdit_input.geometry()
        self.pushButton_4.move(
            self.pushButton_4.x(),
            input_rect.y() + (input_rect.height() - self.pushButton_4.height()) // 2
        )
        self.frame_10.adjustSize()

    def add_text_to_scroll_area(self):
        "При нажатии на pushButton_4, берет текст из textEdit_input, создает QLabel с текстом внутри scrollAreaWidgetContents_7,стилизует его и добавляет в вертикальный макет."
        text_to_add = self.textEdit_input.toPlainText().strip()
        if text_to_add:
            self.add_message_to_chat(text_to_add, "user")
            self.process_user_request(text_to_add)
            self.textEdit_input.clear()

    def scroll_to_bottom(self):
        "Прокрутка к последнему сообщению."
        def perform_scroll():
            if self.scrollAreaWidgetContents_7.layout():
                self.scrollAreaWidgetContents_7.layout().activate()
                self.scrollAreaWidgetContents_7.updateGeometry()
            self.scrollArea.verticalScrollBar().setValue(self.scrollArea.verticalScrollBar().maximum())
        QtCore.QTimer.singleShot(75, perform_scroll)

    def setup_tts(self):
        "Настройка Text-to-Speech (TTS)."
        self.ttsEngine.setProperty('rate', 180)
        voices = self.ttsEngine.getProperty('voices')
        ru_voice_id = None
        for voice in voices:
            if 'ru' in str(voice.languages).lower() or 'russian' in voice.name.lower():
                ru_voice_id = voice.id
                break
        if ru_voice_id is not None:
            self.ttsEngine.setProperty('voice', ru_voice_id)
        else:
            self.add_message_to_chat("Языковой файл для русского языка не найден. Проверьте настройки ашего устройства", "bot")

    def toggle_voice_button_border(self, state):
        "Нажатие на кнопку голоса"
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

    def toggle_voice_input(self):
        "Обработка нажатия на кнопку голоса для нанала/остановки запись. Гс активируется при 1 нажатии и отключается при повторном."
        self.voice_button_state = not self.voice_button_state
        self.toggle_voice_button_border(self.voice_button_state)
        if self.voice_button_state:
            message = "Голосовой ввод активирован. Чем могу помочь?"
            self.add_message_to_chat(message, "bot")
            self.play_voice_assistant_speech(message)
            QThreadPool.globalInstance().start(self.record_and_recognize_audio_threaded)
        else:
            self.add_message_to_chat("Голосовой ввод отключен.", "bot")

    def record_and_recognize_audio_threaded(self):
        "Запись аудио с микрофона и распознование речи (Выполняется в отдельном потоке)"
        while self.voice_button_state:
            recognized_data = ""
            error_message = "Простите, не совсем поняла вас, повторите, пожалуйста"
            try:
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except speech_recognition.WaitTimeoutError:
                self.add_message_to_chat(error_message, "bot")
                self.scroll_to_bottom()
                continue
            except Exception as e:
                print(f"Ошибка при записи аудио: {e}")
                self.add_message_to_chat("Произошла ошибка при записи аудио.", "bot")
                self.scroll_to_bottom()
                break
            try:
                if audio:
                    recognized_data = self.recognizer.recognize_google(audio, language="ru").lower()
                    self.process_user_request(recognized_data)
            except speech_recognition.UnknownValueError:
                self.add_message_to_chat(error_message, "bot")
                self.play_voice_assistant_speech(error_message)
                self.scroll_to_bottom()
            except Exception as e:
                print(f"Ошибка при распознавании речи: {e}")
                self.add_message_to_chat("Произошла ошибка при распознавании речи.", "bot")
                self.scroll_to_bottom()
            if not self.voice_button_state:
                break
        if not self.voice_button_state:
            self.add_message_to_chat("Голосовой ввод отключен.", "bot")
            self.toggle_voice_button_border(False)
            self.scroll_to_bottom()

    def play_voice_assistant_speech(self, text_to_speech):
        "Произносит текст голосом ассистента."
        if text_to_speech:
            try:
                if self.voice_button_state:
                    self.ttsEngine.say(str(text_to_speech))
                    self.ttsEngine.runAndWait()
            except Exception as e:
                print(f"Ошибка воспроизведения речи: {e}")

    def process_user_request(self, request):
        "Обрабатывает запрос и ищет ответ. Если запрос открывает сайт, гс ввод отключается."
        command = request.lower()
        if command in ["привет", "здравствуйте", "добрый день"]:
            bot_response = "Здравствуйте! Чем могу помочь?"
            self.add_message_to_chat(bot_response, "bot")
            self.play_voice_assistant_speech(bot_response)
            return
        found_link = False
        target_url = None
        for url, phrases in self.responses.items():
            for phrase in phrases:
                if phrase.lower() in command:
                    target_url = url
                    found_link = True
                    break
            if found_link:
                break
        if found_link and target_url:
            try:
                webbrowser.open(target_url, new=2, autoraise=True)
                response_message = "Нашел информацию. Открываю."
                self.add_message_to_chat(response_message, "bot")
                self.voice_button_state = False
            except Exception as e:
                error_message = f"Нашел информацию, но не удалось открыть ссылку: {target_url}. Ошибка: {e}"
                self.add_message_to_chat(error_message, "bot")
                if self.voice_button_state:
                    self.play_voice_assistant_speech(error_message)
                self.voice_button_state = False
        else:
            unknown_response = ("Извините, я не понял ваш запрос. Попробуйте переформулировать.")
            self.add_message_to_chat(unknown_response, "bot")
            if self.voice_button_state:
               self.play_voice_assistant_speech(unknown_response)

    def add_message_to_chat(self, message, sender):
        "Добавляет сообщение в область чата."
        if sender == "bot":
            bot_label = QtWidgets.QLabel(message, self.scrollAreaWidgetContents_7)
            bot_label.setStyleSheet(
                "padding: 10px; margin: 5px; border-radius: 5px; background-color: #f0f0f0; color: #333;"
            )
            bot_label.setWordWrap(True)
            bot_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.vertical_layout.addWidget(bot_label)
            self.scroll_to_bottom()
        elif sender == "user":
            user_text = QtWidgets.QLabel(message, self.scrollAreaWidgetContents_7)
            user_text.setStyleSheet(
                "padding: 10px; margin: 5px; border-radius: none; background-color: #fff; color: #00401E;"
            )
            user_text.setWordWrap(True)
            user_text.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.vertical_layout.addWidget(user_text)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MyPersonalAssistantApp()
    main_window.connect_input_actions()
    main_window.show()
    exit_code = app.exec_()
    sys.exit(exit_code)