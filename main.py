"""The main module that runs the user interface alongside scheduling updates"""
import sched
import time
import requests
import json
import os
from flask import render_template
from flask import Flask
from flask import request
import covid_news_handling as news_module
import covid_data_handler as data_module
from functionallity import time_convert
from functionallity import get_config_data


data_module.covid_API_request()
news_module.news_API_request()

app = Flask(__name__)
config = get_config_data()
covid_data = json.load(open('covid_data.json', 'r'))
news = json.load(open('news_articles.json', 'r'))
sched_updates = [{'title':'repeat','content':'dd'},
                 {'title':'covid','content':'dd'},
                 {'title':'news','content':'dd'}]


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
    data_module.s.run(blocking=False)
    
    
    
    if request.method == "GET":
        update_name = request.args.get("two")
        update_time = request.args.get("update")
        if request.args.get("notif"):
            rm_title = request.args.get("notif")
            remove_article(rm_title)
        if request.args.get("repeat"):
            sched_updates[0]['content'] = 'true'
        if request.args.get("covid-data"):
            sched_updates[1]['content'] = update_time
            data_module.schedule_covid_updates(update_time,update_name)
        if request.args.get("news"):
            sched_updates[2]['content'] = update_time
            news_module.update_news(update_time,update_name)

        
        

    return render_template('index.html',
                           title='covid dashboard',
                           image=config['image'],
                           updates=sched_updates,
                           news_articles=news,
                           location=covid_data['location'],
                           local_7day_infections=covid_data['local_infection_sum'],
                           nation_location=covid_data['nation'],
                           national_7day_infections=covid_data['national_infection_sum'],
                           hospital_cases='Hospital cases in '+covid_data['nation']+':'+str(covid_data['national_hosptital_cases']),
                           deaths_total='Deaths in '+covid_data['nation']+':'+str(covid_data['national_cumumlative_deaths']),
                           )


if __name__ == '__main__':
    app.run()



