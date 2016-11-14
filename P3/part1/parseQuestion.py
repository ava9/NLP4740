#!/usr/bin/env python

import os

def getQuestions():
  questionDict = dict()

  f = open('questionP1.txt','r')

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
        questionDict[lastQID] = line

  return questionDict

if __name__ == '__main__':
  print getQuestions()

