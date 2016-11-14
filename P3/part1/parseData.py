#!/usr/bin/env python

import os
from HTMLParser import HTMLParser

#Custom Class to parse text files. Rough, needs to be refined 
#(esp for recognizing potential dates, text fields, etc.)
class MyParser(HTMLParser):
  def __init__(self):
    HTMLParser.__init__(self)
    self.currTagStack = []
    self.currDataStack = []
    self.dataDict = dict()
    self.noTag = '<NoTag>'
    self.scoreTag = '<Score>'
    self.dataDict[self.noTag] = []
    self.textMode = 0

  #adds score to data dictionary
  def addScore(self):
    num = ''
    x = self.dataDict[self.noTag][0]
    i = len(x)-1
    while x[i] != ' ':
      num = x[i] + num
      i -= 1
    self.dataDict[self.scoreTag] = float(num)

  #handles a start tag, adding tag to stack
  def handle_starttag(self, tag, attrs):
    if self.textMode == 0:
      self.currTagStack.append(tag)
      self.currDataStack.append([])
    if tag == "text":
      self.textMode = 1

  #pops data off stacks, adds to dictionary
  def handle_endtag(self, tag):
    if self.currTagStack[-1] != tag and not self.textMode:
      print "Incorrect End Tag Encountered"
    elif not self.textMode or tag == "text":
      if tag == "text":
        self.textMode = 0
      self.currTagStack.pop()
      if tag not in self.dataDict:
        self.dataDict[tag] = self.currDataStack.pop()
      else:
        self.dataDict[tag] += self.currDataStack.pop()

  #adds processed data to datastack when data encoutered
  def handle_data(self, data):
    processedData = data.strip().replace('\r\n', ' ').strip()
    if len(processedData) > 0:
      if len(self.currDataStack) == 0:
        self.dataDict[self.noTag].append(processedData)
        self.addScore()
      else:
        self.currDataStack[-1].append(processedData)

  #reset parser for new contents
  def resetParser(self):
    self.currTagStack = []
    self.currDataStack = []
    self.dataDict = dict()
    self.dataDict[self.noTag] = []

#get all question ids
def getQIDs():
  IDS = os.listdir("doc_dev/")
  intIDS = []
  for ID in IDS:
    try:
      intIDS.append(int(ID))
    except ValueError:
      continue
  return intIDS

#main function to get all data into a dictionary of dictionary of dictionaries
# this is a dictionary for every file for every QID
def getAllData(TOPFILES = 10):
  ids = getQIDs()
  data = dict()
  p = MyParser()
  for ID in ids:
    data[ID] = dict()
    for i in range(1,TOPFILES+1):
      f = open('doc_dev/' +str(ID)+'/'+str(i),'r')
      contents = f.read()
      p.feed(contents)
      data[ID][i]=p.dataDict
      p.resetParser()
      f.close()
  return data

#"tester"
if __name__ == '__main__':
  allData = getAllData()
  print "Extraction of Data Is Successful, (\"Tests\" passed)"
