import sys
import webbrowser
import speech_recognition
from PyQt5 import QtWidgets, QtCore, QtMultimedia
from PyQt5.QtCore import pyqtSignal, QTimer, pyqtSlot, QUrl
import tempfile
import os
from gtts import gTTS
import ui_untitled

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
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=10)
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
        self.new_user_message.connect(self.handle_user_messg)
        self.pushButton_4.clicked.connect(self.add_t_scroll_area)
        self.toolButton_9.clicked.connect(self.toggle_v_input)
        self.toolButton_9.setCheckable(True)
        self.voice_thread = None
        self.voice_worker = None
        self.media_player = QtMultimedia.QMediaPlayer()
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)
        self.temp_audio_file = None

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

    def add_messg_chat(self, message, sender):
        "стили в зависимости от отправителя"
        styles = {
            "bot": "QLabel {padding: 10px; margin: 5px; border-radius: 15px; background-color: #f0f0f0; color: #333;}",
            "user": "QLabel {padding: 10px; margin: 5px; border-radius: 15px; background-color: #fff; color: #00401E;}"
        }
        if sender not in styles:
            return
        label = QtWidgets.QLabel(message, self.scrollAreaWidgetContents_7)
        label.setStyleSheet(styles[sender])
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

    def add_t_scroll_area(self):
        "обработка текста/запроса пользователя"
        text = self.textEdit_input.toPlainText().strip()
        if text:
            self.handle_user_messg(text)
            self.textEdit_input.clear()

    def handle_user_messg(self, text):
        "вывод и обработка запросов пользователя"
        self.add_messg_chat(text, "user")
        self.process_user_request(text)

    def _play_speech(self, text):
        "речь ассистента (не зависит от voice_button_state)."
        if not text:
            return
        try:
            tts = gTTS(text=text, lang='ru')
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as f:
                tts.save(f.name)
                self.temp_audio_file = f.name
            url = QUrl.fromLocalFile(self.temp_audio_file)
            self.media_player.setMedia(QtMultimedia.QMediaContent(url))
            self.media_player.play()
        except Exception as e:
            print(f"Ошибка синтеза речи: {e}")

    def play_v_assistant_speech(self, text):
        "речь ассистента (голосовой ввод включён)"
        if self.voice_button_state:
            self._play_speech(text)

    @pyqtSlot(QtMultimedia.QMediaPlayer.MediaStatus)
    def on_media_status_changed(self, status):
        "удаление временного мп3 файла речи бота"
        if status == QtMultimedia.QMediaPlayer.EndOfMedia:
            self.media_player.stop()
            if self.temp_audio_file and os.path.exists(self.temp_audio_file):
                try:
                    os.unlink(self.temp_audio_file)
                except Exception as e:
                    print(f"Ошибка удаления временного файла: {e}")
                self.temp_audio_file = None

    def toggle_v_input(self):
        "обработка нажатия на микрофон"
        if self.voice_button_state:
            self.stop_v_input()
        else:
            self.start_v_input()

    def start_v_input(self):
        "включение гс ввода с проверкой микрофона"
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        except Exception:
            msg = "Проверьте подключение микрофона."
            self.add_messg_chat(msg, "bot")
            self.scroll_bottom()
            QtWidgets.QApplication.processEvents()
            self._play_speech(msg)
            self.toolButton_9.setChecked(False)
            return
        self.voice_button_state = True
        self.toolButton_9.setChecked(True)
        msg = "Голосовой ввод активирован. Чем могу помочь?"
        self.add_messg_chat(msg, "bot")
        self.scroll_bottom()
        QtWidgets.QApplication.processEvents()
        self.play_v_assistant_speech(msg)
        self.voice_thread = QtCore.QThread()
        self.voice_worker = VoiceRecognitionWorker(self.recognizer, self.microphone)
        self.voice_worker.moveToThread(self.voice_thread)
        self.voice_worker.message.connect(self.new_user_message.emit)
        self.voice_thread.started.connect(self.voice_worker.run)
        self.voice_thread.finished.connect(self.voice_worker.deleteLater)
        self.voice_thread.start()

    def stop_v_input(self):
        "выключение голосового ввода"
        msg = "Голосовой ввод отключен."
        self.add_messg_chat(msg, "bot")
        self.voice_button_state = False
        self.toolButton_9.setChecked(False)
        if self.voice_worker:
            self.voice_worker.stop()
        if self.voice_thread and self.voice_thread.isRunning():
            self.voice_thread.quit()
            if not self.voice_thread.wait(3000):
                self.voice_thread.terminate()
                self.voice_thread.wait()

    def reply(self, text, turn_off_voice=False):
        "Ответ бота и его озвучка"
        self.add_messg_chat(text, "bot")
        self.scroll_bottom()
        QtWidgets.QApplication.processEvents()
        if self.voice_button_state:
            self.play_v_assistant_speech(text)
            if turn_off_voice:
                self.stop_v_input()

    def process_user_request(self, request):
        "обработка запроса пользователя и поиск ответа."
        command = request.lower().strip()
        greetings = ["привет", "здравствуйте", "добрый день"]
        farewells = ["пока", "до свидания", "выход", "стоп"]
        if command in greetings:
            self.reply("Чем могу помочь?")
            return
        if command in farewells:
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
                self.reply("Нашла информацию. Открываю.", turn_off_voice=True)
            except Exception as e:
                err = f"Не удалось открыть ссылку: {target_url}. Ошибка: {e}"
                self.add_messg_chat(err, "bot")
                if self.voice_button_state:
                    self.play_v_assistant_speech("Не удалось открыть ссылку")
        else:
            self.reply("Извините, я не поняла ваш запрос. Попробуйте переформулировать.")

    def closeEvent(self, event):
        "закрытие"
        if self.voice_button_state:
            self.stop_v_input()
        if self.media_player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.media_player.stop()
        if self.temp_audio_file and os.path.exists(self.temp_audio_file):
            try:
                os.unlink(self.temp_audio_file)
            except:
                pass
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MyPersonalAssistantApp()
    window.show()
    sys.exit(app.exec_())