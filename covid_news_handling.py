"""module uses newsAPI to obtain recent articles related to covid by defualt"""
from functionallity import get_config_data
import requests
titles = []
contents = []
urls = []

def news_API_request(covid_terms='Covid COVID-19 coronavirus'):
    api_key = get_config_data()['api_key']
    url = ('https://newsapi.org/v2/everything?'
           'q='
           +covid_terms+
           '&apiKey='+api_key)
    api_response = requests.get(url)
    news_articles = api_response.json()['articles']
    return news_articles



#def update_news(test):



#update_news('a')


#print(news_API_request())
