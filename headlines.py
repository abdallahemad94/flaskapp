import datetime
import feedparser
import json
import urllib
import urllib2
from flask import Flask
from flask import make_response
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

currency_url = "http://openexchangerates.org/api/latest.json?\
app_id=ddda11bbb3fe467e86d17096aa03d4fd"


@app.route('/')
def home():
    """
    get customized headlines and weather and currency
    based on user input or defults
    """
    # get headlines
    publication = get_value_with_fallback('publication')
    articles = get_news(publication)

    # get weather
    city = get_value_with_fallback("city")
    weather = get_weather(city)

    # get currency
    currency_from = get_value_with_fallback('currency_from')
    currency_to = get_value_with_fallback('currency_to')
    rate, currencies = get_rates(currency_from, currency_to)
    # create a response around the Jinja
    response = make_response(render_template('home.html',
                                             articles=articles,
                                             weather=weather,
                                             currency_from=currency_from,
                                             currency_to=currency_to,
                                             rate=rate,
                                             currencies=sorted(currencies),
                                             feeds=sorted(rss_feeds.keys()),
                                             publication=publication))
    # set cookies expire date
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    # set cookies
    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)
    return response


def get_value_with_fallback(key):
    """
    get the user data from cookies if not given an explicit
    input by the user if no input and no cookies revert to the defult value
    """
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return defults[key]


def get_news(query):
    """
    parse and display news feed from a specified publication
    """
    if not query or query.lower() not in rss_feeds:
        publication = defults['publication']
    else:
        publication = query.lower()
    feed = feedparser.parse(rss_feeds[publication])
    return feed['entries']


def get_weather(query):
    """
    Get the weather data from openweathermap.org
    for a specific city or country
    query: the city or country to get the data for
    """
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
    """
    retrieve the latest currency exchange rate json file from
    openexchangerates.org using its API
    frm: the currency to change from eg. 'USD'
    to: the currency to change for eg. 'GBP'
    """
    all_currency = urllib2.urlopen(currency_url).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate / frm_rate, parsed.keys())


if __name__ == '__main__':
    app.run(port=5000, debug=True)
