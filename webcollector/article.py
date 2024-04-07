# article.py
import dateutil.parser
import requests
from newspaper import Article as NewsArticle

class Article:
    def __init__(self, entry, source):
        self.entry = entry
        self.source = source
        self.article = None

    def scrape(self):
        try:
            response = requests.get(self.entry.link)
            if response.status_code == 200:
                self.article = NewsArticle(self.entry.link)
                self.article.set_html(response.text)
                self.article.parse()
                self.article.nlp()
            else:
                print(f"Request failed with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Request exception for URL {self.entry.link}: {e}")

    def get_details(self):
        if self.article:
            return {
                'source': self.source,
                'url': self.entry.link,
                'date': dateutil.parser.parse(self.entry.published).strftime('%Y-%m-%d'),
                'time': dateutil.parser.parse(self.entry.published).strftime('%H:%M:%S'),
                'title': self.article.title,
                'body': self.article.text,
                'summary': self.article.summary,
                'keywords': self.article.keywords,
                'image_url': self.article.top_image
            }
        else:
            return None
