import speech_recognition as sr

# Создаем распознаватель речи
r = sr.Recognizer()

# Функция для преобразования речи в текст
def speech_to_text():
    with sr.Microphone() as source:
        print("Говорите...")
        audio = r.listen(source)

    try:
        text = r.recognize_google(audio, language="ru-RU")
        print(f"Распознанный текст: {text}")
    except sr.UnknownValueError:
        print("Не удалось распознать речь")
    except sr.RequestError as e:
        print(f"Ошибка сервиса распознавания речи; {e}")

# Вызываем функцию
speech_to_text()