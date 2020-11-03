import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
import pickle
# import string
# from nltk.stem import PorterStemmer
# from xml.sax.handler import ContentHandler

from collections import defaultdict
from random import randint
from unidecode import unidecode
from tqdm import tqdm
import re
import Stemmer
import sys
import heapq
import operator
import timeit
import time
import os
import pdb
import threading
import math
import xml.sax




class helperClass(xml.sax.handler.ContentHandler):
  def __init__(self):
    # print("Inside init")
    self.currentData = ""
    self.title = ""
    self.text = ""
    self.pageCount = 0
    self.id = 0
    self.flag = 0
    pass

  def startElement(self, tag, attributes):
    # print("Inside startElement")
    self.currentData = tag
    if(tag == "page"):
      # print("New Page")
      self.pageCount += 1
      # print(self.pageCount)
      self.flag = 0
      self.title = ""
      self.text = ""

  def characters(self, content):
    # print("Inside characters")
    if self.currentData == "title":
      self.title = content
    elif self.currentData == "id":
      if(self.flag == 0):
        self.id = content
        self.flag = 1
    elif self.currentData == "text":
      self.text += content

  def endElement(self, tag):
    # print("Inside endElement")
    # if self.currentData == "title":
    #   print("Title : ", self.title)
    # elif self.currentData == "id":
    #   print("ID    : ", self.id)
    # elif self.currentData == "text":
    #   print("Text  : ",self.text)

    if (self.currentData == "text"):
      docID[pageCount] = self.title.strip().encode("ascii", errors="ignore").decode()
      title, body, info, categories, links, references = process_text(self.text, self.title)
      create_index( title, body, info, categories, links, references)

    self.currentData = ""


def remove_special(text):
  # print("Inside remove_special")
  text = re.sub(r'[^A-Za-z0-9]+', r' ', text)
  return text


def tokenize(text):
  # print("Inside tokenize")
  global tokensCount
  text = text.encode("ascii", errors="ignore").decode()
  text = re.sub(r'[^A-Za-z0-9]+', r' ', text)
  tokens = text.split()
  tokensCount += len(tokens)
  return tokens


def remove_stopwords(text):
  return [word for word in text if word not in stop_words]


def stemming(text):
  text = stemmer.stemWords(text)
  return text



def processing(data):
  # print("Inside processing")
  data = remove_stopwords(data)
  data = stemming(data)
  return data

def process_text(text, title):
  # print("Inside process_text")
  references = []
  categories = []
  links = []
  text = text.lower() 
  temp = text.split("== references ==")
  # print("len(temp)",len(temp))
  if(len(temp) == 1):
    temp = text.split("==references==")
  if(len(temp) != 1):
    references = process_references(temp[1])
    categories = process_categories(temp[1])
    links = process_links(temp[1]) 
  else: 
    categories = []
    links = []
  temp0 = temp[0]
  body = process_body(temp0)
  title= title.lower()
  title = process_title(title)
  info = process_info(temp0)
  return title, body, info, categories, links,  references


def process_categories(text):
  # print("Inside process_categories")
  categories = []
  data = text.split('\n')
  for line in data:
    if re.match(r'\[\[category', line):
      x = re.sub(r'\[\[category:(.*)\]\]', r'\1', line)
      categories.append(x)
  tmp = ' '.join(categories)
  data = tokenize(tmp)
  data = processing(data)
  return data;

def process_title(text):
  # print("Inside process_title")
  data = tokenize(text)
  data = processing(data)
  return data;

def process_body(text):
  # print("Inside process_body")
  data = re.sub(r'\{\{.[^}}]*\}\}', r' ', text)
  data = tokenize(data)
  data = processing(data)
  return data;

def process_info(text):
  # print("Inside process_info")
  data = text.split('\n')
  info = []
  str = "}}"
  flag = -1
  for line in data:
      if re.match(r'\{\{infobox', line):
          x = re.sub(r'\{\{infobox(.*)', r'\1', line)
          info.append(x)
          flag = 0
      elif flag == 0:
          if line == str:
              flag = -1
              continue
          info.append(line)
  tmp = ' '.join(info)
  data = tokenize(tmp)
  data = processing(data)
  return data;

def process_links(text):
  # print("Inside process_links")
  links = []
  data = text.split('\n')
  for line in data:
      if re.match(r'\*[\ ]*\[', line):
          links.append(line)
  tmp = ' '.join(links)
  data = tokenize(tmp)
  data = processing(data)
  return data;


def process_references(text):
  # print("Inside process_references")
  refs = []
  data = text.split('\n')
  for line in data:
      if re.search(r'<ref', line):
          x = re.sub(r'.*title[\ ]*=[\ ]*([^\|]*).*', r'\1', line)
          refs.append(x)
  tmp = ' '.join(refs)
  data = tokenize(tmp)
  data = processing(data)
  return data;


def create_index(title, body, info, categories, links, references):
  # print("Inside createIndex")
  global pageCount
  global postList
  global docID
  global fileCount
  global offset
  ID = pageCount

  words = defaultdict(int)
  d = defaultdict(int)

  for word in title:
      d[word] += 1
      words[word] += 1
  title = d

  d = defaultdict(int)
  for word in body:
      d[word] += 1
      words[word] += 1
  body = d

  d = defaultdict(int)
  for word in info:
      d[word] += 1
      words[word] += 1
  info = d

  d = defaultdict(int)
  for word in categories:
      d[word] += 1
      words[word] += 1
  categories = d

  d = defaultdict(int)
  for word in links:
      d[word] += 1
      words[word] += 1
  links = d

  d = defaultdict(int)
  for word in references:
      d[word] += 1
      words[word] += 1
  references = d

  for word in words.keys():
    string ='d'+(str(ID))
    if(title.get(word) != None):
      string += 't' + str(title[word])
    if(body.get(word) != None):
      string += 'b' + str(body[word])
    if(info.get(word) != None):
      string += 'i' + str(info[word])
    if(categories.get(word) != None):
      string += 'c' + str(categories[word])
    if(links.get(word) != None):
      string += 'l' + str(links[word])
    if(references.get(word) != None):
      string += 'r' + str(references[word])
    postList[word].append(string)
  
  pageCount = pageCount + 1
  if(pageCount % 20000 == 0):
    offset = writeinfile(postList, docID, fileCount , offset)
    postList = defaultdict(list)
    docID = {}
    fileCount = fileCount + 1

# def file_dump(indexPath,postList):
#   data = postList
#   with open(indexPath, 'wb') as handle:
#     pickle.dump(data, handle, protocol = -1)


# def index_stat(path, indexTokenSize, xmlTokenSize):
#   stats = str(xmlTokenSize)+"\n"+str(indexTokenSize)
#   f = open(path, "w")
#   f.write(stats)
#   f.close()


def writeinfile(postList, docID, fileCount , offs):	
    sorted(docID)
    dOffs = "" 
    pOffs = offs
    data = ""
    for key in sorted(postList.keys()):
        entries = postList[key]
        string = key + ' '
        string += ' '.join(entries)
        data += (string +'\n')
    filePath = './files/index' 
    fName = filePath + str(fileCount)
    fName += '.txt'
    with open(fName, 'w') as f:
        f.write(data)

    data =  ""
    for key in docID:
        temp = str(key) + ' ' + docID[key].strip()
        if len(temp) == 0:
            pOffs = 1 + pOffs
        else:
            pOffs = 1 + pOffs + len(temp)
           
        data += (temp + "\n")
        dOffs += (str(pOffs) + "\n")
    fName = './files/titleOffset.txt'
    with open(fName, 'a') as f:
        f.write(dOffs)
       
    fName = './files/title.txt'
    with open(fName, 'a') as f:
        f.write(data)
    
    return pOffs


class writeThread(threading.Thread):
    def __init__(self, field, data, offs, count):
        threading.Thread.__init__(self)
        self.field = field
        self.offs = offs
        self.data = data
        self.count = count
        countType = type(count)
    def run(self):
        store = str(self.count)
        strCount = store
        filePath = './files/' 
        fileName = filePath + self.field 
        fileName += strCount + '.txt'
        with open(fileName, 'w') as f:
            f.write('\n'.join(self.data))
            fType = type(f)
        filePath = './files/offset_'     
        fileName = filePath + self.field + strCount + '.txt'
        fileNameType = type(fileName)
        with open(fileName, 'w') as f:
            f.write('\n'.join(self.offs))
            fType = type(f)



def final_write(data, finalC, offsSize):
    title = defaultdict(dict)
    info = defaultdict(dict)
    link = defaultdict(dict)
    body = defaultdict(dict)
    category = defaultdict(dict)
    offs = []
    distinct = []
    for key in tqdm(sorted(data.keys())):
        keyLen = len(key)
        store = []
        docums = data[key]
        zero = 0
        documsLen = len(docums)
        for i in range(documsLen):
            posting = docums[i]
            postingType = type(posting)
            store = re.sub(r'.*c([0-9]*).*', r'\1', posting)
            storeType = type(store)
            docID = re.sub(r'.*d([0-9]*).*', r'\1', posting)
            storeLen = len(store)
            if storeLen > 0 and posting != store:
                processStore = float(store)
                category[key][docID] = processStore
            store = re.sub(r'.*i([0-9]*).*', r'\1', posting)
            storeLen = len(store)
            storeType = type(store)
            if storeLen > 0 and posting != store:
                processStore = float(store)
                info[key][docID] = processStore
            store = re.sub(r'.*l([0-9]*).*', r'\1', posting)
            storeType = type(store)
            storeLen = len(store)
            if storeLen > 0 and posting != store:
                processStore = float(store)
                link[key][docID] = processStore
            store = re.sub(r'.*b([0-9]*).*', r'\1', posting)
            storeType = type(store)
            storeLen = len(store)
            if storeLen > 0 and posting != store:
                processStore = float(store)
                body[key][docID] = processStore
            store = re.sub(r'.*t([0-9]*).*', r'\1', posting)
            storeType = type(store)
            storeLen = len(store)
            if storeLen >0 and posting != store:
                title[key][docID] = float(store)
           
        string = key + ' ' + str(finalC) + ' ' + str(len(docums))
        offs.append(str(offsSize))
        offsType = type(offs)
        offsSize += len(string) + 1
        distinct.append(string)
    categData = []
    categOffs = []
    prevCateg = zero
    bodyData = []
    bodyOffs = []
    prevBody = zero
    linkData = []
    linkOffs = []
    prevLink = zero
    infoData = []
    infoOffs = []
    prevInfo = zero
    titleData = []
    titleOffs = []
    prevTitle = zero
    for key in tqdm(sorted(data.keys())):
        if key in link:
            docums = link[key]
            documsType = type(docums)
            docums = sorted(docums, key = docums.get, reverse=True)
            string = key + ' '
            for docum in docums:
                string = string + docum + ' ' + str(link[key][docum]) + ' '
            linkData.append(string)
            linkDataType = type(linkData)
            strLenDocums = str(len(docums))
            linkOffs.append(str(prevLink) + ' ' + strLenDocums)
            prevLink = prevLink + len(string) + 1
        if key in info:
            keyLen = len(key)
            docums = info[key]
            documsType = type(docums)
            docums = sorted(docums, key = docums.get, reverse=True)
            string = key + ' '
            for docum in docums:
                string = string + docum + ' ' 
                string = string + str(info[key][docum]) + ' '
            infoData.append(string)
            infoDataType = type(infoData)
            strLenDocums = str(len(docums))
            infoOffs.append(str(prevInfo) + ' ' + strLenDocums)
            prevInfo += len(string) + 1
        if key in body:
            docums = body[key]
            documsType = type(docums)
            docums = sorted(docums, key = docums.get, reverse=True)
            string = key + ' '
            for docum in docums:
                tempo1 = str(body[key][docum])
                string = string + docum + ' ' + tempo1 + ' '
            bodyData.append(string)
            tempo2 = str(len(docums))
            bodyOffs.append(str(prevBody) + ' ' + tempo2)
            prevBody = prevBody + len(string) + 1
        if key in category:
            keyLen = len(key)
            docums = category[key]
            documsType = type(docums)
            docums = sorted(docums, key = docums.get, reverse=True)
            string = key + ' '
            for docum in docums:
                string = string + docum + ' ' + str(category[key][docum]) + ' '
            categData.append(string)
            strLenDocums = str(len(docums))
            categOffs.append(str(prevCateg) + ' ' + strLenDocums)
            prevCateg = prevCateg + len(string) + 1
        if key in title:
            keyLen = len(key)
            docums = title[key]
            documsType = type(docums)
            docums = sorted(docums, key = docums.get, reverse=True)
            string = key + ' '
            for docum in docums:
                string = string + docum + ' ' + str(title[key][docum]) + ' '
            titleData.append(string)
            titleOffs.append(str(prevTitle) + ' ' + str(len(docums)))
            prevTitle = prevTitle + len(string) + 1
    thread = []
    thread.append(writeThread('t', titleData, titleOffs, finalC))
    thread.append(writeThread('b', bodyData, bodyOffs, finalC))
    thread.append(writeThread('i', infoData, infoOffs, finalC))
    thread.append(writeThread('c', categData, categOffs, finalC))
    thread.append(writeThread('l', linkData, linkOffs, finalC))
    i = zero
    total = 5
    while(i < total):
        thread[i].start()
        i += 1
    i = 0
    while(i < total):
        thread[i].join()
        i += 1
    fileName = './files/offset.txt' 
    with open(fileName, 'a') as f:
        f.write('\n'.join(offs))
        f.write('\n')
        fType = type(f)
    fileName = './files/vocab.txt' 
    with open(fileName, 'a') as f:
        f.write('\n'.join(distinct))
        f.write('\n')
    return offsSize , finalC+1



def merge_files(fileC):
    flagList = []
    for i in range(fileC):
      flagList.append(0)
    heap = []
    words = {}
    fCount = 0
    offsSize = 0
    data = defaultdict(list)
    top = {}
    files = {}
    # i = 0
    for i in range(fileC):
        file_path = './files/index'
        f_name = file_path + str(i)
        f_name = f_name + '.txt'
        files[i] = open(f_name, 'r')
        process_line = files[i].readline().strip()
        top[i] = process_line
        words[i] = top[i].split()
        x = words[i][0]
        if x not in heap:
            heapq.heappush(heap,x)
        flagList[i] = 1

    count = 0
    while any(flagList) == 1:
        temp = heapq.heappop(heap)
        count += 1
        if count%100000 == 0:
            oldCount = fCount
            offsSize, fCount = final_write(data, fCount, offsSize)
            if fCount != oldCount :
                data = defaultdict(list)
        # i = 0
        for i in range(fileC):
            if (flagList[i]):
                if temp == words[i][0]:
                    process_line = files[i].readline().strip()
                    top[i] = process_line
                    topType = type(top[i])
                    data[temp].extend(words[i][1:])
                    if top[i] != '':
                        words[i] = top[i].split()
                        if words[i][0] not in heap:
                            heapq.heappush(heap, words[i][0])
                    else:
                        flagList[i] = 0
                        files[i].close()                  
    offsSize, fCount = final_write(data, fCount, offsSize)



def file_handler(index, docID, outputPath):
    sorted(index.keys())
    # data = []
    data = ""
    for key in index.keys():
        strValue = key + ' '
        entry = index[key]
        strValue += ' '.join(entry)
        # data.append(strValue)
        data += (strValue + '\n')
        
    fileInp = outputPath 
    with open(fileInp, 'w') as f:
        # f.write('\n'.join(data))
        f.write(data)



if (__name__ == '__main__'):
  startTime = time.process_time()

  stop_words = set(stopwords.words('english'))
  docID = {}
  pageCount = 0 
  fileCount = 0 
  offset = 0
  argsLen = len(sys.argv)
  xmlFilePath = sys.argv[1]
  indexPath    = sys.argv[2]
  # indexStat    = sys.argv[3]
  stemmer = Stemmer.Stemmer('english')
  dirlist = os.listdir(xmlFilePath)
  # for fl in dirlist:
  #   parser = xml.sax.make_parser()
  #   parser.setFeature(xml.sax.handler.feature_namespaces, 0)
  #   handler = helperClass()
  #   parser.setContentHandler(handler)
  #   postList  = defaultdict(list)
  #   tokensCount = 0
  #   parser.parse(open(xmlFilePath+fl))

  #   file_handler(postList, docID,indexPath+fl)      
  #   offset = writeinfile(postList, docID, fileCount , offset)
  #   docID = {}
  #   fileCount = fileCount + 1
  # with open('./files/fileNumbers.txt', 'w') as f:
  #      f.write(str(pageCount))   
  # merge_files(fileCount)
  merge_files(525)
  # #index_stat(indexStat, len(postList.keys()), tokensCount)
  stopTime = time.process_time()
  print(stopTime - startTime)