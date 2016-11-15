#!/usr/bin/env python

import parseData as pd
import parseQuestion as pq
import nltk
import random as rand
import operator

TOPFILES = 6

#take a text field contents and a fileID to make an array of
#10-grams and fileID tuples
def updatePossibleNES(possibleNES, text, fileID, score, possibleTags):
  tokens = nltk.word_tokenize(text)
  posTokens = nltk.pos_tag(tokens)
  nes = nltk.ne_chunk(posTokens)
  for ne in nes:
    try:
      lab = ne.label()
      if lab in possibleNES: possibleNES[lab][0] += score
      else: possibleNES[lab] = (score, fileID)
    except AttributeError, e:
      pass
  return possibleNES


#get the 5 best 10-grams for a question and an array of ngrams
def best10Grams(question, ngrams, nerArr):
  questionLiteral = question
  question = set(nltk.word_tokenize(question))
  print "i got here"
  filteredNgrams = []
  for tup in ngrams:
    ngramPOS = nltk.pos_tag(tup[0])
    ngramNER = nltk.ne_chunk(ngramPOS)
    for i in range(len(ngramNER)):
      try:
        if ngramNER[i].label() in nerArr:
          filteredNgrams.append(tup)
          break
      except: 
        pass
  ngrams = filteredNgrams
  print "finsihed loop" 
  bestngrams = []
  bestScores = []
  minBestScore = -1
  for ngram, fileID in ngrams:
    score = ngramSimilarity(question, set(ngram))
    if len(bestngrams) < 5:
      bestScores.append(score)
      bestngrams.append((reduce(lambda x,y: x + " " + y, ngram,''),fileID,score))
      minBestScore = min(bestScores)
    elif score > minBestScore:
      ind = bestScores.index(minBestScore)
      bestngrams[ind] = (reduce(lambda x,y: x + " " + y, ngram,''),fileID,score)
      bestScores[ind] = score
      minBestScore = min(bestScores)

  bestngrams = map(lambda x: (x[0],x[1]),sorted(bestngrams, key = lambda x: x[2]))

  if len(bestngrams) == 0:
    #debug output
    print "there are no ngrams for question: "+questionLiteral
  return bestngrams

if __name__ == '__main__':
  #get all data and questions
  data = pd.getAllData(TOPFILES)
  questions = pq.getQuestions()
  #prep output
  outF = open('baselineOutput.txt','w')

  #loop through all ids and files
  for ID, fileDicts in data.iteritems():
    #ensure data and questions are consistent
    if ID not in questions: 
      print "error, ID mismatch for questions and data"
      continue

    #get array of possible answers (10grams)
    possibleNES = dict()
    for fileNum, file in fileDicts.iteritems():
      if 'text' in file and len(file['text'])>0:
        allText = reduce(operator.add, file['text'],'')
        possibleNES = updatePossibleNES(possibleNES, allText, fileNum, file[pd.SCORETAG], questions[ID][[1]])
      else:
        print "File " + str(fileNum) + " for ID " + str(ID) + " has no text tag"

    #get the best answers
    possibleNESArr = []
    for ne, (score, fileID) in possibleNES:
      possibleNESArr.append((ne, score, fileID))
    
    bestAnswers = filter(lambda x: (x[0], x[2]), sorted(possibleNESArr, key = lambda x: x[1]))

    if len(bestgrams)==0:
      outF.write(str(ID)+" 0 nil\n")
    for (ne, fileID) in bestgrams:
      outF.write(str(ID)+" "+str(fileID)+" "+ne+"\n")

  outF.close()