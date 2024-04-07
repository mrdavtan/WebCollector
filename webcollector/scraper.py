# scraper.py
import time
import json
import os
import json
import feedparser
import uuid
import requests
from datetime import datetime
import dateutil.parser
from article import Article
import re
from urllib.robotparser import RobotFileParser


class Scraper:
    def __init__(self, sources, specific_date):
        self.sources = sources
        self.specific_date = specific_date
        self.load_config()
        self.url_to_uuid = {}
        self.articles_dir = self.load_config()

    def load_config(self):
        config_file = 'config.json'
        with open(config_file, 'r') as file:
            config = json.load(file)
        return config['articles_dir']


    def scrape(self):
        os.makedirs(self.articles_dir, exist_ok=True)
        articles_list = []

        try:
            for source, content in self.sources.items():
                print(f"Processing source: {source}")
                for url in content['rss']:
                    feed = feedparser.parse(url)
                    for entry in feed.entries:
                        if hasattr(entry, 'published'):
                            article_date = dateutil.parser.parse(entry.published)
                            if article_date.strftime('%Y%m%d') == str(self.specific_date):
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
                                    headers = {'User-Agent': 'Mozilla/5.0'}
                                    response = requests.get(entry.link, headers=headers)
                                    if response.status_code == 200:
                                        # Corrected instantiation of the custom Article class
                                        article = Article(entry=entry, source=source)  # Corrected line
                                        article.scrape()  # Assuming your custom Article class has a method .scrape() for processing

                                        article_details.update({
                                            'body': article.article.text if article.article else '',
                                            'summary': article.article.summary if article.article else '',
                                            'keywords': article.article.keywords if article.article else '',
                                            'image_url': article.article.top_image if article.article else ''
                                        })
                                    else:
                                        print(f"Request failed with status code: {response.status_code}")
                                except Exception as e:
                                    print(e)
                                    print('continuing...')


                                articles_list.append(article_details)
                                self.save_article_as_json(article_details, self.articles_dir)
                                print(f"Saved article: {article_details['title']}")
                                time.sleep(1)

            return articles_list
        except Exception as e:
            raise Exception(f'Error in "Scraper.scrape()": {e}')

    def check_robots_permission(self, url):
        try:
            rp = robotparser.RobotFileParser()
            rp.set_url(f"{urlparse(url).scheme}://{urlparse(url).netloc}/robots.txt")
            rp.read()
            return rp.can_fetch("*", url)
        except:
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
