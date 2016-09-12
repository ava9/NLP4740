import nltk
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
      
  removedChars = "][\^_`()}{*+-#\$%&/<=>@|~<>\|\"\\"

  badCharReg = re.compile('[%s]' % re.escape(removedChars))
  content = badCharReg.sub('', content)

  return content

def getFileName(folderName, fileNumber):
  return "data_corrected/classification task/" + folderName + "/train_docs/" + folderName + "_file{}.txt".format(fileNumber)

def getFileContents(folderName, fileNumber):
  fileName = getFileName(folderName, fileNumber)
  if os.path.exists(fileName):
    with open(fileName) as f:
      content = f.read()
      return nltk.word_tokenize(preprocesssContent(content))
  return []

def updateDict(tokens, d):
  for token in tokens:
    if token in d:
      d[token] += 1
    else:
      d[token] = 1
  return d

def totalsToCDFTokenArray(d):
  cdfArray = []
  for token in d:
    for i in range(d[token]):
      cdfArray.append(token)
  return cdfArray

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
  UDict = dict()
  for fileNumber in range(300):

    tokens = getFileContents(folderName, fileNumber)
    if not isUnigram:
      tokens = list(nltk.bigrams(bigramPreprocess(tokens)))
    UDict = updateDict(tokens, UDict)
  return UDict

def genRandWord(cdfArray):
  i = random.randint(0,len(cdfArray)-1)
  return cdfArray[i]

def generateUnigramSentence(cdfArray):
  #get starting word
  word = genRandWord(cdfArray)
  while word in endingChars: 
    word = genRandWord(cdfArray)

  sentence = word
  #keep going till we get a ending symbol
  while word not in endingChars:
    word = genRandWord(cdfArray)
    sentence += " " + word
  return sentence

def generateBigramSentence(cdfArray):
  #get starting word
  tupl = genRandWord(cdfArray)
  #might need to change this
  while tupl[0] != "|" or tupl[1] in endingChars: 
    tupl = genRandWord(cdfArray)

  sentence = tupl[1]
  #keep going till we get a ending symbol
  while tupl[1] != "|" and tupl[0] not in endingChars:
    oldWord = tupl[1]
    tupl = genRandWord(cdfArray)
    while tupl[0] != oldWord: 
      # print oldWord
      # print sentence
      tupl = genRandWord(cdfArray)
    sentence += " " + tupl[1]
  return sentence[:-2]

def demo():
  uniCDFArray = totalsToCDFTokenArray(getDict('motorcycles', 1))

  print "Unigram Sentences:"
  for i in range(10):
    print generateUnigramSentence(uniCDFArray)
  print "\n\n\n"
  biCDFArray = totalsToCDFTokenArray(getDict('motorcycles', 0))
  print "Bigram Sentences:"
  for i in range(10):
    print generateBigramSentence(biCDFArray)

def test():
  biCDFArray = totalsToCDFTokenArray(getDict('motorcycles', 0))
  while 1:
    print generateBigramSentence(biCDFArray)

demo()
# test()