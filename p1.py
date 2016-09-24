import nltk
import re
import os
import random
import math

endingChars = ".!?;"
smoothingConstant = 5;
unkToken = "<unk>"
UNKNOWNS = 1
SMOOTHING = 1
VERBOSE = 0

#gets the corpora for the sentence generation task, removes OSX hidden file and classification task for now
def getCorpora():
  corpora = os.listdir("data_corrected/classification task/")
  if ".DS_Store" in corpora:
    corpora.remove(".DS_Store")
  corpora.remove("test_for_classification")
  return corpora

#given the content of a file in a string, preprocesses it to only have relevant words for the corpus
def preprocessContent(content):
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

#returns the file path of a document given the corpus and the file number
def getFileName(folderName, fileNumber):
  return "data_corrected/classification task/" + folderName + "/train_docs/" + folderName + "_file{}.txt".format(fileNumber)

#returns the file path of a document given the corpus and the file number
def getTestFileName(fileNumber):
  return "data_corrected/classification task/test_for_classification/" + "file_{}.txt".format(fileNumber)

#gets the tokens of a file given a corpus and file number (by preprocessing and tokenizing)
#returns the tokens if the file exists, or an empty array otherwise
def getFileContentTokens(folderName, fileNumber, isTest = False):
  if isTest:
    fileName = getTestFileName(fileNumber)
  else:
    fileName = getFileName(folderName, fileNumber)
  if os.path.exists(fileName):
    with open(fileName) as f:
      content = f.read()
      return nltk.word_tokenize(preprocessContent(content))
  elif VERBOSE:
    print "Could not find a file, numbered " + str(fileNumber)
  return []

#updates a frequency table dictionary of n-grams given the old dictionary and the new n-grams,
#returns the new dictionary
def updateDict(keys, d):
  for k in keys:
    if k in d:
      d[k] += 1
    else:
      d[k] = 1
  return d

#creates an array from an n-gram dictionary such that the number of occurances 
#of the n-gram in the array is equal to the frequency in the corpus
def totalsToPDFTokenArray(d):
  pdfArray = []
  for key in d:
    for i in range(d[key]):
      pdfArray.append(key)
  return pdfArray

#special preprocessing for bigrams
def nGramPreprocess(tokens):
  newTokens = ["|"]
  for token in tokens:
    newTokens.append(token)
    if token in endingChars:
      newTokens.append("|")

  #might not be needed
  if newTokens[-1] != "|":
    newTokens.append("|")
  return newTokens

#creating unknowns for words seen for the first time
def makeUnknowns(tokens, seenTokens):
  for i in range(len(tokens)):
    if tokens[i] not in seenTokens:
      seenTokens[tokens[i]] = 1
      tokens[i] = unkToken
  return tokens

def makeBigrams(tokens):
  bigrams = []
  for i in range(len(tokens)-1):
    bigrams.append((tokens[i],tokens[i+1]))

  return bigrams

def makeTrigrams(tokens):
  trigrams = []
  for i in range(len(tokens)-2):
    trigrams.append((tokens[i],tokens[i+1],tokens[i+2]))

  return trigrams

#assembles dictionary for up to 300 documents in a corpus
def getDict(folderName, n):
  d = dict()
  if UNKNOWNS:
    seenTokens = dict()

  for fileNumber in range(300):
    tokens = getFileContentTokens(folderName, fileNumber)
    if UNKNOWNS:
      tokens = makeUnknowns(tokens, seenTokens)
    if n == 2:
      tokens = makeBigrams(nGramPreprocess(tokens))
    elif n == 3:
      tokens = makeTrigrams(nGramPreprocess(tokens))
    d = updateDict(tokens, d)
  return d

#gets a random (uniform) word from a pdf array as described above
def genRandWord(pdfArray):
  return pdfArray[random.randint(0,len(pdfArray)-1)]

#generates a unigram sentence
def generateUnigramSentence(pdfArray):
  #get starting word (that isn't an ending character)
  word = genRandWord(pdfArray)
  while word in endingChars: 
    word = genRandWord(pdfArray)

  sentence = word
  #keep going until we get a ending symbol
  while word not in endingChars:
    word = genRandWord(pdfArray)
    sentence += " " + word
  return sentence

#generates a bigram sentence
def generateBigramSentence(pdfArray):
  #get starting word
  tupl = genRandWord(pdfArray)
  #makes sure the first token in the bigram is a beginning character
  while tupl[0] != "|" or tupl[1] in endingChars: 
    tupl = genRandWord(pdfArray)

  sentence = tupl[1]
  #keep going till we get an end of sentence symbol/endChar (same logic)
  while tupl[1] != "|" and tupl[0] not in endingChars:
    oldWord = tupl[1]
    #makes sure a new random word is generated, in case of a bigram where the tokens are the same
    tupl = genRandWord(pdfArray)
    while tupl[0] != oldWord: 
      tupl = genRandWord(pdfArray)
    sentence += " " + tupl[1]
  return sentence[:-2]

def goodTuring(bigrams):
  def calculateNc():
    d = {};

    counts = bigrams.values();
    for i in range(len(counts)):
      count = counts[i];
      if d.has_key(count):
        d[count] += 1;
      else:
        d[count] = 1;

    return d

  smoothedBigrams = {};
  allNc = calculateNc();

  keys = bigrams.keys();
  for j in range(len(keys)):
    key = keys[j];
    c = bigrams[key];
    if c >= smoothingConstant or (c+1) not in allNc:
      cstar = c
    else:
      nc = allNc[c];
      nc1 = allNc[c+1];
      cstar = (c+1.0)*nc1/nc;

    smoothedBigrams[key] = cstar

  return smoothedBigrams;

def getBigramSubDict(d):
  subD = dict()
  for tk, c in d.iteritems():
    tk = tk[0]
    if tk in subD:
      subD[tk] += c
    else:
      subD[tk] = c
  return subD

def computePerplexity(unigram,bigram,trigram,fileNumber,n):
  tokens = getFileContentTokens("dummy", fileNumber, True)
  total = 0.0
  if n == 1:
    totalC = sum(unigrams.values())
    for tk in tokens:
      if tk not in unigram:
        tk = unkToken
      elif unkToken not in unigram:
        print "corpus is too small, be careful! there is no unknown token in the unigram"
      total += math.log(float(unigram[tk])/totalC)
  elif n == 2:
    bigrams = makeBigrams(nGramPreprocess(tokens))
    subDict = getBigramSubDict(bigram)
    for tupl in bigrams:
      if tupl not in bigram:
        if (unkToken, tupl[1]) in bigram:
          tupl = (unkToken, tupl[1])
        elif (tupl[0], unkToken) in bigram:
          tupl = (tupl[0], unkToken)
        elif (unkToken, unkToken) in bigram:
          tupl = (unkToken, unkToken)
        else:
          print "corpus is too small, be careful! there is no (unknown, unknown) bigram in the bigram"
      total += math.log(float(bigram[tupl])/subDict[tupl[0]])
  else:
    trigrams = makeTrigrams(nGramPreprocess(tokens))

    for tupl in trigrams:
      if tupl not in trigram:
        if (unkToken, tupl[1], tupl[2]) in trigram:
          tupl = (unkToken, tupl[1], tupl[2])
        elif (unkToken, unkToken, tupl[2]) in trigram:
          tupl = (unkToken, unkToken, tupl[2])
        elif (unkToken, tupl[1], unkToken) in trigram:
          tupl = (unkToken, tupl[1], unkToken)
        elif (unkToken, unkToken, unkToken) in trigram:
          tupl = (unkToken, unkToken, unkToken)
        elif (tupl[0], unkToken, tupl[2]) in trigram:
          tupl = (tupl[0], unkToken, tupl[2])
        elif (tupl[0], tupl[1], unkToken) in trigram:
          tupl = (tupl[0], tupl[1], unkToken)
        elif (tupl[0], unkToken, unkToken) in trigram:
          tupl = (tupl[0], unkToken, unkToken)
        else:
          print "corpus is too small, be careful! there is no (unknown, unknown) bigram in the trigram"
      total += math.log(float(trigram[tupl])/bigram[(tupl[0],tupl[1])])

  return math.exp(-total/len(tokens))

def topicClassification(n):
  corpora = getCorpora()
  unigrams = []
  bigrams = []
  trigrams = []
  for i in range(len(corpora)):
    unigrams.append(getDict(corpora[i],1))
    bigrams.append(getDict(corpora[i],2))
    trigrams.append(getDict(corpora[i],3))

  for i in range(6):
    fileNumber = i
    minPerp = 999999
    corpNum = 15
    for j in range(len(unigrams)):
      currentPerp = computePerplexity(unigrams,bigrams[j],trigrams[j],fileNumber,n)
      if currentPerp < minPerp:
        minPerp = currentPerp
        corpNum = j

    print "file_" + str(fileNumber) + "," + str(corpNum)
    print "Perp: " + str(minPerp)
  

#main demo of sentence generation
def demo():
  global UNKNOWNS 
  UNKNOWNS = 0

  #get all the corpora and choose a random one
  corpora = getCorpora()
  corpusToUse = corpora[random.randint(0,len(corpora)-1)]

  #generate 10 unigram sentences
  unipdfArray = totalsToPDFTokenArray(getDict(corpusToUse, 1))

  print "\nUnigram Sentences with the " + corpusToUse + " corpus:"
  for i in range(10):
    print generateUnigramSentence(unipdfArray)

  #generate 10 bigram sentences
  bipdfArray = totalsToPDFTokenArray(getDict(corpusToUse, 2))
  print "\n\n\nBigram Sentences with the " + corpusToUse + " corpus:"
  for i in range(10):
    print generateBigramSentence(bipdfArray)

  UNKNOWNS = 1

def test():
  topicClassification(3)

if __name__ == "__main__":
  test()