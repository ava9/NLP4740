from nltk import word_tokenize
import re
import os

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
      
  Bad_symbols = "[\]^_`()}{*+-#\$%&/<=>@|~<>\|\\"

  badCharReg = re.compile('[%s]' % re.escape(Bad_symbols))
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
    if token not in d:
      d[token] = 1
    else:
      d[token] += 1
  return d


def getAllFilesForUnigram(folderName):
  UDict = dict()
  for fileNumber in range(300):
    tokens = getFileContents(folderName, fileNumber)
    updateDict(tokens, UDict)
  return UDict


print getAllFilesForUnigram('motorcycles')