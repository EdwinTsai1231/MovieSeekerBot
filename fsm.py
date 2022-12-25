from transitions.extensions import GraphMachine
from linebot.models import MessageAction,MessageEvent, TextMessage, TextSendMessage, VideoSendMessage
from linebot.models import PostbackAction,URIAction, CarouselColumn,ImageCarouselColumn, URITemplateAction, MessageTemplateAction
from spider import SearchMovies, show_hot_movies, search_animations, show_hot_animates

from utils import send_text_message, send_button_message, send_carousel_message, do_game

search_movies = ['現在熱映電影', '即將上映電影']
movie_menu_options = ['現在熱映電影', '即將上映電影', '台灣票房榜', '返回主目錄']
animates_menu_options = ['本季新作', '人氣排行', '評分排行', '返回主目錄']
game_mode_options = ['剪刀', '石頭', '布', '返回主目錄']

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)


    def is_back_to_main_menu(self, event):
        text = event.message.text
        return text == '返回主目錄'

    def is_going_to_movie_menu(self, event):
        text = event.message.text
        return text == '電影目錄'

    def type_other_options_in_movie_menu(self, event):
        text = event.message.text
        return not text in movie_menu_options

    def type_other_options_in_game_mode(self, event):
        text = event.message.text
        return not text in movie_menu_options

    def type_other_options_in_animates_menu(self, event):
        text = event.message.text
        return not text in animates_menu_options


    def is_back_to_movie_menu(self, event):
        text = event.message.text
        return text == '返回電影目錄'

    def is_back_to_animates_menu(self, event):
        text = event.message.text
        return text == '返回動畫目錄'

    def is_go_to_movie_leaderboard(self, event):
        text = event.message.text
        return text == '台北票房榜'
            

    def is_going_to_animates_menu(self, event):
        text = event.message.text
        return text == "動畫目錄"

    def is_going_to_search_movies(self, event):
        text = event.message.text
        return text in search_movies

    def is_go_to_new_animates(self, event):
        text = event.message.text
        return text == "本季新作"

    def is_go_to_game_mode(self, event):
        text = event.message.text
        return text == "遊戲模式"

    def is_back_to_animates_menu(self, event):
        text = event.message.text
        return text == "返回動畫目錄"
    
    def is_go_to_hot_animates(self, event):
        text = event.message.text
        return text == "人氣排行" or text == '評分排行'

    def is_going_to_chat_mode(self, event):
        text = event.message.text
        return text == "聊天模式"

    def on_enter_main_menu(self, event):
        reply_token = event.reply_token
        text = '已返回主目錄:\n請使用底下的主目錄選單選擇: "電影目錄" "動畫目錄" "聊天模式" "遊戲模式" 或 輸入 "show fsm" 顯示 FSM 圖'
        send_text_message(reply_token, text)

    def on_enter_chat_mode(self, event):
        reply_token = event.reply_token
        text = '已切換到聊天模式，輸入 "返回主目錄" 即會結束聊天模式'
        send_text_message(reply_token, text)

    def on_enter_movie_menu(self, event):
        reply_token = event.reply_token
        title = "請選擇要查詢\"現在熱映\"電影、\"即將上映\" 電影，或\"台北票房榜\""
        text = '下方選擇您的查詢方式'
        btn = [
            MessageTemplateAction(
                label = '現在熱映電影',
                text ='現在熱映電影'
            ),
            MessageTemplateAction(
                label = '即將上映電影',
                text = '即將上映電影'
            ),
            MessageTemplateAction(
                label = '台北票房榜',
                text = '台北票房榜'
            ),
            MessageTemplateAction(
                label = '返回主目錄',
                text = '返回主目錄'
            )
        ]
        url = 'https://cdn-icons-png.flaticon.com/512/2040/2040698.png'
        send_button_message(event.reply_token, title, text, btn, url)
    
    def on_enter_movie_leaderboard(self, event):
        reply_token = event.reply_token

        hot_movies = show_hot_movies()
        col = []
        c = CarouselColumn(
            thumbnail_image_url='https://static-00.iconduck.com/assets.00/champion-2-icon-256x256-l9sxi164.png',
            title= "台北票房榜",
            text='以下是台北票房榜的前三名',
            actions=[
                URIAction(
                    label='點我查看詳細票房榜',
                    uri= 'https://movies.yahoo.com.tw/chart.html'
                ),
                MessageAction(
                    label='返回電影目錄',
                    text='返回電影目錄'
                )
            ]
        )
        col.append(c)
        for i in range(3):
            if (hot_movies[i].web_src != ''):
                detail = '上映日期 ： ' + hot_movies[i].start_date + '\n' + '網友滿意度 ： ' + str((float(hot_movies[i].star)) * 20) + '\n' + '劇情介紹 ： ' + hot_movies[i].des
                if len(detail) > 60 :
                    detail = detail[0:56]+'...略'
                carousel_data = CarouselColumn(
                    thumbnail_image_url=hot_movies[i].img_src,
                    title=f"TOP{i+1}: "+hot_movies[i].name[0:40],
                    text=detail[0:60],
                    actions=[
                        URIAction(label='詳細內容', uri=hot_movies[i].web_src),
                        URIAction(label='預告片', uri=hot_movies[i].trailer_src),
                    ]
                )
                col.append(carousel_data)

        send_carousel_message(reply_token, col)
        
    def on_enter_search_movies(self, event):
        reply_token = event.reply_token
        search_method = event.message.text
        movies = SearchMovies(search_method)
        title = f'根據您的搜尋方式有{len(movies)}部電影' if len(movies) > 0 else f'很抱歉,我找不到資料'
        col = []
        c = CarouselColumn(
            thumbnail_image_url='https://cdn-icons-png.flaticon.com/512/31/31087.png',
            title=title,
            text='以下是為您提供的4部電影的資訊',
            actions=[
                MessageAction(
                    label='點我要搜尋其他的',
                    text= '現在熱映電影' if search_method == '現在熱映電影' else '即將上映電影'
                ),
                MessageAction(
                    label='返回電影目錄',
                    text='返回電影目錄'
                )
            ]
        )
        col.append(c)
        # print(movies)
        for movie in movies:
            des = f'{movie.state} {movie.start_date}\n{movie.typeInfo}\n{movie.des}'
            if len(des) > 60 :
                des = des[0:56]+'...略'
            
            c = CarouselColumn(
            thumbnail_image_url= f'{movie.img_src}',
            title = f'{movie.name}',
            text=f'{des}',
            actions=[
                URIAction(
                    label='查看更多',
                    uri=f'{movie.web_src}'
                ),
                URIAction(
                    label='觀看預告片',
                    uri=f'{movie.trailer_src}'
                )
            ]
            )
            col.append(c)
        send_carousel_message(reply_token, col)

    def on_enter_animates_menu(self, event):
        reply_token = event.reply_token
        title = "請選擇要查詢 \"本季新作\" \"人氣排行\" 或 \"評分排行\""
        text = '下方選擇您的查詢方式'
        btn = [
            MessageTemplateAction(
                label = '本季新作',
                text ='本季新作'
            ),
            MessageTemplateAction(
                label = '人氣排行',
                text = '人氣排行'
            ),
            MessageTemplateAction(
                label = '評分排行',
                text = '評分排行'
            ),
            MessageTemplateAction(
                label = '返回主目錄',
                text = '返回主目錄'
            )
        ]
        url = 'https://cdn-icons-png.flaticon.com/128/5651/5651147.png'
        send_button_message(reply_token, title, text, btn, url)

    def on_enter_new_animates(self, event):
        reply_token = event.reply_token
        animates_movie_list = search_animations()
        col = []
        title = f'根據您的搜尋方式有4部動畫'
        c = CarouselColumn(
            thumbnail_image_url='https://cdn-icons-png.flaticon.com/512/31/31087.png',
            title=title,
            text='以下是為您提供的4部動畫的資訊',
            actions=[
                MessageAction(
                    label='點我要搜尋其他的',
                    text= '本季新作'
                ),
                MessageAction(
                    label='返回動畫目錄',
                    text='返回動畫目錄'
                )
            ]
        )
        col.append(c)
        for i in range(4):
            detail = animates_movie_list[i].start_date + '\n' + animates_movie_list[i].star + "　" + animates_movie_list[i].hot + "\n" + animates_movie_list[i].des
            carousel_data = CarouselColumn(
                thumbnail_image_url=animates_movie_list[i].img_src,
                title=animates_movie_list[i].name,
                text=detail[0:60],
                actions=[
                    URIAction(label='詳細內容', uri=animates_movie_list[i].web_src),
                    URIAction(label='詳細內容', uri=animates_movie_list[i].web_src)
                ]
            )
            col.append(carousel_data)

        send_carousel_message(reply_token, col)

    def on_enter_hot_animates(self, event):
        reply_token = event.reply_token
        chart = event.message.text
        animates_movie_list = show_hot_animates(chart)
        col = []
        title = f'根據您的搜尋方式列出前四名動畫'
        if chart == '人氣排行':
            target_url = 'https://acg.gamer.com.tw/billboard.php?t=2&p=anime'
        elif chart == '評分排行':
            target_url = 'https://acg.gamer.com.tw/billboard.php?t=3&p=anime'

        c = CarouselColumn(
            thumbnail_image_url='https://cdn-icons-png.flaticon.com/512/31/31087.png',
            title=title,
            text='以下是為您提供前四名動畫的資訊',
            actions=[
                URIAction(
                    label='點我查看詳細排行榜',
                    uri= target_url
                ),
                MessageAction(
                    label='返回動畫目錄',
                    text='返回動畫目錄'
                )
            ]
        )
        col.append(c)

        for i in range(4):
            detail = animates_movie_list[i].start_date + '\n' + animates_movie_list[i].star + "　" + animates_movie_list[i].hot + "\n" + animates_movie_list[i].des
            carousel_data = CarouselColumn(
                thumbnail_image_url=animates_movie_list[i].img_src,
                title=f'TOP{i+1}: ' + animates_movie_list[i].name,
                text=detail[0:60],
                actions=[
                    URIAction(label='詳細內容', uri=animates_movie_list[i].web_src),
                    URIAction(label='詳細內容', uri=animates_movie_list[i].web_src)
                ]
            )
            col.append(carousel_data)

        send_carousel_message(reply_token, col)
    
    def on_enter_game_mode(self, event):
        reply_token = event.reply_token
        title = "歡迎來到猜拳小遊戲\n請輸入'剪刀' '石頭' '布' 來進行猜拳"
        text = '下方選擇您要出的拳'
        btn = [
            MessageTemplateAction(
                label = '剪刀',
                text ='剪刀'
            ),
            MessageTemplateAction(
                label = '石頭',
                text = '石頭'
            ),
            MessageTemplateAction(
                label = '布',
                text = '布'
            ),
            MessageTemplateAction(
                label = '返回主目錄',
                text = '返回主目錄'
            )
        ]
        url = 'https://pic.616pic.com/ys_img/01/04/01/V8S3VobDbt.jpg'
        send_button_message(event.reply_token, title, text, btn, url)

    def is_go_to_do_game(self, event):
        text = event.message.text
        return text == '石頭' or text == '剪刀' or text == '布'

    def on_enter_do_game(self, event):
        do_game(event, event.message.text)
        self.go_back_game_mode(event)