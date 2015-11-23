from flask import Flask, render_template, request
from flask.ext.sqlalchemy import SQLAlchemy
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup
import operator
import os
import requests
import re
import nltk

#%% configuration
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

from models import *

#%% routes
@app.route('/', methods=['GET', 'POST'])
def index():
    nltk.download('punkt')
    errors = []
    results = {}
    if request.method == "POST":
        # get url that the user has entered
        try:
            url = request.form['url']
            r = requests.get(url)
            print(r.text)
        except:
            errors.append(
                "Unable to get URL. Please make sure it's valid and try again."
            )
            return render_template('index.html', errors=errors, results=results)
        if r:
            # test processing
            raw = BeautifulSoup(r.text).get_text()
            nltk.data.path.append('./nltk_data/')
            tokens = nltk.word_tokenize(raw)
            text = nltk.Text(tokens)

            nonPunct = re.compile('.*[A-Za-z].*')
            raw_words = [w for w in text if nonPunct.match(w)]
            raw_word_count = Counter(raw_words)

            no_stop_words = [w for w in raw_words if w.lower() not in stops]
            no_stop_words_count = Counter(no_stop_words)

            results = sorted(
                no_stop_words_count.items(),
                key=operator.itemgetter(1),
                reverse=True
            )[:10]
            try:
                result = Result(url=url, result_all=raw_word_count, result_no_stop_words=no_stop_words_count)
                db.session.add(result)
                db.session.commit()
            except:
                errors.append("Unable to add item to databse")
    return render_template('index.html', errors=errors, results=results)
    
if __name__ == '__main__':
    app.run('0.0.0.0', 5000)

