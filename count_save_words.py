import nltk
#from models import Result
import requests
from bs4 import BeautifulSoup
import operator
import re
from collections import Counter
from stop_words import stops
from models import *
def count_and_save_words(url):
    #nltk.download('punkt')
    errors = []
    try:
        r = requests.get(url)
    except:
        errors.append("Unable to get URL. Please make sure its valid")
        return {'errors': errors}
    # test processing
    raw = BeautifulSoup(r.text, "html.parser").get_text()
    nltk.data.path.append('./nltk_data/')
    tokens = nltk.word_tokenize(raw)
    text = nltk.Text(tokens)

    nonPunct = re.compile('.*[A-Za-z].*')
    raw_words = [w for w in text if nonPunct.match(w)]
    raw_word_count = Counter(raw_words)

    no_stop_words = [w for w in raw_words if w.lower() not in stops]
    no_stop_words_count = Counter(no_stop_words)
    try:
        result = Result(url=url, result_all=raw_word_count, result_no_stop_words=no_stop_words_count)
        db.session.add(result)
        db.session.commit()
        return result.id
    except:
        errors.append("Unable to add item to databse")
        return {"errors":errors}
