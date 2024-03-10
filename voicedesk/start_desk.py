from threading import Thread
from time import sleep
import RPi.GPIO as GPIO
from google.cloud import texttospeech
import os
import time
from google.cloud import vision
import io
import cv2
from openai import OpenAI
import base64
import requests
from pydub import AudioSegment
from pydub.playback import play
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)
def summrize(txt):
    secret_key = "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"
    if secret_key is None:
        raise ValueError("No SECRET_KEY found in environment variables")

    client = OpenAI(api_key = secret_key)
    messages = [
        {"role": "system", "content": "너는 최고의 요약도우미야"},
        {"role": "user", "content": f"[{txt}] + 이거 요약해줘"}
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    response_content = response.choices[0].message.content
    return response_content


def describe_image_with_openai(image_path, txt):

    api_key ="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"
    if api_key is None:
        raise ValueError("No SECRET_KEY found in environment variables")
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    base64_image = encode_image(image_path)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": f"[{txt}]이게 이미지에 있는 글 내용인데 이거 참고해서, 이 책에 있는 표, 그래프, 그림등의 자료를 정확하게 특수문자 쓰지 말고 글로 설명해줘"
              },
              {
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/jpeg;base64,{base64_image}"
                }
              }
            ]
          }
        ],
        "max_tokens": 1000
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    content = response.json()['choices'][0]['message']['content']

    return content
def capture_and_split_image():
    if not cap.isOpened():
        print("camera is not opened")
    else:
        ret, original_image = cap.read()
        if not ret:
            print("can't capture")
        else:
            for i in range(25):
                ret, original_image = cap.read()
    # 이미지를 두 부분으로 나누기
    height, width = original_image.shape[:2]
    half_width = width // 2
    left_half = original_image[:, :half_width]
    right_half = original_image[:, half_width:]

    # 각 부분을 별도의 파일로 저장
    cv2.imwrite("/home/jimin/voicedesk/left.png", left_half)
    cv2.imwrite("/home/jimin/voicedesk/right.png", right_half)
    cap.release()

def detect_text(path):
    """Detects text in the file."""
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.path.join("/home/jimin/voicedesk/google_api.json")
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

        image = vision.Image(content=content)

        response = client.text_detection(image=image)
        full_text_annotation = response.full_text_annotation
        if full_text_annotation:
            full_text = full_text_annotation.text
        else:
            return "No text found in the image."
        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
        full_text = full_text.replace("\n", "")
        return full_text
def play_wav(file_path):
    audio = AudioSegment.from_file(file_path, format = "wav")
    play(audio)

def text_to_speech(text):
    try:
        client = texttospeech.TextToSpeechClient.from_service_account_json("/home/jimin/voicedesk/google_api.json")

        input_text = texttospeech.SynthesisInput(text=text)
        voice_selection = texttospeech.VoiceSelectionParams(
            language_code= "ko-KR",
            name="ko-KR-Wavenet-A"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )

        response = client.synthesize_speech(
            input=input_text,
            voice=voice_selection,
            audio_config=audio_config
        )

        with open("/home/jimin/voicedesk/output.wav", "wb") as out:
          out.write(response.audio_content)
          print('Audio content written to file')
        play_wav("/home/jimin/voicedesk/output.wav")
    except Exception as e:
        print("오류 발생:", str(e))
content = str()
passage1 = str()
passage2 = str()
def read():
    print("read start")
    play_wav("/home/jimin/voicedesk/read.wav")
    global content
    global passage1
    global passage2
    content = ""
    passage1 = ""
    passage2 = ""
    capture_and_split_image()
    passage1 = detect_text("/home/jimin/voicedesk/left.png")
    if passage1  =="No text found in the image.":
        func1 = Thread(target=play_wav, args = ("/home/jimin/voicedesk/notice.wav",))
        func1.start()
        passage2 = detect_text("/home/jimin/voicedesk/right.png")
        func1.join()
    else:
        func1 = Thread(target=text_to_speech, args = (passage1,))
        func1.start()
        passage2 = detect_text("/home/jimin/voicedesk/right.png")
        func1.join()
    if passage2  =="No text found in the image.":
        func2 = Thread(target=play_wav, args = ("/home/jimin/voicedesk/notice.wav",))
        func2.start()
        func2.join()
    else:   
        func2 = Thread(target=text_to_speech, args = (passage2,))
        func2.start()
        func2.join()
    content = passage1 + passage2

def gpt_summrize():
    print("summrize start")
    play_wav("/home/jimin/voicedesk/summurize.wav")
    global content
    summrized_passage = summrize(content)
    func = Thread(target=text_to_speech, args = (summrized_passage,))
    func.start()

def gpt_image_interpret():
    print("image start")
    global passage1, passage2
    play_wav("/home/jimin/voicedesk/detect_image.wav")
    first_page_image = describe_image_with_openai(image_path="/home/jimin/voicedesk/left.png", txt=passage1)
    func1_5 = Thread(target=play_wav, args=("/home/jimin/voicedesk/left_page.wav",))
    func1 = Thread(target=text_to_speech, args=(first_page_image,))

    func1_5.start()
    func1_5.join()  
    sleep(1)
    func1.start() 

    second_page_image = describe_image_with_openai(image_path="/home/jimin/voicedesk/right.png", txt=passage2)
    func2_5 = Thread(target=play_wav, args=("/home/jimin/voicedesk/right_page.wav", ))
    func2 = Thread(target=text_to_speech, args=(second_page_image,))
    func1.join() 
    func2_5.start()
    func2_5.join()  
    sleep(1)
    func2.start()
    func2.join()   

play_wav("/home/jimin/voicedesk/workstart.wav")
GPIO.setmode(GPIO.BCM)

BUTTON_PIN_1 = 17
BUTTON_PIN_2 = 23
BUTTON_PIN_3 = 18
GPIO.setup(BUTTON_PIN_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_PIN_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(BUTTON_PIN_3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
try:
    while True:
        if GPIO.input(BUTTON_PIN_1) == GPIO.HIGH:
            read()
            sleep(1)
        if GPIO.input(BUTTON_PIN_2) == GPIO.HIGH:
            gpt_summrize()
            sleep(1)
        if GPIO.input(BUTTON_PIN_3) == GPIO.HIGH:
            gpt_image_interpret()
            sleep(1)
        
        
        
except KeyboardInterrupt:
    GPIO.cleanup()