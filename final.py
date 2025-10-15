import RPi.GPIO as GPIO     ###various modules for speech-to-text, text-to-speech, lcd screen,and GPIO 
import time
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import random
import whisper #stt
import speech_recognition as sr #stt
import openai #stt
import sounddevice 
from gtts import gTTS #tts
from rpi_lcd import LCD #lcd screen
from io import BytesIO
from pygame import mixer #sound output from USB speaker 

MIC_PIN = 26

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(MIC_PIN, GPIO.IN) #setting up microphone input on pin 26 
lcd = LCD()
lcd.clear()
text_output = "hello world, hello world! hello world."


model = whisper.load_model("tiny.en")
recognizer = sr.Recognizer()

AM = open("hate.txt", 'r')
script = AM.read()
bee = open("bee.txt", 'r')
script2 = bee.read()
walter = open("walter.txt", 'r')
script3 = walter.read()

def lcd_text(txt, spd):
    chunk = 0
    line = 1
    l = line 
    for i in range(len(txt)):
        lcd.text(txt[chunk * 16 : i + 1], l)
        time.sleep(spd)
        if (i + 1) % 32 == 0:
            time.sleep(spd * 5)
            lcd.clear()
            time.sleep(spd * 5)
        if (i + 1) % 16 == 0:
            chunk += 1
            line += 1
            time.sleep(spd * 5)
        if line % 2 == 0:
            l = 2
        else:
            l = 1 


            
    #goal is to create a scrolling effect.
    time.sleep(spd * 10) 
    lcd.clear() 

def listen():
    while True:
        try:
            with sr.Microphone() as source:
                print("Speaketh.")
                audio = recognizer.listen(source)

            with open("temp.wav", "wb") as f:
                f.write(audio.get_wav_data())

            print("Processing...")
            result = model.transcribe("temp.wav", fp16 = False)
            print("Complete.")
            text = result["text"]
            return text
        except Exception as e:
            print("Error", e)

def process(txt):
    mp3_fp = BytesIO()
    tts = gTTS(txt, lang='en', tld='co.uk')
    tts.write_to_fp(mp3_fp)
    return mp3_fp
def speak(txt):
    mixer.init()
    print("Processing...")
    sound = process(txt)
    print("Complete.")
    sound.seek(0)
    mixer.music.load(sound, "mp3")
    mixer.music.play()
    time.sleep(60)

speech = listen()
print("You said:", speech)
lcd_text(f"You said: {speech}", 0.05)
speak(f"You said: {speech}")