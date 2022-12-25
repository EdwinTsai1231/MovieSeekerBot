import os
# import openai

from linebot import LineBotApi, WebhookParser
from linebot.models import VideoSendMessage,MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ImageCarouselColumn,CarouselTemplate, ImageCarouselTemplate, URITemplateAction, ButtonsTemplate, MessageTemplateAction, ImageSendMessage
from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction
import openai
import random

channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)

def send_text_message(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))

    return "OK"
def send_text_multiple_message(reply_token, textList):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, textList)
    return "OK"

def send_text_message_AI(reply_token, text):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=text,
        temperature=0,
        max_tokens =100
    )
    
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token,TextSendMessage(text=response.choices[0].text.strip()))

    return "OK"
def send_video_message(reply_token, videoUrl, preUrl):
    line_bot_api = LineBotApi(channel_access_token)
    message = VideoSendMessage(
        original_content_url = videoUrl,
        preview_image_url = preUrl
    )
    line_bot_api.reply_message(reply_token, message)
    return "OK"

def send_carousel_message(reply_token, col):
    line_bot_api = LineBotApi(channel_access_token)
    message = TemplateSendMessage(
        alt_text = '*選單*',
        template = CarouselTemplate(columns = col)
    )
    line_bot_api.reply_message(reply_token, message)

    return "OK"

def send_button_message(reply_token, title, text, btn, url):
    line_bot_api = LineBotApi(channel_access_token)
    message = TemplateSendMessage(
        alt_text='button template',
        template = ButtonsTemplate(
            title = title,
            text = text,
            thumbnail_image_url = url,
            actions = btn
        )
    )
    line_bot_api.reply_message(reply_token, message)

    return "OK"

def send_image_message(reply_token, url):
    line_bot_api = LineBotApi(channel_access_token)
    message = ImageSendMessage(
        original_content_url = url,
        preview_image_url = url
    )
    line_bot_api.reply_message(reply_token, message)

    return "OK"

def call_openai(event):
    completed_text = ""
    openai_key = os.getenv("OPENAI_KEY", None)
    openai.api_key = openai_key
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt= event.message.text,
        max_tokens=128,
        temperature=0.5,
    )
    completed_text = response["choices"][0]["text"].replace('\n', '')
    
    return completed_text   


def do_game(event, text):
    if text == '石頭':
        ran = random.randint(1, 3)
        if (ran == 2):
            send_text_message(event.reply_token, '剪刀\n你贏了!')
        elif (ran == 3):
            send_text_message(event.reply_token, '布\n我贏了!')
        else:
            send_text_message(event.reply_token, '石頭\n平手')
    elif text == '剪刀':
        ran = random.randint(1, 3)
        if (ran == 3):
            send_text_message(event.reply_token, '布\n你贏了!')
        elif (ran == 1):
            send_text_message(event.reply_token, '石頭\n我贏了!')
        else:
            send_text_message(event.reply_token, '剪刀\n平手')
    elif text == '布':
        ran = random.randint(1, 3)
        if (ran == 1):
            send_text_message(event.reply_token, '石頭\n你贏了!')
        elif (ran == 2):
            send_text_message(event.reply_token, '剪刀\n我贏了!')
        else:
            send_text_message(event.reply_token, '布\n平手')
    
    return True
