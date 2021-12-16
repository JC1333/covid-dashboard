"""The main module that runs the user interface alongside scheduling updates"""
import time
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
sched_updates = []

def remove_schedule_title(title):
    """removes a schedule based on user input"""
    index=0
    while index != len(sched_updates):
        if sched_updates[index]['title'] == title:
            removed_schedule = sched_updates.pop(index)
            try:
                data_module.s.cancel(removed_schedule['event'])
            except ValueError:
                print('this event has already been executed and removed')
            index=index-1
        index=index+1

def remove_schedule_event(time,priority,sequence,action,argument1,argument2):
    """removes a schedule when the event occurs"""
    index=0
    while index != len(sched_updates):
        if sched_updates[index]['event'][0] == time:
            if sched_updates[index]['event'][1] == priority:
                if sched_updates[index]['event'][2] == sequence:
                    if sched_updates[index]['event'][3] == action:
                        if sched_updates[index]['event'][4] == argument1:
                            if sched_updates[index]['event'][5] == argument2:
                                if sched_updates[index]['repeat'] is True:
                                    data_module.s.enterabs(time+86400,priority,action,(argument1,argument2))
                                    return
                                sched_updates.pop(index)
                                index=index-1
        index=index+1


def remove_article(title):
    """removes news articles from the site and stores them
in a file of seen news articles"""
    for index in range(len(news)-1):
        if news[index]['title'] == title:
            removed_article = news.pop(index)
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
    """creates the website and takes user input/calls other functions"""
    data_module.s.run(blocking=False)
    update_time = '00:00'
    repeat=False
    if request.method == "GET":
        update_name = request.args.get("two")
        update_time = request.args.get("update")
        current_day_time = time.time()%(24*60*60)
        current_day_start = (time.time()-current_day_time)
        next_day_start = (86400)+(time.time()-current_day_time)
        update_time_seconds = time_convert(update_time)
        if update_time_seconds < current_day_time:
            update_time_seconds = next_day_start + update_time_seconds
        else:
            update_time_seconds = current_day_start + update_time_seconds
        if request.args.get("notif"):
            rm_title = request.args.get("notif")
            remove_article(rm_title)
        if request.args.get("update_item"):
            rm_sched = request.args.get("update_item")
            remove_schedule_title(rm_sched)
        if request.args.get("repeat"):
            repeat=True
        if request.args.get("covid-data"):
            data_name = data_module.schedule_covid_updates(update_time_seconds,update_name)
            data_module.s.enterabs(update_time_seconds,2, remove_schedule_event,data_name)
            sched_updates.append({'title':'covid update' + update_name,'content':'scheduled at'+update_time,'event':data_name,'repeat':repeat})
        if request.args.get("news"):
            news_name = news_module.update_news(update_time_seconds,update_name)
            data_module.s.enterabs(update_time_seconds,2, remove_schedule_event,news_name)
            sched_updates.append({'title':'news update' + update_name,'content':'scheduled at'+update_time,'event':news_name,'repeat':repeat})

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
