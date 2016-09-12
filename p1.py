import nltk
import re
import os
import random

endingChars = ".!?;"

def getCorpora():
  corpora = os.listdir("data_corrected/classification task/")
  corpora.remove(".DS_Store")
  corpora.remove("test_for_classification")
  return corpora

def preprocesssContent(content):
  #only keep the actual contents of the article
  content = content.split('writes : ')[-1]
  #These shouldn't be called, but just in case:
  content = content.split('From : ')[-1]
  content = content.split('To : ')[-1]
  content = content.split('Subject : ')[-1]
  content = content.split('Re : ')[-1]
  content = content.split('wrote : ')[-1]

  #remove email addresses
  emailPattern = '[\w\.-]+@[\w\.-]+'
  content = re.sub(emailPattern, '', content)

  #remove bad characters
  badChars = "][\^_`()}{*+-#\$%&/<=>@|~<>\|\"\\"
  badCharReg = re.compile('[%s]' % re.escape(badChars))
  content = badCharReg.sub('', content)

  return content

def getFileName(folderName, fileNumber):
  return "data_corrected/classification task/" + folderName + "/train_docs/" + folderName + "_file{}.txt".format(fileNumber)

def getFileContentTokens(folderName, fileNumber):
  fileName = getFileName(folderName, fileNumber)
  if os.path.exists(fileName):
    with open(fileName) as f:
      content = f.read()
      return nltk.word_tokenize(preprocesssContent(content))
  return []

def updateDict(keys, d):
  for k in keys:
    if j in d:
      d[k] += 1
    else:
      d[k] = 1
  return d

def totalsToPDFTokenArray(d):
  pdfArray = []
  for key in d:
    for i in range(d[key]):
      pdfArray.append(key)
  return pdfArray

def bigramPreprocess(tokens):
  newTokens = ["|"]
  for token in tokens:
    newTokens.append(token)
    if token in endingChars:
      newTokens.append("|")

  #might not be needed
  if newTokens[-1] != "|":
    newTokens.append("|")

  return newTokens

def getDict(folderName, isUnigram):
  d = dict()
  for fileNumber in range(300):
    tokens = getFileContentTokens(folderName, fileNumber)
    if not isUnigram:
      tokens = list(nltk.bigrams(bigramPreprocess(tokens)))
    d = updateDict(tokens, d)
  return d

def genRandWord(pdfArray):
  return pdfArray[random.randint(0,len(pdfArray)-1)]

def generateUnigramSentence(pdfArray):
  #get starting word
  word = genRandWord(pdfArray)
  while word in endingChars: 
    word = genRandWord(pdfArray)

  sentence = word
  #keep going till we get a ending symbol
  while word not in endingChars:
    word = genRandWord(pdfArray)
    sentence += " " + word
  return sentence

def generateBigramSentence(pdfArray):
  #get starting word
  tupl = genRandWord(pdfArray)
  while tupl[0] != "|" or tupl[1] in endingChars: 
    tupl = genRandWord(pdfArray)

  sentence = tupl[1]
  #keep going till we get a ending symbol
  while tupl[1] != "|" and tupl[0] not in endingChars:
    oldWord = tupl[1]
    tupl = genRandWord(pdfArray)
    while tupl[0] != oldWord: 
      tupl = genRandWord(pdfArray)
    sentence += " " + tupl[1]
  return sentence[:-2]

def demo():
  corpora = getCorpora()
  corpusToUse = corpora[random.randint(0,len(corpora)-1)]

  unipdfArray = totalsToPDFTokenArray(getDict(corpusToUse, 1))

  print "\nUnigram Sentences with the " + corpusToUse + " corpus:"
  for i in range(10):
    print generateUnigramSentence(unipdfArray)

  bipdfArray = totalsToPDFTokenArray(getDict(corpusToUse, 0))
  print "\n\n\nBigram Sentences with the " + corpusToUse + " corpus:"
  for i in range(10):
    print generateBigramSentence(bipdfArray)

def test():
  bipdfArray = totalsToPDFTokenArray(getDict('autos', 0))
  while 1:
    print generateBigramSentence(bipdfArray)

demo()