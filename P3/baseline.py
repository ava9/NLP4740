#!/usr/bin/env python

import parseData as pd
# import parseQuestion as pq
import nltk
import numpy as np


TOPFILES = 10

def make10Grams(text):
  outArr = []
  tokens = nltk.word_tokenize(item)
  for i in range(len(tokens)-9):
    outArr.append(tokens[i:i+10])

def ngramSimilarity(ngram1, ngram2):
  score = 0
  # can optimize by looping through smaller ngram
  for tkn in ngram2:
    if tkn in ngram1: score += 1
  return score

def best10Grams(question, ngrams, topN = 5):
  question = set(nltk.word_tokenize(question))
  bestngrams = []
  bestScore = -1
  for ngram in ngrams:
    score = ngramSimilarity(question, set(ngram))
    if score > bestScore:
      bestngrams = [ngram]
      bestScore = score
    elif score == bestScore:
      bestngrams.append(ngram)

  truncated = []
  for ind in np.random.randint(len(bestngrams)-1, size=10): truncated.append(bestngrams[ind])
  return truncated

if __name__ == '__main__':
  data = pd.getAllData(TOPFILES)
  # questions = pq.getAllQuestions()
  questions = dict()


  for ID, fileDicts in data.iteritems():
    if ID not in questions: 
      print "error, ID mismatch"
      continue

    possibleAnswers = []
    for file in fileDicts:
      if 'text' in file:
        possibleAnswers += make10Grams(file['text'])

    bestgrams = best10Grams(questions[ID], possibleAnswers)
    # extract relevant data/answer for each ID

    # write answer for each ID