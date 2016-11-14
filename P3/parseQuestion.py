#!/usr/bin/env python

import os

def getNER(firstWord):
  # All NERs
  #['LOCATION', 'ORGANIZATION', 'PERSON', 'DURATION', 'DATE', 'CARDINAL', 'PERCENT', 'MONEY', 'MEASURE']
  
  # Location
  whereArr = ['LOCATION']

  # Person or Organization
  whoArr = ['PERSON','ORGANIZATION']

  # All of the above
  whatArr = ['LOCATION', 'ORGANIZATION', 'PERSON', 'DURATION', 'DATE', 'CARDINAL', 'PERCENT', 'MONEY', 'MEASURE']

  # Date or Time
  whenArr = ['DATE', 'DURATION']

  if firstWord == 'Where':
    return whereArr
  elif firstWord == "Where's":
    return whereArr
  elif firstWord == 'Who':
    return whoArr
  elif firstWord == "Who's":
    return whoArr
  elif firstWord == 'What':
    return whatArr
  elif firstWord == "What's":
    return whatArr
  elif firstWord == 'When':
    return whenArr
  elif firstWord == "When's":
    return whenArr
  else:
    return []

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
        firstWord = line.partition(' ')[0]
        nersToConsider = getNER(firstWord)
        questionDict[lastQID] = (line, nersToConsider)

  return questionDict

if __name__ == '__main__':
  print getQuestions()

