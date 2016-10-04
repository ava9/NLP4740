# Project 2 Part 1
import os
import csv

BASELINE = 25
THRESHOLD = 0.1

# get tuples from a file's contents
def preProcess(content):
	outArr = []
	lines = content.split('\n')
	for line in lines:
		words = line.split('\t')
		outArr.append(words)
	return outArr

# preprocess content for a file if it exists
def getFileContents(folder, fileName):
	fileName = folder + "/" + fileName
	if os.path.exists(fileName):
		with open(fileName) as f:
			content = f.read()
			return preProcess(content)

# fetch all file names and then get their tuples from a folder
def getAllFileContents(folder):
	allWords = []
	docs = os.listdir(folder)
	for fileName in docs:
		fileWords = getFileContents(folder, fileName)
		# add to array
		allWords += fileWords
	return allWords

# build lexicons
def lexGenerator(tuples):
	# initialize variables
	uncertainDict = dict()
	lexicon = dict()

	# update uncertainSet
	for tupl in tuples:
		# make sure it is a tuple of at least 3 and it is a cue
		if (len(tupl) >= 3) and "CUE" in tupl[2]:
			if tupl[0] in uncertainDict:
				uncertainDict[tupl[0]] += 1
			else:
				uncertainDict[tupl[0]] = 1

	# sort list
	sortedList = sorted(uncertainDict, key=uncertainDict.get)
	sortedList.reverse()

	baselineForLexicon = BASELINE

	#update lexicon
	for i in range(min(baselineForLexicon,len(sortedList))):
		lexicon[sortedList[i]] = uncertainDict[sortedList[i]]

	return lexicon

def tagUncertaintyTuples(tuples, uncertainWords):
	for t in tuples:
		if (len(t) >= 2):
			if t[0] in uncertainWords:
				t.append("CUE")
			else:
				t.append("_")
	return tuples

def getRanges(tuples):
	ranges = []
	inRange = False
	for i in range(len(tuples)):
		t = tuples[i]
		if (len(t) >= 3) and "CUE" in t[2] and not inRange:
			ranges.append(str(i)+"-")
			inRange = True
		elif inRange and (((len(t) >= 3) and "CUE" not in t[2]) or (len(t) <3)):
			ranges[-1] += str(i-1)
			inRange = False
	if inRange:
		ranges[-1] += str(len(tuples)-1)
	return ranges

def getAllTagged(lexicon, isPublic):
	folderName = "test-private"
	if isPublic:
		folderName = "test-public"

	uncertainWords = set(lexicon.keys())

	wordTuples = getAllFileContents(folderName)
	taggedTuples = tagUncertaintyTuples(wordTuples, uncertainWords)
	return taggedTuples

def removeNewLineTuples(tuples):
	newTuples = []
	for t in tuples:
		if t[0] != "":
			newTuples.append(t)
	return newTuples

def uncertainRangeDetection(lexicon, isPublic):
	taggedTuples = getAllTagged(lexicon, isPublic)
	taggedTuples = removeNewLineTuples(taggedTuples)
	ranges = getRanges(taggedTuples)

	return ranges

def tuplesToSentences(tuples):
	taggedSentences = []
	currSentence = []
	for t in tuples:
		if t[0]=="" and len(currSentence) > 0:
			taggedSentences.append(currSentence)
			currSentence = []
		else:
			currSentence.append(t)
	return taggedSentences

#currently determining if a sentence is uncertain if it's tokens are >=25% uncertain
def isSentenceUncertain(sentence):
	thresh = THRESHOLD
	uncCount = 0.0
	for tupl in sentence:
		if len(tupl) >= 3 and "CUE" in tupl[2]:
			uncCount += 1.0
	return uncCount/float(len(sentence)) >= thresh

def indicesOfTaggedSentences(sentences):
	indices = []
	for i in range(len(sentences)):
		s = sentences[i]
		if isSentenceUncertain(s):
			indices.append(i)
	return indices

def uncertainSentenceDetection(lexicon, isPublic):
	taggedTuples = getAllTagged(lexicon, isPublic)
	taggedSentences = tuplesToSentences(taggedTuples)
	sentenceIndices = indicesOfTaggedSentences(taggedSentences)

	return sentenceIndices

def formatArray(arr):
	s = ""
	for i in range(len(arr)-1):
		s += str(arr[i]) + ' '
	s += str(arr[-1])
	return s

def writeRanges(publicRanges, privateRanges):
	with open('kaggleSubmission1.csv', 'w') as f:
		writer = csv.writer(f)
		writer.writerow(['Type', 'Spans'])
		writer.writerow(['CUE-public', formatArray(publicRanges)])
		writer.writerow(['CUE-private', formatArray(privateRanges)])

def writeSentences(publicSentences, privateSentences):
	with open('kaggleSubmission2.csv', 'w') as f:
		writer = csv.writer(f)
		writer.writerow(['Type', 'Indices'])
		writer.writerow(['SENTENCE-public', formatArray(publicSentences)])
		writer.writerow(['SENTENCE-private', formatArray(privateSentences)])

# main function
if __name__ == '__main__':
	tuples = getAllFileContents("train")
	lexicon = lexGenerator(tuples)
	publicRanges = uncertainRangeDetection(lexicon, 1)
	privateRanges = uncertainRangeDetection(lexicon, 0)

	publicSentences = uncertainSentenceDetection(lexicon, 1)
	privateSentences = uncertainSentenceDetection(lexicon, 0)

	writeRanges(publicRanges, privateRanges)
	writeSentences(publicSentences, privateSentences)
