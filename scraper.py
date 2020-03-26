import urllib3
import re
import string
import json
import html
import config
from bs4 import BeautifulSoup
from bs4.element import Comment
from urllib3.exceptions import HTTPError
from io import StringIO
from nltk.stem import PorterStemmer
import os.path as path


class SoupStrainer():
    englishDictionary = {}
    haveHeadline = False
    recHeadline = ''
    locToGet = ''
    pageData = None
    errMsg = None
    soup = None
    msgOutput = True

    def init(self):
        with open(path.join(config.base_dir, 'words.json')) as reader:
            self.englishDictionary = json.load(reader)


    def tag_visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

    def loadAddress(self, address):
        self.locToGet = address
        self.haveHeadline = False
        htmatch = re.compile('.*http.*')
        user_agent = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.3;rv:36.0) Gecko/20100101 Firefox/36.0'}
        ps = PorterStemmer()
        if(htmatch.match(self.locToGet) is None):
            self.locToGet = 'http://' + self.locToGet

        if len(self.locToGet) > 5:
            try:
                urllib3.disable_warnings(
                    urllib3.exceptions.InsecureRequestWarning)
                http = urllib3.PoolManager(2, headers=user_agent)
                r = http.request('GET', self.locToGet)
                self.pageData = r.data
            except:
                self.errMsg = 'Error on HTTP request'
                return False

        self.extractText = ''
        self.recHeadline = self.locToGet
        self.soup = BeautifulSoup(self.pageData, 'html.parser')
        ttexts = self.soup.findAll(text=True)
        viz_text = filter(self.tag_visible, ttexts)
        allVisText = u"".join(t.strip() for t in viz_text)
        for word in allVisText.split():
            canonWord = word.lower()
            canonWord = canonWord.translate(
                str.maketrans('', '', string.punctuation))
            canonWord = canonWord.strip(string.punctuation)
            if(canonWord in self.englishDictionary):
                canonWord = ps.stem(canonWord)
                self.extractText = self.extractText + canonWord + " "

        return True
