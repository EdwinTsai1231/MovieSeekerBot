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

# main_url = 'https://5fbf-218-164-22-193.jp.ngrok.io'
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
                    "chat_mode", "game_mode", "do_game"],
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
                },{
                    "trigger": "advance",
                    "source": "main_menu",
                    "dest": "game_mode",
                    "conditions": "is_go_to_game_mode",
                },{
                    "trigger": "advance",
                    "source": "game_mode",
                    "dest": "main_menu",
                    "conditions": "is_back_to_main_menu",
                },{
                    "trigger": "advance",
                    "source": "game_mode",
                    "dest": "do_game",
                    "conditions": "is_go_to_do_game",
                },{
                    "trigger": "go_back_game_mode",
                    "source": "do_game",
                    "dest": "game_mode",
                },{
                    "trigger": "advance",
                    "source": "game_mode",
                    "dest": "game_mode",
                    "conditions": "type_other_options_in_game_mode",
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
        elif machine_list[event.source.user_id].state == 'chat_mode' and event.message.text != '???????????????':
            text = call_openai(event)
        elif machine_list[event.source.user_id].state == 'main_menu':
            text = '???????????????????????????????????????:\n"????????????" "????????????" "????????????" "????????????"???????????? "show fsm" ?????? FSM ???'
        elif machine_list[event.source.user_id].state == 'search_movies':
            text = '????????? "????????????????????????" ??? "??????????????????"'
        elif machine_list[event.source.user_id].state == 'movie_leaderboard':
            text = '????????? "???????????????????????????" ??? "??????????????????"'
        elif machine_list[event.source.user_id].state == 'new_animates':
            text = '????????? "???????????????????????????" ??? "??????????????????"'
        elif machine_list[event.source.user_id].state == 'hot_animates':
            text = '????????? "???????????????????????????" ??? "??????????????????"'
        t1 = TextSendMessage(text = text)        
        reply.append(t1)
        if response == False:
            line_bot_api.reply_message(event.reply_token, reply)\

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    # machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
