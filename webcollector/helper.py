# helper.py

import os
import json
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
import string
from unidecode import unidecode

def load_sources(folder):
    sources = {}
    try:
        for filename in os.listdir(folder):
            if filename.endswith('.json'):
                file_path = os.path.join(folder, filename)
                with open(file_path) as data:
                    file_sources = json.load(data)
                    sources.update(file_sources)
        print(f'INFO: Loaded sources from "{folder}".')
        return sources
    except:
        raise Exception(f'Error in "Helper.load_sources()"')

def write_dataframe(sources):
    try:
        df = pd.json_normalize(sources)
        return df
    except:
        raise Exception(f'Error in "Helper.write_dataframe()"')

def clean_dataframe(df):
    try:
        if 'title' in df.columns:
            df = df[df.title != '']
        if 'body' in df.columns:
            df = df[df.body != '']
        if 'image_url' in df.columns:
            df = df[df.image_url != '']
        if 'title' in df.columns:
            df = df[df.title.str.count('\s+').ge(3)]
        if 'body' in df.columns:
            df = df[df.body.str.count('\s+').ge(20)]
        return df
    except:
        raise Exception(f'Error in "Helper.clean_dataframe()"')

def remove_stopwords(text):
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(text)
    filtered_sentence = [w for w in word_tokens if not w.lower() in stop_words]
    return ' '.join(filtered_sentence)

def clean_articles(df):
    try:
        df = (df.drop_duplicates(subset=["title", "source"])).sort_index()
        df = (df.drop_duplicates(subset=["body"])).sort_index()
        df = (df.drop_duplicates(subset=["url"])).sort_index()
        df = df.reset_index(drop=True)

        df['clean_body'] = df['body'].str.lower()

        df['clean_body'] = [remove_stopwords(x).translate(str.maketrans('', '', string.punctuation)).translate(str.maketrans('', '', string.digits)) for x in df['clean_body']]

        sources_set = [x.lower() for x in set(df['source'])]
        sources_to_replace = dict.fromkeys(sources_set, "")
        df['clean_body'] = (df['clean_body'].replace(sources_to_replace, regex=True))

        df['clean_body'] = df['clean_body'].apply(unidecode)

        df['clean_body'] = df['clean_body'].apply(word_tokenize)

        stemmer = SnowballStemmer(language='english')
        df['clean_body'] = df["clean_body"].apply(lambda x: [stemmer.stem(y) for y in x])
        df['clean_body'] = df["clean_body"].apply(lambda x: ' '.join([word for word in x]))

        return df
    except:
        raise Exception(f'Error in "Helper.clean_articles()"')
