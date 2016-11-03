#!/usr/bin/env python

import parseData as pd
import parseQuestion as pq
import nltk
import random as rand
import operator

TOPFILES = 6

#take a text field contents and a fileID to make an array of
#10-grams and fileID tuples
def make10Grams(text, fileID):
  outArr = []
  tokens = nltk.word_tokenize(text)
  for i in range(len(tokens)-9):
    outArr.append((tokens[i:i+10],fileID))
  return outArr

#get the similarity of two ngrams (make them sets to optimize it)
def ngramSimilarity(ngram1, ngram2):
  score = 0
  if len(ngram2) > len(ngram1):
    temp = ngram1
    ngram1 = ngram2
    ngram2 = temp
  for tkn in ngram2:
    if tkn in ngram1: score += 1
  return score

#get the 5 best 10-grams for a question and an array of ngrams
def best10Grams(question, ngrams):
  questionLiteral = question
  question = set(nltk.word_tokenize(question))
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
    possibleAnswers = []
    for fileNum, file in fileDicts.iteritems():
      if 'text' in file and len(file['text'])>0:
        allText = reduce(operator.add, file['text'],'')
        possibleAnswers += make10Grams(file['text'][0], fileNum)
      else:
        print "File " + str(fileNum) + " for ID " + str(ID) + " has no text tag"

    #get the best answers
    bestgrams = best10Grams(questions[ID], possibleAnswers)

    if len(bestgrams)==0:
      outF.write(str(ID)+" 0 nil\n")
    for ngram, fileID in bestgrams:
      outF.write(str(ID)+" "+str(fileID)+" "+ngram+"\n")

  outF.close()