"""module uses newsAPI to obtain recent articles related to covid by defualt"""
import os
import json
import requests
from functionallity import get_config_data
import covid_data_handler as data
titles = []
contents = []
urls = []

def news_API_request(covid_terms='Covid COVID-19 coronavirus'):
    """collects news articles using an API for it to go to prepare_news_articles"""
    api_key = get_config_data()['api_key']
    url = ('https://newsapi.org/v2/everything?'
           'q='
           +covid_terms+
           '&apiKey='+api_key)
    api_response = requests.get(url)
    news_articles = api_response.json()['articles']
    prepare_news_articles(news_articles)


def prepare_news_articles(full_news):
    """takes news articles and compares them against a list of already seen articles
to either keep or remove them"""
    if os.path.getsize('removed_news.json')>6:
        file = open('removed_news.json', 'r')
        removed_news = json.load(file)
        new_index = 0
        rm_index = 0
        while new_index != len(full_news):
            while rm_index != len(removed_news):
                if full_news[new_index]['title'] == removed_news[rm_index]['title']:
                    full_news.pop(new_index)
                rm_index = rm_index + 1
            rm_index = 0
            new_index = new_index + 1
        file.close()
    news_file = open('news_articles.json', 'w')
    json.dump(full_news,news_file)
    news_file.close()

def update_news(update_interval,update_name):
    """schedules updates to the news articles using the sched module"""
    sched_name = data.s.enterabs(update_interval,1, news_API_request,())
    return sched_name
