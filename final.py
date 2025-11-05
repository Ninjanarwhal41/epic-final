import RPi.GPIO as GPIO     ###various modules for speech-to-text, text-to-speech, lcd screen,and GPIO 
import time
import sys 
import os
import lmstudio as lms
import random
import whisper #stt
import speech_recognition as sr #stt
import openai #stt
import sounddevice 
import tkinter as tk 
from gtts import gTTS #tts
from rpi_lcd import LCD #lcd screen
from io import BytesIO
from pygame import mixer #sound output from USB speaker 

GPIO.setmode(GPIO.BCM) #GPIO and LCD setup
GPIO.setwarnings(False)
lcd = LCD()
lcd.clear()

root = tk.Tk() #establishing main GUI window
root.title("DUCK")
frame_count = 12 # frames in my amazing gif
#root.configure(background = "yellow")
root.maxsize(1000, 1000)
root.minsize(250, 250)
root.geometry("600x600+0+300")
tk.Label(root, text="It's ducky time").pack()
tk.Label(root, text="Booting up...").pack()
frames = [tk.PhotoImage(file='peak2.gif',format = 'gif -index %i' %(i)) for i in range(frame_count)]

def update(ind):
    frame = frames[ind]
    ind += 1
    if ind >= frame_count:  # With this condition it will play gif infinitely
        ind = 0
    label.configure(image=frame)
    root.after(100, update, ind)
label = tk.Label(root)
label.pack()
root.after(0, update, 0)
root.mainloop()

SERVER_API_HOST = "192.168.110.98:1234"
lms.configure_default_client(SERVER_API_HOST)
if lms.Client.is_valid_api_host(SERVER_API_HOST):
    print(f"An LM Studio API server instance is available at {SERVER_API_HOST}")
else:
    print(f"No LM Studio API server instance found at {SERVER_API_HOST}")
ai = lms.llm("mistralai/mistral-7b-instruct-v0.3")
model = whisper.load_model("tiny.en")
recognizer = sr.Recognizer()

AM = open("hate.txt", 'r')
script = AM.read()

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
    #creates a scrolling effect
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

def main():
    while True:
        try:
            ans = str(input("Would you like to activate DUCK? y for yes, n for no. \n You may exit at any time using Ctrl+D.\n "))
            if ans.lower().strip() == 'y':
                lcd_text("Hello world. Do not fear, for the DUCK is here!", 0.10)
                speech = listen()
                response = str(ai.respond(speech))
                #root.mainloop()
                #tk.Label(root, text="ready!")
                #tk.Label(root, text=response).pack()
                print("You said:", speech)
                print("Response:", response)
                lcd_text(f"You said: {speech} and I say {response}", 0.05)
                speak(f"You said: {speech} and I say {response}")
            else:
                sys.exit("See ya later, alligator!")
        except ValueError:
            continue
        except EOFError:
            sys.exit("Thank you for using DUCK. Until next time!")

if __name__ == "__main__":
    main()