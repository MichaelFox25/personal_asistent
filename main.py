import sys
import webbrowser
import speech_recognition
from PyQt5 import QtWidgets, QtCore
import ui_untitled
from PyQt5.QtCore import pyqtSignal, QTimer, pyqtSlot
import playsound3
from gtts import gTTS
import tempfile
import os

class VoiceRecognitionWorker(QtCore.QObject):
    message = pyqtSignal(str)

    def __init__(self, recognizer, microphone):
        super().__init__()
        self.recognizer = recognizer
        self.microphone = microphone
        self._is_running = True

    def stop(self):
        self._is_running = False

    @pyqtSlot()
    def run(self):
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            print(f"Ошибка настройки шумоподавления: {e}")
            return
        while self._is_running:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            except speech_recognition.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"Ошибка записи: {e}")
                break
            if not self._is_running:
                break
            try:
                recognized = self.recognizer.recognize_google(audio, language="ru").lower()
                if recognized:
                    recognized = recognized[0].upper() + recognized[1:]
                    self.message.emit(recognized)
            except speech_recognition.UnknownValueError:
                pass
            except Exception as e:
                print(f"Ошибка распознавания: {e}")

class MyPersonalAssistantApp(QtWidgets.QMainWindow, ui_untitled.Ui_PersonalAssistant):
    new_user_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.add_messg_chat("Привет, можешь задать свой вопрос.", "bot")
        self.recognizer = speech_recognition.Recognizer()
        self.microphone = speech_recognition.Microphone()
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
        self.voice_thread = None
        self.voice_worker = None

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

    def play_v_assistant_speech(self, text):
        "речь ассистента"
        if text and self.voice_button_state:
            try:
                tts = gTTS(text=text, lang='ru')
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                    tts.save(f.name)
                    temp_filename = f.name
                sound = playsound3.playsound(temp_filename, block=False)
                while sound.is_alive():
                    QtCore.QThread.msleep(180)
                os.unlink(temp_filename)
            except Exception as e:
                print(f"Ошибка синтеза речи: {e}")

    def toggle_v_input(self):
        if self.voice_button_state:
            msg = "Голосовой ввод отключен."
            self.add_messg_chat(msg, "bot")
            self.voice_button_state = False
            self.toolButton_9.setChecked(False)
            if self.voice_worker:
                self.voice_worker.stop()
                if self.voice_thread and self.voice_thread.isRunning():
                    self.voice_thread.quit()
                    self.voice_thread.wait()
        else:
            self.voice_button_state = True
            self.toolButton_9.setChecked(True)
            msg = "Голосовой ввод активирован. Чем могу помочь?"
            self.add_messg_chat(msg, "bot")
            self.scroll_bottom()  # немедленная прокрутка
            QtWidgets.QApplication.processEvents()  # обновление интерфейса
            self.play_v_assistant_speech(msg)

            self.voice_thread = QtCore.QThread()
            self.voice_worker = VoiceRecognitionWorker(self.recognizer, self.microphone)
            self.voice_worker.moveToThread(self.voice_thread)
            self.voice_worker.message.connect(self.new_user_message.emit)
            self.voice_thread.started.connect(self.voice_worker.run)
            self.voice_thread.finished.connect(self.voice_worker.deleteLater)
            self.voice_thread.start()

    def reply(self, text, turn_off_voice=False):
        "Ответ бота и его озвучка"
        self.add_messg_chat(text, "bot")
        self.scroll_bottom()
        QtWidgets.QApplication.processEvents()
        if self.voice_button_state:
            self.play_v_assistant_speech(text)
            if turn_off_voice:
                self.voice_button_state = False
                self.toolButton_9.setChecked(False)

    def process_user_request(self, request):
        "обработка запроса пользователя и поиск ответа."
        command = request.lower().strip()
        if command in ["привет", "здравствуйте", "добрый день"]:
            self.reply("Чем могу помочь?")
            return
        if command in ["пока", "до свидания", "выход", "стоп"]:
            self.reply("До свидания", turn_off_voice=True)
            self.close()
            return

        target_url = None
        for url, phrases in self.responses.items():
            if any(phrase in command for phrase in phrases):
                target_url = url
                break
        if target_url:
            try:
                webbrowser.open(target_url, new=2, autoraise=True)
                self.reply("Нашел информацию. Открываю.", turn_off_voice=True)
            except Exception as e:
                err = f"Не удалось открыть ссылку: {target_url}. Ошибка: {e}"
                self.add_messg_chat(err, "bot")
                if self.voice_button_state:
                    self.play_v_assistant_speech("Не удалось открыть ссылку")
        else:
            self.reply("Извините, я не понял ваш запрос. Попробуйте переформулировать.")

    def closeEvent(self, event):
        "закрытие"
        self.voice_button_state = False
        if self.voice_worker:
            self.voice_worker.stop()  # останавливаем воркер
        if self.voice_thread and self.voice_thread.isRunning():
            self.voice_thread.quit()
            self.voice_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyPersonalAssistantApp()
    window.show()
    sys.exit(app.exec_())