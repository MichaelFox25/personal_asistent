import speech_recognition
import pyttsx3
import webbrowser
import os
engine = pyttsx3.init()
engine.setProperty('rate', 180)
voices = engine.getProperty('voices')
ru_voice_id = None
for voice in voices:
    print('===================')
    print('name:', voice.name)
    print('Language:', voice.languages)
    print('ID:', voice.id)
    if 'ru' in str(voice.languages).lower() or 'russian' in voice.name.lower():
        ru_voice_id = voice.id
if ru_voice_id is not None:
    engine.setProperty('voice', ru_voice_id)
    engine.say('Привет')
else:
    print('Русский голос не найден. Установите русский голос в вашей системе.')
engine.runAndWait()
def play_v_assistant_speech(text_to_speech):
    ttsEngine.say(str(text_to_speech))
    ttsEngine.runAndWait()
def record_recognize_audio(*args: tuple):
    with microphone:
        recognized_data = ""
        recognizer.adjust_for_ambient_noise(microphone, duration=2)
        try:
            print("Запись голоса... Listening...")
            audio = recognizer.listen(microphone, 5, 5)
            with open("microphone-results.wav", "wb") as file:
                file.write(audio.get_wav_data())
        except speech_recognition.WaitTimeoutError:
            print("Проверьте ,пожалуйста, подключение микрофона. Can you check if your microphone is on, please?")
            return
        recognizer.pause_threshold = 2
        try:
            print("Начало распознавания... Started recognition...")
            recognized_data = recognizer.recognize_google(audio, language="ru").lower()
        except speech_recognition.UnknownValueError:
            pass
        return recognized_data
if __name__ == "__main__":
    recognizer = speech_recognition.Recognizer()
    microphone = speech_recognition.Microphone()
    ttsEngine = pyttsx3.init()
    while True:
        voice_input = record_recognize_audio()
        print (voice_input)
        command = voice_input
        if command == "привет":
            print("Что вы хотите сделать?")
            engine.say("Что вы хотите сделать")
        if command == "расскажи про поступление":
            engine.say("открываю сайт")
            webbrowser.open ('https://new.vyatsu.ru/')
        if command == "открой нормативные акты":
            play_v_assistant_speech("открываю сайт")
            webbrowser.open('https://new.vyatsu.ru/sveden/document/')
        if command == "расскажи про институты факультеты и кафедры":
            play_v_assistant_speech("открываю сайт")
            webbrowser.open('https://www.vyatsu.ru/studentu-1/nauka-i-praktika.html')
        if command == "контакты":
            play_v_assistant_speech("открываю сайт")
            webbrowser.open('https://www.vyatsu.ru/contacts')
        if command == "расскажи про преподавателей":
            play_v_assistant_speech("открываю сайт")
            webbrowser.open('https://www.vyatsu.ru/studentu-1/kto-est-kto-v-vyatgu.html')
        if command == "какие новости":
            play_v_assistant_speech("открываю сайт")
            webbrowser.open('https://www.vyatsu.ru/internet-gazeta.html')
        if command == "покажи расположение корпусов":
            play_v_assistant_speech("открываю сайт")
            webbrowser.open('https://www.vyatsu.ru/studentu-1/pervokursniku/adresa-i-telefonyi-uchebnyih-korpusov-fakul-tetov.html')
        if command == "покажи расписание":
            play_v_assistant_speech("открываю сайт")
            webbrowser.open('https://www.vyatsu.ru/studentu-1/spravochnaya-informatsiya/raspisanie.html')
        if command == "покажи календарный учебный график":
            play_v_assistant_speech("открываю сайт")
            webbrowser.open('https://www.vyatsu.ru/sotrudniku/doska/grafiki-uchebnogo-protsessa-na-2015-2016-uchebnyiy.html')
        if command == "расскажи про колледж":
            play_v_assistant_speech("открываю сайт")
            webbrowser.open('https://www.vyatsu.ru/nash-universitet/obrazovatelnaya-deyatel-nost/kolledzh. html')
