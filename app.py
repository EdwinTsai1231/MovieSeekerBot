import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import graphviz
from dotenv import load_dotenv

from fsm import TocMachine
from utils import send_text_message, call_openai, send_image_message

main_url = 'https://movieseekerbot.onrender.com'

machine_list = {}



app = Flask(__name__, static_url_path="")
load_dotenv()

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

#pyreq
@app.route("/callback", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue

        if event.source.user_id not in machine_list:
            machine_list[event.source.user_id] = TocMachine(
            states=["main_menu",
                    "movie_menu", "search_movies", "movie_leaderboard",
                    "animates_menu", "new_animates", "hot_animates",
                    "chat_mode"],
            transitions=[
                {
                    "trigger": "advance",
                    "source": "main_menu",
                    "dest": "movie_menu",
                    "conditions": "is_going_to_movie_menu",
                },
                {
                    "trigger": "advance",
                    "source": "main_menu",
                    "dest": "animates_menu",
                    "conditions": "is_going_to_animates_menu",
                },
                {
                    "trigger": "advance",
                    "source": "movie_menu",
                    "dest": "search_movies",
                    "conditions": "is_going_to_search_movies",
                },{
                    "trigger": "advance",
                    "source": "search_movies", 
                    "dest": "search_movies",
                    "conditions": "is_going_to_search_movies",
                },{
                    "trigger": "advance",
                    "source": "search_movies", 
                    "dest": "movie_menu",
                    "conditions": "is_back_to_movie_menu",
                },{
                    "trigger": "advance",
                    "source": "movie_menu", 
                    "dest": "main_menu",
                    "conditions": "is_back_to_main_menu",
                },{
                    "trigger": "advance",
                    "source": "movie_menu", 
                    "dest": "movie_leaderboard",
                    "conditions": "is_go_to_movie_leaderboard",
                },{
                    "trigger": "advance",
                    "source": "movie_menu",
                    "dest": "movie_menu",
                    "conditions": "type_other_options_in_movie_menu",
                },{
                    "trigger": "advance",
                    "source": "movie_leaderboard",
                    "dest": "movie_menu",
                    "conditions": "is_back_to_movie_menu",
                },{
                    "trigger": "advance",
                    "source": "animates_menu",
                    "dest": "new_animates",
                    "conditions": "is_go_to_new_animates",
                },{
                    "trigger": "advance",
                    "source": "new_animates",
                    "dest": "new_animates",
                    "conditions": "is_go_to_new_animates",
                },{
                    "trigger": "advance",
                    "source": "new_animates",
                    "dest": "animates_menu",
                    "conditions": "is_back_to_animates_menu",
                },{
                    "trigger": "advance",
                    "source": "animates_menu",
                    "dest": "hot_animates",
                    "conditions": "is_go_to_hot_animates",
                },{
                    "trigger": "advance",
                    "source": "hot_animates",
                    "dest": "animates_menu",
                    "conditions": "is_back_to_animates_menu",
                },{
                    "trigger": "advance",
                    "source": "animates_menu",
                    "dest": "main_menu",
                    "conditions": "is_back_to_main_menu",
                },{
                    "trigger": "advance",
                    "source": "animates_menu",
                    "dest": "animates_menu",
                    "conditions": "type_other_options_in_animates_menu",
                },{
                    "trigger": "advance",
                    "source": "main_menu",
                    "dest": "chat_mode",
                    "conditions": "is_going_to_chat_mode",
                },{
                    "trigger": "advance",
                    "source": "chat_mode",
                    "dest": "main_menu",
                    "conditions": "is_back_to_main_menu",
                }
            ],
            initial="main_menu",
            auto_transitions=False,
            show_conditions=True,
        )
        
        response = machine_list[event.source.user_id].advance(event)
        reply = []
        text = ""
        if event.message.text == 'show fsm':
            send_image_message(event.reply_token, main_url + "/show-fsm")            
        elif machine_list[event.source.user_id].state == 'chat_mode' and event.message.text != '返回主目錄':
            text = call_openai(event)
        elif machine_list[event.source.user_id].state == 'main_menu':
            text = '請使用底下的主目錄選單選擇:\n"電影目錄" "動畫目錄" "聊天模式" 或是輸入 "show fsm" 顯示 FSM 圖'
        elif machine_list[event.source.user_id].state == 'search_movies':
            text = '請點選 "點我要搜尋其他的" 或 "返回電影目錄"'
        elif machine_list[event.source.user_id].state == 'movie_leaderboard':
            text = '請點選 "點我查看詳細票房榜" 或 "返回電影目錄"'
        elif machine_list[event.source.user_id].state == 'new_animates':
            text = '請點選 "點我查看詳細排行榜" 或 "返回動畫目錄"'
        elif machine_list[event.source.user_id].state == 'hot_animates':
            text = '請點選 "點我查看詳細排行榜" 或 "返回動畫目錄"'
        t1 = TextSendMessage(text = text)        
        reply.append(t1)
        if response == False:
            line_bot_api.reply_message(event.reply_token, reply)\

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    # machine_list[event.source.user_id].get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
