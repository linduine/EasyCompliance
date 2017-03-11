import uuid
import os
import PyPDF2
import nltk
import string
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import *

from collections import Counter

def get_tokens(text):
    #with open('/opt/datacourse/data/parts/shakes-1.txt', 'r') as shakes:
    #text = data.read()
    lowers = text.lower().encode('ascii','replace')
     #remove the punctuation using the character deletion step of translate
    no_punctuation = lowers.translate(None, string.punctuation)
    tokens = nltk.word_tokenize(no_punctuation)
    return tokens

def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def read_pdf(source):
    pdfFileObj = open(source, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    numPages = pdfReader.numPages
    pageObj = pdfReader.getPage(0)
    text = pageObj.extractText()
    return numPages, text

print uuid.uuid4() # generate random uuid 
lengthDoc, text = read_pdf('esma_guidelines.pdf')
tokens = get_tokens(text)
filtered = [w for w in tokens if not w in stopwords.words('english')]
count = Counter(filtered)
print count.most_common(100)

stemmer = PorterStemmer()
stemmed = stem_tokens(filtered, stemmer)
count = Counter(stemmed)
print count.most_common(100)