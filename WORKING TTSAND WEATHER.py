from time_conversions import hhmm_to_seconds
from time_conversions import current_time_hhmm
from flask import Flask
from flask import request
from flask import render_template
import pyttsx3
import time
import sched
#import logging
import requests
import json
import pprint
#logging.basicConfig(filename='sys.log' , encoding='utf-8' , level=logging.DEBUG)
s = sched.scheduler(time.time, time.sleep)
app = Flask(__name__)
engine = pyttsx3.init()
notifications = []
alarms = []
APIkey_weather = ""
APIkey_news = ""
with open('config.json') as json_file:
    data = json.load(json_file) #putting the dictionary in a file called data
    print('json file is running')
    APIkey_weather = data["APIs"]["weather"]
    APIkey_news = data["APIs"]["news"]

def setalarm(alarm_time):
    print(alarm_time)
    label_input = request.args.get("two")
    alarm = {'content': alarm_time, 'title': label_input}
    alarms.append(alarm)
    print(alarm)

    return alarms

def get_top_headlines(): #api call
    base_url = "https://newsapi.org/v2/top-headlines?"
    api_key = "c72ddfc6018746bb9d5d14ae63a16e5c"
    complete_url = base_url + "country=gb" + "&apiKey=" + api_key
    r = requests.get(complete_url)
    r.json()
    return r.json()["articles"]

@app.route('/')
@app.route('/index')
def controller():

    alarm_item = request.args.get("alarm_item")
    if alarm_item != None:
        for alarm in alarms:
            if alarm['title'] == alarm_item:
                alarms.remove(alarm)
    s.run(blocking=False)
    alarm_time = request.args.get("alarm")
    news = get_top_headlines()
    if alarm_time:
        #convert alarm_time to a delay
        alarm_hhmm = alarm_time[-5:-3] + ':' + alarm_time[-2:]
        delay = hhmm_to_seconds(alarm_hhmm) - hhmm_to_seconds(current_time_hhmm())
        weather_input = ""
        news_input = ""
        if request.args.get("weather") != None and request.args.get("news") != None:
            weather_input = get_weather()
            news_input = get_news_briefing()
            setalarm(alarm_time + " " + weather_input + news_input)
        elif request.args.get("weather") != None:
            weather_input = get_weather()
            setalarm(alarm_time + " " + weather_input + news_input)
        elif request.args.get("news") != None:
            news_input = get_news_briefing()
            setalarm(alarm_time + " " + weather_input + news_input)
        else:
            setalarm(alarm_time)

        print(alarms)
        print(alarms[-1]['title'])
        s.enter(int(delay), 1, announce, (alarms[-1]['title'],))
    #    alarms.remove(alarms[0])

    return render_template('index.html', title='Daily update', notifications=news, image='alarm-meme.jpg', alarms= alarms)

def announce(announcement):
    print("announcement is running")
    print(announcement)
    try:
        engine.endLoop()
    except:
        pass
        #logging.error('pyttsx3 endLoop error. No action taken Program should continue to run.')
    engine.say(announcement)
    engine.runAndWait()


def get_weather():
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city_name = input("Enter city name : ")
    complete_url = base_url + "appid=" + APIkey_weather + "&q=" + city_name
    print("APi key: ")
    print(APIkey_weather)
    response = requests.get(complete_url)
    print(response)
    x = response.json()['weather']
    weather_description = x[0]["description"]
    #print(weather_description)
    return weather_description

def get_news_briefing(): #api call
    base_url = "https://newsapi.org/v2/top-headlines?"
    api_key = "c72ddfc6018746bb9d5d14ae63a16e5c"
    complete_url = base_url + "country=gb" + "&apiKey=" + api_key
    response = requests.get(complete_url)
    x = response.json()['articles'] #x = list of articles
    news_list = []
    for i in x:
        if 'covid' in i['title'].lower():
            news_list.append(i['title'])
        news_string = "" #initialises the empty string
        for ele in news_list:     # traverse in the string
            news_string += ele
    return news_string # return string

if __name__ == '__main__':
    #logging.info('Application starting...')
    app.run()
