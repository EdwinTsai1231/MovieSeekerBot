import requests
import re
import random
import math
from bs4 import BeautifulSoup

headers ={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

class Movie:
    def __init__(self, name, img_src, web_src, trailer_src, typeInfo, state, start_date, description, hot = "", star = "") -> None:
        self.name = name
        self.img_src = img_src
        self.web_src = web_src
        self.trailer_src = trailer_src
        self.typeInfo = typeInfo
        self.state = state
        self.start_date = start_date
        self.des = description
        self.hot = hot
        self.star = star

def SearchMovies(search_method):
    searchWeb = 'https://www.ambassador.com.tw/'
    subWebTitle_1 = 'home/MovieList?Type=1'
    movie_entry_list = []
    subWeb = f'{searchWeb}'
    subWeb = subWeb+(f'{subWebTitle_1}')
    mainpage = requests.get(subWeb)
    main = BeautifulSoup(mainpage.text, 'html.parser')
    if search_method == '現在熱映電影':
        movie_list = main.find('div', class_='tabs-panel is-active', id='tab1').find('div', class_='grid-x grid-margin-x small-up-2 medium-up-3 large-up-4 movie-list').findAll('div', class_='cell')
        movie_list = random.sample(movie_list, 4)
        for element in movie_list:
            img_src = element.find('a').find('img')['src']
            title = element.find('div', class_='poster-info').find('a').text
            subsubWeb = searchWeb+element.find('a')['href']
            submainpage = requests.get(subsubWeb)
            submain = BeautifulSoup(submainpage.text, 'html.parser')
            movie_description = submain.find('div', class_ = 'cell small-12 medium-12 large-12 movie-info-box').find('p').text
            movie_type = submain.find('div', class_ = 'cell small-12 medium-12 large-12 movie-info-box').findAll('p', class_ = 'note')[1].text
            start_date = submain.find('div', class_ = 'cell small-12 medium-12 large-12 movie-info-box').findAll('p', class_ = 'note')[2].text
            trailer_url = submain.find('div', class_ = 'responsive-embed widescreen').find('iframe')['src']
            movie_entry = Movie(title, img_src, subsubWeb, trailer_url, movie_type, "現在熱映", start_date, movie_description)
            movie_entry_list.append(movie_entry)

    if search_method == '即將上映電影':
        movie_list = main.find('div', class_='tabs-panel', id='tab2').find('div', class_='grid-x grid-margin-x small-up-2 medium-up-3 large-up-4 movie-list').findAll('div', class_='cell')
        movie_list = random.sample(movie_list, 4)
        for element in movie_list:
            img_src = element.find('a').find('img')['src']
            title = element.find('div', class_='poster-info').find('a').text
            subsubWeb = searchWeb+element.find('a')['href']
            submainpage = requests.get(subsubWeb)
            submain = BeautifulSoup(submainpage.text, 'html.parser')
            movie_description = submain.find('div', class_ = 'cell small-12 medium-12 large-12 movie-info-box').find('p').text
            movie_type = submain.find('div', class_ = 'cell small-12 medium-12 large-12 movie-info-box').findAll('p', class_ = 'note')[1].text
            start_date = submain.find('div', class_ = 'cell small-12 medium-12 large-12 movie-info-box').findAll('p', class_ = 'note')[2].text
            trailer_url = submain.find('div', class_ = 'responsive-embed widescreen').find('iframe')['src']
            movie_entry = Movie(title, img_src, subsubWeb, trailer_url, movie_type, "即將上映", start_date, movie_description)
            movie_entry_list.append(movie_entry)

    return random.sample(movie_entry_list, 4)            
            
def show_hot_movies():
    requests.packages.urllib3.disable_warnings()
    target_url = 'https://movies.yahoo.com.tw/chart.html'
    rs = requests.session()
    res = rs.get(target_url, verify=False)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')

    movie_list = []
    for index, datas in enumerate(soup.select('div.rank_list.table.rankstyle1 div.tr')[0:4]):
        if index == 0:
            continue
        if index == 8:
            break
        movie_info = datas.find_all('div')
        non = movie_info[3].find('a')
        if non != None:
            movie_url = non['href']
            movie_rs = requests.session()
            movie_res = movie_rs.get(movie_url, verify=False)
            movie_res.encoding = 'utf-8'
            movie_soup = BeautifulSoup(movie_res.text, 'html.parser')
            movies_info_text = movie_soup.select_one('#story')
            movies_text = movies_info_text.text.lstrip()
            movie_img_data = movie_soup.select_one('div .movie_intro_foto img')
            img_link = movie_img_data['src']
        else:
            link = ''
            img_link = ''
            movies_text = ''
        if index == 1:
            movies_title = movie_info[3].find('h2').text
            date = movie_info[4].text
            non = movie_info[5].find('a')
            
            if non != None:
                movies_pre = non['href']
            else:
                movies_pre = ''
            non = movie_info[6].find('h6')
            
            if non != None:
                movies_star = non.text
            else:
                movies_star = ''
        else:
            movies_title = movie_info[3].find('div', 'rank_txt').text
            date = movie_info[5].text
            non = movie_info[6].find('a')
            
            if non != None:
                movies_pre = non['href']
            else:
                movies_pre = ''
            non = movie_info[7].find('h6')
            
            if non != None:
                movies_star = non.text
            else:
                movies_star = ''

        movie_list.append(Movie(movies_title, img_link, movie_url, movies_pre, "", "", date, movies_text, "", movies_star))
        
    return movie_list

def search_animations():
    
    requests.packages.urllib3.disable_warnings()
    target_url = 'https://acg.gamer.com.tw/quarterly.php'
    rs = requests.session()
    res = rs.get(target_url, headers=headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')

    anime_list = random.sample(soup.findAll('div', class_ = 'ACG-mainbox1'), 4)
    animates_movie_list = []
    
    for anime in anime_list:

        acg_info = anime.find('div', 'ACG-mainbox2')
        link = ('https:' + acg_info.find('h1', 'ACG-maintitle').find('a')['href'])
        animates_title = (acg_info.find('h1', 'ACG-maintitle').find('a').text)
        type = acg_info.find_all('ul')
        more_type = type[0].find_all('li')
        date = (more_type[0].text)
        animates_text = (type[1].li.text)
        img_link = (acg_info.find('div', 'ACG-mainbox2B').a.img['src'])
        star  = '評分：' + anime.find('div', 'ACG-mainbox4').find('p', 'ACG-mainboxpoint').span.text
        hot = '人氣：' + anime.find('div', 'ACG-mainbox4').find('p', 'ACG-mainplay').span.text

        animates_movie_list.append(Movie(animates_title, img_link, link, "", type, "", date, animates_text, star, hot))

    return animates_movie_list
    
def show_hot_animates(chart):
    requests.packages.urllib3.disable_warnings()
    
    if chart == '人氣排行':
        target_url = 'https://acg.gamer.com.tw/billboard.php?t=2&p=anime'
    elif chart == '評分排行':
        target_url = 'https://acg.gamer.com.tw/billboard.php?t=3&p=anime'

    rs = requests.session()
    res = rs.get(target_url, headers=headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')
    
    animates_movie_list = []
    anime_list = soup.findAll('div', class_ = 'ACG-mainbox1')[0:4]
    
    for anime in anime_list:
        
        acg_info = anime.find('div', 'ACG-mainbox2')
        link = ('https:' + acg_info.find('h1', 'ACG-maintitle').find('a')['href'])
        animates_title = (acg_info.find('h1', 'ACG-maintitle').find('a').text)
        type = acg_info.find_all('ul')
        more_type = type[0].find_all('li')
        date = (more_type[0].text)
        animates_text = (type[1].li.text)
        img_link = (acg_info.find('div', 'ACG-mainbox2B').a.img['src'])
        star  = '評分：' + anime.find('div', 'ACG-mainbox4').find('p', 'ACG-mainboxpoint').span.text
        hot = '人氣：' + anime.find('div', 'ACG-mainbox4').find('p', 'ACG-mainplay').span.text

        animates_movie_list.append(Movie(animates_title, img_link, link, "", type, "", date, animates_text, star, hot))

    return animates_movie_list
    
