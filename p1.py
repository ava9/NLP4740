from nltk import word_tokenize
import re
import os
import random

endingChars = ".!?;"



def preprocesssContent(content):
  emailPattern = '[\w\.-]+@[\w\.-]+'
  content = re.sub(emailPattern, '', content)

  content = content.split('writes : ')[-1]
  #These shouldn't be called, but just in case:
  content = content.split('From : ')[-1]
  content = content.split('To : ')[-1]
  content = content.split('Subject : ')[-1]
  content = content.split('Re : ')[-1]
  content = content.split('wrote : ')[-1]
      
  removedChars = ",][\^_`()}{*+-#\$%&/<=>@|~<>\|\\"

  badCharReg = re.compile('[%s]' % re.escape(removedChars))
  content = badCharReg.sub('', content)

  multipleSpaces = '[\s]+'
  content = re.sub(multipleSpaces, ' ', content)

  return content

def getFileName(folderName, fileNumber):
  return "data_corrected/classification task/" + folderName + "/train_docs/" + folderName + "_file{}.txt".format(fileNumber)

def getFileContents(folderName, fileNumber):
  fileName = getFileName(folderName, fileNumber)
  if os.path.exists(fileName):
    with open(fileName) as f:
      content = f.read()
      return word_tokenize(preprocesssContent(content))
  return []

def updateDict(tokens, d):
  for token in tokens:
    if token in d:
      d[token] += 1
    else:
      d[token] = 1

def totalsToCDFTokenArray(d):
  cdfArray = []
  for token in d:
    for i in range(d[token]-1):
      cdfArray.append(token)
  return cdfArray

def getUnigramDict(folderName):
  UDict = dict()
  for fileNumber in range(300):
    tokens = getFileContents(folderName, fileNumber)
    updateDict(tokens, UDict)
  return UDict

def unaryGenRandWord(cdfArray):
  i = random.randint(0,len(cdfArray)-1)
  return cdfArray[i]


def generateUnigramSentence(folderName):
  cdfArray = totalsToCDFTokenArray(getUnigramDict(folderName))

  #get starting word
  word = unaryGenRandWord(cdfArray)
  while word in endingChars: 
    word = unaryGenRandWord(cdfArray)

  sentence = word
  #keep going till we get a ending symbol
  while word not in endingChars:
    word = unaryGenRandWord(cdfArray)
    sentence += " " + word
  return sentence

mydict = generateUnigramSentence('motorcycles')
print mydict