import urllib2 as urllib
import uuid
import os
import PyPDF2
import nltk
import string
from urlparse import urlparse
from nltk.corpus import stopwords
from os.path import splitext, basename
import numpy as np
from pymongo import MongoClient
import datetime
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import *
#from nltk.stem.snowball import SnowballStemmer

from collections import Counter

client = MongoClient()
db = client['documents']

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

def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = stem_tokens(tokens, stemmer)
    return stems

def read_pdf(source):
    pdfFileObj = open(source, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    numPages = pdfReader.numPages
    text = ''
    for i in range(0, numPages):
    	pageObj = pdfReader.getPage(i)
    	text += pageObj.extractText()
    return numPages, text

def upload_save_new(url):
	uniqID = uuid.uuid4() # generate random uuid 
	response = urllib.urlopen(url)
	addrData = "./Data/"
	fileName = addrData + str(uniqID) + ".pdf"
	file = open(fileName, 'wb')
	file.write(response.read())
	file.close()
	return fileName

def insert_document(uuid, title, path, link, numPages, word_vector, top_words, categories):
	item = {
		'uuid': uuid,
		'path': path,
		'title': title,
		'link': link,
		'numPages': numPages,
		'word_vector': word_vector,
		'top_words': top_words,
		'categories': categories,
		'created_date': datetime.datetime.utcnow()
	}
	db.documents.insert_one(item)


#docLink = "https://www.esma.europa.eu/sites/default/files/library/2015/11/2015-esma-1464_annex_i_-_draft_rts_and_its_on_mifid_ii_and_mifir.pdf"
#fileName = upload_save_new(docLink)
#disassembled = urlparse(docLink)
#lengthDoc, text = read_pdf(fileName)
#name, file_ext = splitext(basename(disassembled.path))
#tokens = get_tokens(text)
#filtered = [w for w in tokens if not w in stopwords.words('english')]
#count = Counter(filtered)
#mostCommon100 = count.most_common(100)
#print mostCommon100

stemmer = PorterStemmer()

#token_dict = {}
path = './Data3'
#for subdir, dirs, files in os.walk(path):
#	for file in files:
#		file_path = subdir + os.path.sep + file
#		lengthDoc, text = read_pdf(file_path)
#		lowers = text.lower().encode('ascii','replace')
#		no_punctuation = lowers.translate(None, string.punctuation)
#		token_dict[file] = no_punctuation

tfidf = pickle.load(open('./tfidf'))
tfs = pickle.load(open('./tfs'))
#tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words='english')
#tfs = tfidf.fit_transform(token_dict.values())

#pickle.dump(tfidf, open('./tfidf', 'w+'))
#pickle.dump(tfs, open('./tfs', 'w+'))

#lengthDoc, str = read_pdf("596-2014 MAR_Regulations.pdf")
#tfidf_a = tfidf.transform([str])

lengthDoc, str2 = read_pdf("2015-1787_-_guidelines_on_complex_debt_instruments_and_structured_deposits.pdf")
tfidf_a = tfidf.transform([str2])
from sklearn.metrics.pairwise import cosine_similarity
list_similarity = []
file_names = []

for subdir, dirs, files in os.walk(path):
#	print files
	for file in files:
		file_path = subdir + os.path.sep + file
		#lengthDoc, text = read_pdf(file_path)
		uniqID = uuid.uuid4() # generate random uuid 
		try:
#			tfidf_b = tfidf.transform([text])
#			pickle.dump(tfidf_b, open('./Data4/' + file, 'w+'))
			tfidf_b = pickle.load(open('./Data4/' + file))
			word_vector = tfidf_b
			CS = cosine_similarity(tfidf_a, tfidf_b)
			list_similarity.append(CS)
			file_names.append(file)
		except:
			print "Could not compute distances."
			list_similarity.append(0)
			file_names.append(file)
			word_vector = 0
			pass
		#finally:
			#insert_document(uniqID, file, file_path, '', lengthDoc, str(word_vector.toarray), [], [])
print file_names[np.argmax(list_similarity)]
