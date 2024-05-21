import requests
from google.cloud import speech

# Учетные данные для доступа к API Битрикс24
BITRIX_URL = 'https://your_bitrix24.bitrix24.com/rest/1/xxxxx/'
BITRIX_AUTH_CODE = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# Учетные данные для Google Speech-to-Text API
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/google-credentials.json"
speech_client = speech.SpeechClient()

# Функция для обработки входящих звонков в Битрикс24
def handle_incoming_call(call_data):
    # Получение записи звонка из Битрикс24 или запись звонка самостоятельно
    recording_path = '/path/to/recording.wav'
    
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
    
    # Сохранение транскрипта в Битрикс24 или в базе данных
    save_transcript(transcript)

# Получение событий о входящих звонках из API Битрикс24
def get_incoming_calls():
    url = BITRIX_URL + 'voximplant.callView.getList'
    headers = {'Authorization': 'Bearer ' + BITRIX_AUTH_CODE}
    response = requests.get(url, headers=headers)
    calls = response.json()['result']
    for call in calls:
        handle_incoming_call(call)

# Основной цикл
while True:
    get_incoming_calls()
    # Задержка перед следующей проверкой
    time.sleep(60)