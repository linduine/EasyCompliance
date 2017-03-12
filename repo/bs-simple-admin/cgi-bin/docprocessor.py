#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
import os
import PyPDF2
import nltk
import string
import cgi		# for invoking from web page
from nltk.corpus import stopwords

from nltk.stem.porter import *

from collections import Counter

from PyPDF2 import PdfFileWriter, PdfFileReader
from StringIO import StringIO

import urllib2 as urllib
from urllib2 import Request, urlopen
from urlparse import urlparse
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
stemmer = PorterStemmer()

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


print("Content-type: text/html\n")
print("""﻿<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
      <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Simple Responsive Admin</title>
	<!-- BOOTSTRAP STYLES-->
    <link href="../assets/css/bootstrap.css" rel="stylesheet" />
     <!-- FONTAWESOME STYLES-->
    <link href="../assets/css/font-awesome.css" rel="stylesheet" />
        <!-- CUSTOM STYLES-->
    <link href="../assets/css/custom.css" rel="stylesheet" />
     <!-- GOOGLE FONTS-->
   <link href='http://fonts.googleapis.com/css?family=Open+Sans' rel='stylesheet' type='text/css' />
</head>
<body>
     
           
          
    <div id="wrapper">
         <div class="navbar navbar-inverse navbar-fixed-top">
            <div class="adjust-nav">
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".sidebar-collapse">
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>
                    <a class="navbar-brand" href="#">
                        <img src="assets/img/logo.png" />
                    </a>
                </div>
              
                 <span class="logout-spn" >
                  <a href="#" style="color:#fff;">LOGOUT</a>  

                </span>
            </div>
        </div>
        <!-- /. NAV TOP  -->
        <nav class="navbar-default navbar-side" role="navigation">
            <div class="sidebar-collapse">
                <ul class="nav" id="main-menu">
                 

 <li >
                        <a href="index.html" ><i class="fa fa-desktop "></i>Dashboard <span class="badge"></span></a>
                    </li>
                    <li class="active-link">
                        <a href="blank.html"><i class="fa fa-edit "></i> Add Note  <span class="badge"></span></a>
                    </li>
                </ul>
                            </div>

        </nav>
        <!-- /. NAV SIDE  -->
        <div id="page-wrapper" >
            <div id="page-inner">
                <div class="row">
                    <div class="col-md-12">
                     <h2>DOCUMENTS </h2>   
                    </div>
                </div>              
                 <!-- /. ROW  -->
                  <hr />
                  <ul class="nav top-menu">                    
                        <li>
                            <form class="navbar-form">
                                <h3 style="display: inline;">Search documents</h3>
								<div class="input-group input-group">
								  <input type="text" class="form-control" placeholder="Titles, topics, key words...">
								  <div class="input-group-btn">
									<button class="btn btn-default" type="submit"><i class="glyphicon glyphicon-search"></i></button>
								  </div>
								</div>
                            </form>
                        </li>                 
                    </ul>
					<ul class="nav top-menu">                    
                        <li>
                            <form class="navbar-form">
                                <h3>Categories</h3>
								<div class="dropdown">
								  <button class="btn btn-primary dropdown-toggle" type="button" data-toggle="dropdown">Choose
								  <span class="caret"></span></button>
								  <ul class="dropdown-menu">
									<li><a href="#">Technical Regulations</a></li>
									<li><a href="#">Data Obligations</a></li>
									<li><a href="#">Impact Analysis</a></li>
								  </ul>
								</div>
                            </form>
                        </li>                 
                    </ul>             
                 <!-- /. ROW  -->
                  <ul class="nav top-menu">                    
                        <li>
							<form class="navbar-form-lg">
                                <h3>Add new document</h3>
								<div class="input-group input-group">
								  <input type="text" class="form-control" placeholder="URL...">
								  <div class="input-group-btn">
									<button class="btn btn-default" type="submit"><i class="glyphicon glyphicon-search"></i></button>
								  </div>
								</div>
                            </form>
                        </li>                    
                    </ul>
                  <hr />""")

form = cgi.FieldStorage()

url = form.getfirst("docURL") # first double slash becomes single
docLink = url #"https://www.esma.europa.eu/sites/default/files/library/2015/11/2015-esma-1464_annex_i_-_draft_rts_and_its_on_mifid_ii_and_mifir.pdf"
fileName = upload_save_new(docLink)
disassembled = urlparse(docLink)
lengthDoc, text = read_pdf(fileName)
name, file_ext = splitext(basename(disassembled.path))
print("<h3>Document saved! </h3>")
address = "Address of the file: " + str(fileName)
print("<p>{0}</p>".format(address))
nameF = "Name of the file: " + str(name)
print("<p>{0}</p>".format(nameF))
numPag = "Length of the file (pages): " + str(lengthDoc)
print("<p>{0}</p>".format(numPag))
tokens = get_tokens(text)
filtered = [w for w in tokens if not w in stopwords.words('english')]
count = Counter(filtered)
mostCommonFiltered = count.most_common(10)
print("<h3>Top 10 used words </h3>")
print("<p>{0}</p>".format(mostCommonFiltered))
#print mostCommon100

#url = url.replace(":/", "://") # double the slash again

#print("<h3>URL</h3>")
#print("<p>{0}</p>".format(url))

# start saving file on disk
tfidf_a = tfidf.transform([text])
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
mostSimilar = file_names[np.argmax(list_similarity)]

print("<h3>Most similar document</h3>")
print("<p>{0}</p>".format(mostSimilar))


#print("<h3>Top 10 word stems</h3>")
#print("<p>{0}</p>".format(mostCommonStemmed))

print("""<!-- /. ROW  -->           
    </div>
             <!-- /. PAGE INNER  -->
            </div>
         <!-- /. PAGE WRAPPER  -->
        </div>
    <div class="footer">
      
    
             <div class="row">
                <div class="col-lg-12" >
                    2017 EasyCompliance | Drafted at: SIXHackathon 2017
                </div>
        </div>
        </div>
          

     <!-- /. WRAPPER  -->
    <!-- SCRIPTS -AT THE BOTOM TO REDUCE THE LOAD TIME-->
    <!-- JQUERY SCRIPTS -->
    <script src="assets/js/jquery-1.10.2.js"></script>
      <!-- BOOTSTRAP SCRIPTS -->
    <script src="assets/js/bootstrap.min.js"></script>
      <!-- CUSTOM SCRIPTS -->
    <script src="assets/js/custom.js"></script>
    
   
</body>
</html>""")
