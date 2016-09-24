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
def getFileName(folderName, fileNumber, spellCheck = False, isMod = False):
  modStr = ""
  if isMod: modStr = "_modified"
  if spellCheck:
    return "data_corrected/spell_checking_task/" + folderName + "/train" + modStr + "_docs/" + folderName + "_file{}".format(fileNumber) + modStr + ".txt"
  return "data_corrected/classification task/" + folderName + "/train_docs/" + folderName + "_file{}.txt".format(fileNumber)

#returns the file path of a document given the corpus and the file number
def getTestFileName(fileNumber, folderName = "", spellCheck = False):
  if spellCheck:
    return "data_corrected/spell_checking_task/" + folderName + "/test_modified_docs/" + folderName + "_file{}".format(fileNumber) + "_modified.txt"
  return "data_corrected/classification task/test_for_classification/" + "file_{}.txt".format(fileNumber)

#gets the tokens of a file given a corpus and file number (by preprocessing and tokenizing)
#returns the tokens if the file exists, or an empty array otherwise
def getFileContentTokens(folderName, fileNumber, isTest = False, spellCheck = False, isMod = False):
  if isTest:
    fileName = getTestFileName(fileNumber, spellCheck)
  else:
    fileName = getFileName(folderName, fileNumber, spellCheck, isMod)
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
def getDict(folderName, isUnigram):
  d = dict()
  if UNKNOWNS:
    seenTokens = dict()

  for fileNumber in range(300):
    tokens = getFileContentTokens(folderName, fileNumber)
    if UNKNOWNS:
      tokens = makeUnknowns(tokens, seenTokens)
    if not isUnigram:
      tokens = makeBigrams(bigramPreprocess(tokens))
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

def computePerplexity(dictionary, fileNumber, isUnigram):
  tokens = getFileContentTokens("dummy", fileNumber, True)
  total = 0.0
  if isUnigram:
    totalC = sum(dictionary.values())
    for tk in tokens:
      if tk not in dictionary:
        tk = unkToken
      elif unkToken not in dictionary:
        print "corpus is too small, be careful! there is no unknown token in the dictionary"
      total += math.log(float(dictionary[tk])/totalC)
  else:
    bigrams = makeBigrams(bigramPreprocess(tokens))
    subDict = getBigramSubDict(dictionary)
    for tupl in bigrams:
      if tupl not in dictionary:
        if (unkToken, tupl[1]) in dictionary:
          tupl = (unkToken, tupl[1])
        elif (tupl[0], unkToken) in dictionary:
          tupl = (tupl[0], unkToken)
        elif (unkToken, unkToken) in dictionary:
          tupl = (unkToken, unkToken)
        else:
          print "corpus is too small, be careful! there is no (unknown, unknown) bigram in the dictionary"
      total += math.log(float(dictionary[tupl])/subDict[tupl[0]])

  return math.exp(-total/len(tokens))

#assembles dictionary for up to 300 documents in a corpus
def getSpellCheckDict(folderName, isUnigram, isMod = False):
  d = dict()
  if UNKNOWNS:
    seenTokens = dict()

  for fileNumber in range(300):
    tokens = getFileContentTokens(folderName, fileNumber, False, True, isMod)
    if UNKNOWNS:
      tokens = makeUnknowns(tokens, seenTokens)
    if not isUnigram:
      tokens = makeBigrams(bigramPreprocess(tokens))
    d = updateDict(tokens, d)
  return d

def getAllDicts(spellCheck = False):
  isUnigram = 0
  corpora = getCorpora()
  if not spellCheck:
    dicts = []
    for i in range(len(corpora)):
      dicts.append(getDict(corpora[i],isUnigram))
    return dicts
  else:
    dicts = dict()
    dicts["good"] = []
    dicts["mod"] = []
    for i in range(len(corpora)):
      dicts["good"].append(getSpellCheckDict(corpora[i],isUnigram,False))
      dicts["mod"].append(getSpellCheckDict(corpora[i],isUnigram,True))
    return dicts

def topicClassification(totalFiles):
  dicts = getAllDicts()

  filename = "tempSubmission.csv"
  fid = open(filename, 'w')
  fid.write("Id,Prediction\n")

  for i in range(totalFiles):
    fileNumber = i
    if not i % 10: print "we at " + str(i)

    minPerp = 999999
    corpNum = 15
    for j in range(len(dicts)):
      currentPerp = computePerplexity(dicts[j],fileNumber, isUnigram)
      if currentPerp < minPerp:
        minPerp = currentPerp
        corpNum = j
    fid.write("file_" + str(fileNumber) + ".txt," + str(corpNum) + "\n")

  fid.close()
  
def performSpellCheck():
  #read the confusion set
  fileName = "data_corrected/spell_checking_task/confusion_set.txt"
  content = ""
  if os.path.exists(fileName):
    with open(fileName) as f:
      content = f.read()
  content = [s.strip() for s in content.splitlines()]
  content[0] = 'went want' #had to hardcode this, got some weird escape characters
  
  confusionDict = dict()

  for p in content:
    w1 = ""
    w2 = ""
    isFirst = 1
    for c in p:
      if c == " ": isFirst = 0
      if isFirst and c != " ":
        w1 += c
      elif c != " ":
        w2 += c
    confusionDict[w1] = w2
    confusionDict[w2] = w1

  #threshold for the probability for the switch (this can be adjusted for with a validation run)
  pThresh = 0

  #get dicts for the 7*2 corpora
  dicts = getAllDicts(True)
  corpora = getCorpora()
  for cpI in range(len(corpora)):
    for fileNumber in range(300):
      tokens = getFileContentTokens(corpora[cpI], fileNumber, True, True)
      testBigrams = makeBigrams(bigramPreprocess(tokens))
      fileStr = ""
      for i in range(len(testBigrams)-1):
        bg1 = testBigrams[i]
        tk = bg1[1]
        if bg1[1] in confusionDict:
          tk2 = confusionDict[bg1[1]]
          bg2 = (bg1[1],testBigrams[i+1][1])
          bg3 = (bg1[0],tk2)
          bg4 = (tk2,testBigrams[i+1][1])

          p1, p2 = 0, 0
          if bg1 in dicts["mod"][cpI] and bg3 in dicts["good"][cpI]:
            p1 = dicts["good"][cpI][bg3]-dicts["mod"][cpI][bg1]
          if bg2 in dicts["mod"][cpI] and bg4 in dicts["good"][cpI]:
            p2 = dicts["good"][cpI][bg4]-dicts["mod"][cpI][bg2]

          if (p1 + p2) > pThresh:
            #do the switch
            tk = tk2
        #add stuff to the file if it isnt a delimiter 
        if tk != "|":
          fileStr += tk + " "
      filename = "data_corrected/spell_checking_task/" + corpora[cpI] + "/test_docs/" + corpora[cpI] + "_file{}".format(fileNumber) + ".txt"
      fid = open(filename, 'w')
      fid.write(fileStr)
      fid.close()


#main demo of sentence generation
def demoSentenceGeneration():
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
  bipdfArray = totalsToPDFTokenArray(getDict(corpusToUse, 0))
  print "\n\n\nBigram Sentences with the " + corpusToUse + " corpus:"
  for i in range(10):
    print generateBigramSentence(bipdfArray)

  UNKNOWNS = 1

def test():
  pass

if __name__ == "__main__":
  performSpellCheck()
