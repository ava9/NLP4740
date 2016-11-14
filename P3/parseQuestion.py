#!/usr/bin/env python

import os

def getQuestions():
  questionDict = dict()

  f = open('question.txt','r')

  lastQID = 0
  for line in f.readlines():
    line = line.strip()

    if line:
      pieces = line.split(' ')
      if pieces[0] == '<num>':
        qid = int(pieces[2])
        questionDict[qid] = ''
        lastQID = qid
      elif pieces[0][0] != '<':
        # tuple is ('question', 'first word in question') 
        # first word in question (who, what, when, where, where's, who's) used in p2
        questionDict[lastQID] = (line, line.partition(' ')[0])

  return questionDict

if __name__ == '__main__':
  print getQuestions()

