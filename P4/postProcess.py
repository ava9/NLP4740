#!/usr/bin/env python

import csv

cueTags = ['B', 'I', 'U' , 'L']

def backToX(resultFile):
    X = []
    with open(resultFile) as f:
        for line in f:
            line = line.strip('\n')
            if line:
                # arr is the word/token (0), pos (1), assigned tag (2)
                X.append(line.split('\t'))
            else:
                #denotes end of sentence
                X.append([""])
    return X

def getRanges(X):
    ranges = []
    inRange = False
    for i in range(len(X)):
        t = X[i]
        if t[2] in cueTags and not inRange:
            ranges.append(str(i)+"-")
            inRange = True
        elif inRange and t[2] == 'O':
            ranges[-1] += str(i-1)
            inRange = False
    if inRange:
        ranges[-1] += str(len(X)-1)
    return ranges

def removeNewLineTuples(X):
    newX = []
    for t in X:
        if t[0] != "":
            newX.append(t)
    return newX

def uncertainRangeDetection(isPublic):
    fileName = "priv"
    if isPublic:
        fileName = "pub"
    fileName += "results.txt"

    X = backToX(fileName)
    X = removeNewLineTuples(X)
    ranges = getRanges(X)

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

#currently determining if it has a tag in it
def isSentenceUncertain(sentence):
    # thresh = THRESHOLD
    # uncCount = 0.0
    for t in sentence:
        if t[2] in cueTags:
            return True
            # uncCount += 1.0
    # return uncCount/float(len(sentence)) >= thresh
    return False

def indicesOfTaggedSentences(sentences):
    indices = []
    for i in range(len(sentences)):
        s = sentences[i]
        if isSentenceUncertain(s):
            indices.append(i)
    return indices

def uncertainSentenceDetection(isPublic):
    fileName = "priv"
    if isPublic:
        fileName = "pub"
    fileName += "results.txt"

    X = backToX(fileName)
    sentences = tuplesToSentences(X)
    sentenceIndices = indicesOfTaggedSentences(sentences)

    return sentenceIndices

def formatArray(arr):
    s = ""
    for i in range(len(arr)-1):
        s += str(arr[i]) + ' '
    s += str(arr[-1])
    return s

def writeRanges(publicRanges, privateRanges):
    with open('CRFkaggleSubmission1.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['Type', 'Spans'])
        writer.writerow(['CUE-public', formatArray(publicRanges)])
        writer.writerow(['CUE-private', formatArray(privateRanges)])

def writeSentences(publicSentences, privateSentences):
    with open('CRFkaggleSubmission2.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['Type', 'Indices'])
        writer.writerow(['SENTENCE-public', formatArray(publicSentences)])
        writer.writerow(['SENTENCE-private', formatArray(privateSentences)])

if __name__ == "__main__":
    publicRanges = uncertainRangeDetection(1)
    privateRanges = uncertainRangeDetection(0)

    publicSentences = uncertainSentenceDetection(1)
    privateSentences = uncertainSentenceDetection(0)

    writeRanges(publicRanges, privateRanges)
    writeSentences(publicSentences, privateSentences)
