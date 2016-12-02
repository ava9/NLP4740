#!/usr/bin/env python

import parseData as pd
import parseQuestion as pq
import nltk
import re
import random as rand
import operator
import datefinder

TOPFILES = 10
INFILENAME = 'questionP2.txt'
TRAINFOLDER = 'doc_test/'
OUTPUTFILENAME = 'part2outputTest.txt'

# timeregex = r'([0-1]?[0-9]|2[0-3]):[0-5][0-9]'
yearregex = re.compile(r'\b\d{4}\b')

#take a text field contents and a fileID to make an array of
#10-grams and fileID tuples
def updatePossibleNES(possibleNES, text, fileID, score, possibleTags):
  """ specifically handle dates and (cant do duration)
   this is necessary because nltk's ner doesn't seem to be tagging dates. We would also have to 
   make a manual tagging for durations, but this shouldn't be necessary for when questions
   datefinder library is pretty bad too... this makes me sad"""
  if 'DATE' in possibleTags:
    matches = []
    try:
      matches += datefinder.find_dates(text)
    except Exception:
      pass
    t = yearregex.findall(text)
    for string in matches:
      string = str(string)
      if string in possibleNES: possibleNES[string] = (possibleNES[string][0] + score, possibleNES[string][1])
      else: possibleNES[string] = (score, fileID)
    return possibleNES

  # only tokenize documents that have unicode chars, drop data that doesnt
  try:
    tokens = nltk.word_tokenize(text)
  except UnicodeDecodeError:
    return possibleNES

  # update entities dictionary
  posTokens = nltk.pos_tag(tokens)
  nes = nltk.ne_chunk(posTokens)
  for ne in nes:
    try:
      lab = ne.label()
      string = reduce(lambda x,y: x + " " + y, [tupl[0] for tupl in ne],'') 
      if lab in possibleTags:
        if string in possibleNES: possibleNES[string] = (possibleNES[string][0] + score, possibleNES[string][1])
        else: possibleNES[string] = (score, fileID)
    except AttributeError, e:
      pass
    except Exception, e:
      print possibleNES[string]
      raise e
  return possibleNES

if __name__ == '__main__':
  #get all data and questions
  data = pd.getAllData(TOPFILES)
  questions = pq.getQuestions(INFILENAME)
  #prep output
  outF = open(OUTPUTFILENAME,'w')

  #loop through all ids and files
  for ID, fileDicts in data.iteritems():
    #ensure data and questions are consistent
    if ID not in questions: 
      print "error, ID mismatch for questions and data"
      continue

    #get array of possible answers (tagged entities)
    possibleNES = dict()
    for fileNum, file in fileDicts.iteritems():
      if 'text' in file and len(file['text'])>0:
        allText = reduce(operator.add, file['text'],'')
        possibleNES = updatePossibleNES(possibleNES, allText, fileNum, file[pd.SCORETAG], questions[ID][1])
      else:
        print "File " + str(fileNum) + " for ID " + str(ID) + " has no text tag"

    possibleNESArr = []

    # get best answers from dictionary
    for ne, (score, fileID) in possibleNES.iteritems():
      possibleNESArr.append((ne, score, fileID))
    bestAnswers = map(lambda x: (x[0], x[2]), sorted(possibleNESArr, key = lambda x: x[1], reverse = True))
    bestAnswers = bestAnswers[0:5]

    if len(bestAnswers)==0:
      outF.write(str(ID)+" 0 nil\n")

    print (ID, bestAnswers)

    for (ne, fileID) in bestAnswers:
      outF.write(str(ID)+" "+str(fileID)+" "+ne+"\n")

  outF.close()