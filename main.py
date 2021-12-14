"""The main module that runs the user interface alongside scheduling updates"""
import sched
import time
import requests
import json
import os
from flask import render_template
from flask import Flask
from flask import request
from covid_news_handling import news_API_request
from covid_data_handler import covid_API_request
from covid_data_handler import schedule_covid_updates
from functionallity import time_convert
from functionallity import get_config_data


app = Flask(__name__)

config = get_config_data()

scheduler = sched.scheduler(time.time,time.sleep)

covid_data = covid_API_request()

new_news = []


def prepare_news_articles():
    full_news = news_API_request()
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
    return(full_news)
        


def remove_article(title):
    for index in range(len(prepped_news)-1):
        if prepped_news[index]['title'] == title:
            removed_article = prepped_news.pop(index)
            file = open("removed_news.json", "r+")
            
            if os.path.getsize('removed_news.json')>6:
                data = json.load(file)
                for index in range(len(data)):
                    if data[index]['title']== removed_article['title']:
                        return
                data.append(removed_article)
                file.seek(0)
                json.dump(data,file)
            else:
                list = []
                list.append(removed_article)
                json.dump(list,file)
            file.close()
        

@app.route('/index', methods=['GET', 'POST'])
def index():
    scheduler.run(blocking=False)
    
    if request.method == "GET":
        update_name = request.args.get("two")
        update_time = request.args.get("update")
        if request.args.get("notif"):
            rm_title = request.args.get("notif")
            remove_article(rm_title)
        if request.args.get("repeat"):
            repeat_update=True
        if request.args.get("covid-data"):
            update_covid=True
        if request.args.get("news"):
            update_news=True

        
        

    return render_template('index.html',
                           title='covid dashboard',
                           image=config['image'],
                           news_articles=prepped_news,#
                           location=covid_data['location'],
                           local_7day_infections=covid_data['local_infection_sum'],
                           nation_location=covid_data['nation'],
                           national_7day_infections=covid_data['national_infection_sum'],
                           hospital_cases='Hospital cases in '+covid_data['nation']+':'+str(covid_data['national_hosptital_cases']),
                           deaths_total='Deaths in '+covid_data['nation']+':'+str(covid_data['national_cumumlative_deaths']),
                           )

prepped_news = prepare_news_articles()

if __name__ == '__main__':
    app.run()



