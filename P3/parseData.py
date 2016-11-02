#!/usr/bin/env python

import os
from HTMLParser import HTMLParser

class MyParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.currTagStack = []
    self.currDataStack = []
    self.dataDict = dict()
    self.noTag = '<NoTag>'
    self.scoreTag = '<Score>'
    self.dataDict[self.noTag] = []

  def addScore(self):
    num = ''
    x = self.dataDict[self.noTag][0]
    i = len(x)-1
    while x[i] != ' ':
      num = x[i] + num
      i -= 1
    self.dataDict[self.scoreTag] = float(num)

  def handle_starttag(self, tag, attrs):
    self.currTagStack.append(tag)
    self.currDataStack.append([])

  def handle_endtag(self, tag):
    if self.currTagStack[-1] != tag:
      print "Incorrect End Tag Encountered"
    else:
      self.currTagStack.pop()
      if tag not in self.dataDict:
        self.dataDict[tag] = self.currDataStack.pop()
      else:
        self.dataDict[tag] += self.currDataStack.pop()

  def handle_data(self, data):
    processedData = data.strip().replace('\r\n', ' ').strip()
    if len(processedData) > 0:
      if len(self.currDataStack) == 0:
        self.dataDict[self.noTag].append(processedData)
        self.addScore()
      else:
        self.currDataStack[-1].append(processedData)

  def resetParser(self):
    self.currTagStack = []
    self.currDataStack = []
    self.dataDict = dict()
    self.dataDict[self.noTag] = []

def getQIDs():
  IDS = os.listdir("doc_dev/")
  intIDS = []
  for ID in IDS:
    try:
      intIDS.append(int(ID))
    except ValueError:
      continue
  return intIDS

def getAllData(TOPFILES = 10):
  ids = getQIDs()
  data = dict()
  p = MyParser()
  for ID in ids:
    data[ID] = [0 for x in range(TOPFILES+1)]
    for i in range(1,TOPFILES+1):
      f = open('doc_dev/' +str(ID)+'/'+str(i),'r')
      contents = f.read()
      p.feed(contents)
      data[ID][i] = p.dataDict
      p.resetParser()
      f.close()
  return data

if __name__ == '__main__':
  allData = getAllData()
  print "Extraction of Data Is Successful, (\"Tests\" passed)"
