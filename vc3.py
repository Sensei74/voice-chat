import asterisk.manager
import speech_recognition as sr
import os
from google.cloud import speech
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import logging
from flask import Flask, render_template, request
import threading

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Настройка подключения к Asterisk PBX
manager = asterisk.manager.Manager()
manager.connect('host')
manager.login('username', 'password')

# Настройка распознавания речи (Google Speech-to-Text API)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/google-credentials.json"
speech_client = speech.SpeechClient()

# Настройка базы данных (SQLAlchemy)
Base = declarative_base()

class Call(Base):
    __tablename__ = 'calls'
    id = Column(Integer, primary_key=True)
    transcript = Column(Text)

engine = create_engine('sqlite:///calls.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

# Веб-сервер Flask для просмотра транскриптов
app = Flask(__name__)

@app.route('/')
def index():
    session = Session()
    calls = session.query(Call).all()
    session.close()
    return render_template('index.html', calls=calls)

# Функция для обработки входящих звонков
def handle_incoming_call(channel, data):
    # Запись звонка
    recording_path = f'/path/to/recordings/{data.get("uniqueid")}.wav'
    call_recording = channel.recordCall(recording_path)
    
    # Распознавание речи из записи
    with open(recording_path, 'rb') as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=8000,
        language_code='ru-RU'
    )
    response = speech_client.recognize(config=config, audio=audio)
    
    transcript = ''
    for result in response.results:
        transcript += result.alternatives[0].transcript
    
    # Сохранение транскрипта в базе данных
    session = Session()
    call = Call(transcript=transcript)
    session.add(call)
    session.commit()
    session.close()
    
    # Удаление временного файла записи
    os.remove(recording_path)
    
    logging.info(f'Call transcribed: {transcript}')

# Регистрация обработчика событий в Asterisk
manager.register_event('Newchannel', handle_incoming_call)

# Запуск веб-сервера и цикла обработки событий Asterisk в отдельных потоках
if __name__ == '__main__':
    app_thread = threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
    app_thread.start()
    
    logging.info('Starting Asterisk event loop')
    try:
        manager.run()
    except KeyboardInterrupt:
        logging.info('Exiting')