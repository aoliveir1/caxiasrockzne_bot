# -*- coding: utf-8 -*-

import sys
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent
from telepot.exception import TelegramError
from urllib.request import urlopen
from bs4 import BeautifulSoup

# Scrapping the main page
#import urllib2
#page = urllib2.urlopen('http://www.caxiasrockzne.com.br')
page = urlopen('http://www.caxiasrockzne.com.br')
soup = BeautifulSoup(page, 'html.parser')
posts = soup.find_all('h3', attrs={'class': 'post-title entry-title'})

def get_links():
    # Crawling for the posts links
    links = []
    for link in posts:
        link = str(link)
        l0 = link.find('www')
        l1 = link.find('l\">')
        link = link[l0 : l1 + 1]
        links.append(link)
    return links

def get_soup(i):
    # Prepare page to scrap
    page = urlopen('http://' + get_links()[i])
    return BeautifulSoup(page, 'html.parser')

def get_title(i):
    # Get the post title
    title = get_soup(i).find('h3', attrs={'class': 'post-title entry-title'})
    return title.text.strip()

def get_date(i):
    # Get the post date
    date = get_soup(i).find('span', attrs={'class': 'byline post-timestamp'})
    return date.text.strip().replace('\n', ' ').replace('  ', '')[2:]

def get_text(i):
    # Get the post text
    text = get_soup(i).find('div', attrs={'class':'post-body entry-content float-container'})
    text = text.text.strip()
    text = str(text[0:500]).replace('\n\n', ' ').replace('\r', '')
    text += '...\nPostado em: ' + get_date(i) + '\nContinue lendo: ' + get_links()[i]
    return text

def on_chat_message(msg):
    pass

def on_inline_query(msg):
    def compute():
        query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')
        print ('Inline Query:', query_id, from_id, query_string)
        articles = []
        for i in range(3):
            articles.append(InlineQueryResultArticle(
                id=i,
                title=get_title(i),
                input_message_content=InputTextMessageContent(
                    message_text=get_text(i))
                             ))
        return articles
    try:
        answerer.answer(msg, compute)
    except TelegramError as e:
        print(e.description)
        print(e.error_code)

def on_chosen_inline_result(msg):
    result_id, from_id, query_string = telepot.glance(msg, flavor='chosen_inline_result')
    print ('Chosen Inline Result:', result_id, from_id, query_string)


TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot(TOKEN)
answerer = telepot.helper.Answerer(bot)

try:
    MessageLoop(bot, {'chat': on_chat_message,
                      'inline_query': on_inline_query,
                      'chosen_inline_result': on_chosen_inline_result}).run_as_thread()
except TelegramError as e:
    print(e.description)
    print(e.error_code)

while 1:
    time.sleep(10)
