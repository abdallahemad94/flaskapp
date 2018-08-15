import feedparser
import json
import urllib
import urllib2
from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)

rss_feeds = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640'}

defults = {'publication': 'bbc',
           'city': 'London,UK',
           'currency_from': 'GBP',
           'currency_to': 'USD'}

weather_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric\
&appid=fd7c5a65c0f0108722f0f8695283cb79"

currency_url = "https://openexchangerates.org/api/latest.json?app_id=ddda11bbb3fe467e86d17096aa03d4fd"


@app.route('/')
def home():
    """get customized headlines and weather and currency
    based on user input or defults"""
    # get headlines
    publication = request.args.get('publication')
    if not publication:
        publication = defults['publication']
    articles = get_news(publication)
    # get weather
    city = request.args.get('city')
    if not city:
        city = defults['city']  
    weather = get_weather(city)
    # get currency
    currency_from = request.args.get('currency_from')
    if not currency_from:
        currency_from = defults['currency_from']
    currency_to = request.args.get('currency_to')
    if not currency_to:
        currency_to = defults['currency_to']
    rate, currencies = get_rates(currency_from, currency_to)
    return render_template('home.html', articles=articles,
                           weather=weather, currency_from=currency_from,
                           currency_to=currency_to, rate=rate,
                           currencies=sorted(currencies))


def get_news(query):
    """parse and display news feed from the publication"""
    if not query or query.lower() not in rss_feeds:
        publication = defults['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(rss_feeds[publication])
    return feed['entries']


def get_weather(query):
    """Get the weather data from openweathermap.org"""
    query = urllib.quote(query)
    url = weather_url.format(query)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {
            'description': parsed['weather'][0]['description'],
            'temperature': parsed['main']['temp'],
            'city': parsed['name'],
            'country': parsed['sys']['country']
        }
    return weather


def get_rates(frm, to):
    #import os, ssl
    #if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
    #   getattr(ssl, '_create_unverified_context', None)): 
    #       ssl._create_default_https_context = ssl._create_unverified_context
    all_currency = urllib2.urlopen(currency_url).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate / frm_rate, parsed.keys())


if __name__ == '__main__':
    app.run(port=5000, debug=True)
