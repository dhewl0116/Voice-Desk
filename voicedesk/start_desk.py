from threading import Thread
from time import sleep
import RPi.GPIO as GPIO
import os
import time
from chatgpt import summrize, describe_image_with_openai
from ocr import detect_text
from speak import play_wav, text_to_speech
from capture import capture_and_split_image


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
