# scraper.py
import signal
import time
import json
import os
import random
import feedparser
import uuid
import requests
from datetime import datetime
import dateutil.parser
from article import Article
import re
from urllib.robotparser import RobotFileParser

MIN_SCRAPE_DELAY_SECONDS = float(os.getenv("WEBCOLLECTOR_MIN_DELAY_SECONDS", "0.05"))
MAX_SCRAPE_DELAY_SECONDS = float(os.getenv("WEBCOLLECTOR_MAX_DELAY_SECONDS", "0.25"))


class Scraper:
    def __init__(self, sources, specific_date):
        self.sources = sources
        self.specific_date = specific_date
        self.load_config()
        self.url_to_uuid = {}
        self.articles_dir = self.load_config()

    def load_config(self):
        config_file = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_file, 'r') as file:
            config = json.load(file)
        return config['articles_dir']


#    def load_config(self):
#        config_file = 'config.json'
#        with open(config_file, 'r') as file:
#            config = json.load(file)
#        return config['articles_dir']

    def scrape(self):
        os.makedirs(self.articles_dir, exist_ok=True)
        articles_list = []

        try:
            for source, content in self.sources.items():
                print(f"Processing source: {source}")
                for url in content['rss']:
                    try:
                        feed = feedparser.parse(url, request_headers={'User-Agent': 'Mozilla/5.0'})
                    except Exception as e:
                        print(f"Failed to parse feed {url}: {e}")
                        continue
                    for entry in feed.entries:
                        if hasattr(entry, 'published'):
                            article_date = dateutil.parser.parse(entry.published)
                            if article_date.strftime('%Y%m%d') == str(self.specific_date):
                                self.sleep_with_jitter()
                                article_details = {
                                    'source': source,
                                    'url': getattr(entry, 'link', 'No URL Available'),
                                    'title': getattr(entry, 'title', 'No Title Available'),
                                    'date': article_date.strftime('%Y-%m-%d'),
                                    'time': article_date.strftime('%H:%M:%S %Z'),
                                    'description': getattr(entry, 'description', 'No Description Available'),
                                    'body': '',
                                    'summary': '',
                                    'keywords': [],
                                    'image_url': '',
                                    'robots_permission': self.check_robots_permission(entry.link)
                                }

                                try:
                                    headers = {
                                        'User-Agent': random.choice([
                                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
                                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0',
                                            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
                                            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36'
                                        ])
                                    }
                                    response = requests.get(entry.link, headers=headers, timeout=10)  # 10 seconds timeout
                                    if response.status_code == 200:
                                        article = Article(entry=entry, source=source)  # Correct instantiation
                                        article.scrape()  # Processing the article

                                        article_details.update({
                                            'body': article.article.text if hasattr(article, 'article') else '',
                                            'summary': article.article.summary if hasattr(article, 'article') else '',
                                            'keywords': article.article.keywords if hasattr(article, 'article') else '',
                                            'image_url': article.article.top_image if hasattr(article, 'article') else ''
                                        })
                                    else:
                                        print(f"Request failed with status code: {response.status_code}")
                                except requests.Timeout:
                                    print(f"Request for {entry.link} timed out.")
                                except Exception as e:
                                    print(e)
                                    print('continuing...')

                                articles_list.append(article_details)
                                self.save_article_as_json(article_details, self.articles_dir)  # Assuming implementation exists
                                print(f"Saved article: {article_details['title']}")
                                self.sleep_with_jitter()

            return articles_list
        except Exception as e:
            raise Exception(f'Error in "Scraper.scrape()": {e}')


    def check_robots_permission(self, url):
        try:
            rp = RobotFileParser()
            parsed = re.match(r'(https?://[^/]+)', url)
            if not parsed:
                return True
            rp.set_url(f"{parsed.group(1)}/robots.txt")
            rp.read()
            return rp.can_fetch("*", url)
        except Exception:
            return True

    def save_article_as_json(self, article, directory):
        article_id = self.generate_uuid_for_article(article['url'])
        article_with_id = {'id': article_id}
        article_with_id.update(article)

        source_name_abbreviation = self.abbreviate_source_name(article['source'])
        sanitized_title = self.sanitize_title(article['title'])
        filename = f"{source_name_abbreviation}_{sanitized_title}_{article['date'].replace('-', '')}.json"
        filepath = os.path.join(directory, filename)

        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(article_with_id, file, ensure_ascii=False, indent=4)

        print(f"Article saved: {filepath}")

    def generate_uuid_for_article(self, article_url):
        if article_url not in self.url_to_uuid:
            self.url_to_uuid[article_url] = uuid.uuid4().hex
        return self.url_to_uuid[article_url]

    def abbreviate_source_name(self, source_name):
        words = source_name.split()
        if len(words) >= 2:
            source_name_abbreviation = words[0][:3] + "_" + words[1][:2]
        else:
            source_name_abbreviation = words[0][:5]
        return source_name_abbreviation

    def sanitize_title(self, title):
        sanitized_title = re.sub(r'[\\/*?:"<>|]', '_', title)
        sanitized_title = re.sub(r'\s+', '_', sanitized_title)[:50]
        return sanitized_title

    def sleep_with_jitter(self):
        low = min(MIN_SCRAPE_DELAY_SECONDS, MAX_SCRAPE_DELAY_SECONDS)
        high = max(MIN_SCRAPE_DELAY_SECONDS, MAX_SCRAPE_DELAY_SECONDS)
        if high <= 0:
            return
        time.sleep(random.uniform(low, high))
