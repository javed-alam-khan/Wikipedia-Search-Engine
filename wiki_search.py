import nltk
# nltk.download('punkt')
# nltk.download('stopwords')
from nltk.corpus import stopwords


import math
import re
import timeit
import Stemmer
import sys
from collections import defaultdict
from random import randint


def remove_special(text):
    text = re.sub(r'[^A-Za-z0-9]+', r' ', text)
    textLen = len(text)
    return text

def tokenize(text):
    text = text.encode("ascii", errors="ignore").decode()
    text = re.sub(r'[^A-Za-z0-9]+', r' ', text)
    tokens = text.split()
    return tokens

def remove_stopwords(text):
  global stop_words
  return [word for word in text if word not in stop_words]

def stem(text):
  text = stemmer.stemWords(text)
  return text

def processing(data):
  data = remove_stopwords(data)
  data = stem(data)
  return data

def obtain_num_file(offs, w, l, h, f, ofType = 'str'):
    # print("l ",l)
    # print("h ",h)
    while True:
        if (l>=h):
           break
        else:
            m = int((l + h) / 2)
            f.seek(offs[m])
            wPointer = f.readline().strip().split()
            if (ofType != 'int'):
                if (wPointer[0] == w):
                    tempo1 = wPointer[1:]
                    return m, tempo1
                elif (w <= wPointer[0]):
                    h = m
                else:
                    l = m + 1
            else:
                if (int(wPointer[0]) == int(w)):
                    tempo2 = wPointer[1:]
                    return m, tempo2
                elif (int(w) <= int(wPointer[0])):
                    h = m
                else:
                    l = m + 1
    return -1, []

def obtain_docum(fileName, w, fileNum, field, fieldFile):
    documFreq = []
    fieldOffs = [] 
    filePath = './files/offset_'
    filePath = filePath + field
    filePath = filePath + fileNum
    with open(filePath +'.txt') as fObj:
        for lv in fObj:
            offs = lv.strip().split()[0]
            df = lv.strip().split()[1]
            documFreq.append(int(df))
            fieldOffs.append(int(offs))
    zero = 0
    fieldOffsLen = len(fieldOffs)        
    m, documList = obtain_num_file(fieldOffs, w, zero, fieldOffsLen, fieldFile)
    # print(m)
    # print(documList)
    return documFreq[m], documList

def ranking(nFiles, queryType, results, documFreq):
    # print("results", results)
    # print("nFiles",nFiles)
    documFreqLen = len(documFreq)
    if (queryType == 's'):
            valueList = [0.05, 0.40, 0.05, 0.40, 0.10]   #l, b, i, t, c
    else:
            valueList = [0.10, 0.40, 0.10, 0.40, 0.10]   #l, b, i, t, c
    docums = defaultdict(float)
    queryIdf = {}
    
  
    for key in documFreq:
        comp1 = (float(nFiles) - float(documFreq[key]) + 0.5)
        comp2 = (float(documFreq[key]) + 0.5)
        num = comp1 / comp2
        queryIdf[key] = math.log(num)
        temp1 = float(nFiles)
        temp2 = float(documFreq[key])
        temp =  temp1/temp2 
        documFreq[key] = math.log(temp)
    for word in results:
        fieldPostingList = results[word]
        zero = 0
        one = 1
        two = 2
        three = 3
        four = 4
        for field in fieldPostingList:
                if (len(field) > zero):
                    field = field
                    postingList = fieldPostingList[field]
                if (field == 'l'):
                    factor = valueList[zero]
                if (field == 'b'):
                    factor = valueList[one]
                if (field == 'i'):
                    factor = valueList[two]
                if (field == 't'):
                    factor = valueList[three]
                if (field == 'c'):
                    factor = valueList[four]
                i = zero
                size_post = len(postingList)
                while (i < size_post):
                    # print("postingList[i]",postingList[i])
                    comp3 = 1 + math.log(float(postingList[i+1]))
                    temp = (comp3) * documFreq[word]
                    comp4 = docums[postingList[i]] + float(temp * factor)
                    docums[postingList[i]] = comp4
                    # print("docums[postingList[i]]",docums[postingList[i]])
                    i = i + 2
    return docums

def getQueryList(path):
    fp = open(path,"r")
    query = []
    
    for line in fp:
        temp = line.strip().split(',')
        query.append((int(temp[0]),temp[1].lower()))
    return query



def begin_search(interrog, topResults):
    # print(interrog)
    print('Loading.........\n')
    fileName = './files/titleOffset.txt'
    fileNameType = type(fileName)
    with open(fileName, 'r') as fObj:
        for lv in fObj:
            processVal1 = int(lv.strip())
            titleOffs.append(processVal1)
    fileName = './files/offset.txt'
    with open(fileName, 'r') as fObj:
        for lv in fObj:
            processVal2 = int(lv.strip())
            offs.append(processVal2)
    # print("length", len(offs))
    fObj = open('./files/fileNumbers.txt', 'r')
    processFObj = fObj.read().strip();
    nFiles = int(processFObj)
    fObj.close()
    titleFile = open('./files/title.txt', 'r')
    fVocab = open('./files/vocab.txt', 'r')
    fvocabType = type(fVocab)
    titleOffsetLen = len(titleOffs)
    resFileObj = open('2019201035_queries_op.txt', 'w')
    # while (True):
    variab = 0
    for q in interrog:
        noResults = topResults[variab]
        variab += 1
        query = q.strip()
        # print(query)
        query = query.lower()
        queryLen = len(query)
        startTime = timeit.default_timer()
        if re.match(r'[t|b|i|c|l]:', query):
            tempFields = re.findall(r'([t|b|c|i|l]):', query)
            words = re.findall(r'[t|b|c|i|l]:([^:]*)(?!\S)', query)
            fields = []
            tokens = []
            zero = 0
            i = zero
            while(i < len(words)):
                for word in words[i].split():
                    fields.append(tempFields[i])
                    tokens.append(word)
                i = i+1
            tokens = processing(tokens)
            results, documFreq = field_query(tokens, fields, fVocab)
            results = ranking(nFiles, 'f', results, documFreq)
        else:
            tokens = tokenize(query)
            tokens = processing(tokens)
            results, documFreq = simple_query(fVocab, tokens)
            results = ranking(nFiles, 's',results, documFreq)

        # print('\nResults:')
        # queryResWrite(results)
        resultsLen = len(results)
        if (resultsLen > 0):
            results = sorted(results, key = results.get, reverse = True)
            # topRes = results[:noResults]
            # results = topRes
        myCount = 0
        for key in results:
          # print("key", key)
          store, title = obtain_num_file(titleOffs, key, 0, titleOffsetLen, titleFile, 'int')
          titleLen = len(title)
          # print(type(title))
          # print(title)
          resFileObj.write(str(key) + " " + title[0] + "\n")
          # print(' '.join(title))
          myCount += 1
          if(myCount == noResults):
          	break

        endTime = timeit.default_timer()
        # print('Time =', endTime - startTime)
        resFileObj.write(str(endTime - startTime) + "\n\n")
    resFileObj.close()

def field_query(words, fieldList, fVocab):
    documFreq = {}
    documList = defaultdict(dict)
    zero = 0
    i = zero
    wordsLen = len(words)
    while (i < wordsLen):
        w = words[i]
        field = fieldList[i]
        m, docums = obtain_num_file(offs, w, zero, len(offs), fVocab)
        if (len(docums) > zero):
            fileNum = docums[zero]
            fileName = './files/' + field
            fileName = fileName + str(fileNum) 
            fileName = fileName + '.txt'
            fieldFile = open(fileName, 'r')
            df, returnList = obtain_docum(fileName, w, fileNum, field, fieldFile)
            # dfLen = len(df)
            documFreq[w] = df
            documList[w][field] = returnList
        i = i + 1
    return documList, documFreq

def simple_query(fvocab, words):
    fieldList = []
    fieldList.append('t')
    fieldList.append('b')
    fieldListLen = len(fieldList)
    fieldList.append('i')
    fieldList.append('c')
    fieldList.append('l')
    documFreq = {}
    documList = defaultdict(dict)
    for w in words:
        zero = 0
        m, docums = obtain_num_file(offs, w, 0, len(offs), fvocab)
        documsLen = len(docums)
        if (documsLen > 0):
            fileNum = docums[zero]
            documFreq[w] = docums[zero+1]
            for field in fieldList:
                fieldLen = len(field)
                fileName = './files/' + field
                strFileNum = str(fileNum)
                fileName = fileName + strFileNum
                fileName = fileName + '.txt'
                fieldFile = open(fileName, 'r')
                store, returnList = obtain_docum(fileName, w, fileNum, field, fieldFile)
                returnListLen = len(returnList)
                documList[w][field] = returnList
    return documList, documFreq

if __name__ == '__main__':
    query_path  = sys.argv[1]
   
    stop_words = set(stopwords.words('english'))
    stemmer = Stemmer.Stemmer('english')
    titleOffs = [] 
    offs = []
    qry_lst = getQueryList(query_path)
    query = [x[1] for x in qry_lst]
    
    noResults = [x[0] for x in qry_lst]
    begin_search(query, noResults)