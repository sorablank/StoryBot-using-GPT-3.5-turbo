import gradio as gr
import openai
import pyttsx3
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import threading
from gtts import gTTS
import os
import pygame

openai.api_key = ""

messages = [
    {"role": "system", "content": "You are a gruesome horror story writer. Give prompt in less than 1000 words. Include a name for the story in the start"},
]


def generate_midjourney_prompt(transcript_text):
    midjourney_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Create a detailed midjourney prompt based on the next few lines. Keep it under 50 words"},
            {"role": "user", "content": transcript_text},
        ]
    )
    return midjourney_response["choices"][0]["message"]["content"]


def transcribe(audio):
    global messages
    
    audio_file = open(audio, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    print(transcript)
    
    messages.append({"role": "user", "content": transcript["text"]})
    print(messages)

    
    midjourney_prompt = generate_midjourney_prompt(transcript["text"])
    chat_transcript = messages_to_text(messages)
    image = create_transcript_image(midjourney_prompt)
    

    
    engine = pyttsx3.init()
     
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    system_message = response["choices"][0]["message"]["content"]
    
    
    pygame.mixer.init()
    myobj = gTTS(text=system_message, lang='en', slow=False)

    # Saving the converted audio in an mp3 file named 'welcome'
    myobj.save("welcome.mp3")

    
    pygame.mixer.music.load("welcome.mp3")
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        continue
    messages.append({"role": "assistant", "content": system_message})
    
    return chat_transcript+'\n'+'Response: '+system_message,image


def create_transcript_image(transcript_text):
    
    response = openai.Image.create(
        prompt="Create a realistic image based on the following description:" + transcript_text,
        n=1,
        size="1024x1024"
    )

    image_bytes = response['data'][0]['url']

    return image_bytes


def messages_to_text(messages):
    chat_transcript = ""
    for message in messages:
        if message['role'] != 'system':
            chat_transcript += message['role'] + ": " + message['content'] + "\n\n"
    return chat_transcript


ui = gr.Interface(fn=transcribe, inputs=gr.Audio(source="microphone", type="filepath"), outputs=["text", "image"])
ui.launch()
