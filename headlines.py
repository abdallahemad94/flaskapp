from flask import Flask
import feedparser

APP = Flask(__name__)

rss_feed = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
            'cnn': 'http://rss.cnn.com/rss/edition.rss',
            'fox': 'http://feeds.foxnews.com/foxnews/latest',
            'iol': 'http://www.iol.co.za/cmlink/1.640'}


@APP.route('/')
@APP.route('/<publication>')
def get_news(publication='bbc'):
    '''"""docstring"""
    feed = feedparser.parse(rss_feed[publication])
    first_article = feed['entries'][0]
    return(
            """<html>
                    <body>
                        <h1>Headlines</h1>
                        <b>{0}</b> <br/>
                        <i>{1}</i> <br/>
                        <p>{2}</p> <br/>
                    </body>
                </html>
            """.format(first_article.get('title'),
                       first_article.get('published'),
                       first_article.get('summary')
                       )
        )'''
    return 'no news'

if __name__ == '__main__':
    APP.run(port=5000, debug=True)
