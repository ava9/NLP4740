import sys, os
import numpy as np
from seqlearn.hmm import MultinomialHMM

tagArr = {'B': 0, 'I': 1, 'L': 2, 'O': 3, 'U': 4}
revTagArr = ['B', 'I', 'L', 'O', 'U']
def tagsToIntArr(arr):
	# return [tagArr[t] for t in arr]
	return arr != 'O'

def myIterHash(arr):
	d = dict()
	newArr = []
	nextNew = 0
	for i in range(len(arr)):
		ent = arr[i]
		if ent in d:
			newArr.append(d[ent])
		else:
			d[ent]=nextNew
			newArr.append(nextNew)
			nextNew += 1
	return newArr

def createFeatures(path, isTrain):
	files = os.listdir('./' + path + '/')
	for f in files:
		if f[0] == '.':
			files.remove(f)
	if len(files) == 0:
		raise ValueError('Wrong Path')
	featureArray = []
	lengths = []
	currLen = 0

	for name in files:
		with open('./' + path + '/' + name) as f:
			fd = f.readlines()
			for line in fd:
				line = line.strip('\n')
				if line and len(line) > 0:
					fields = line.split('\t')
					featureArray.append(fields)
					currLen += 1
				else:
					if currLen > 0:
						lengths.append(currLen)
						currLen = 0
			if currLen > 0:
				lengths.append(currLen)
				currLen = 0


	tags = np.array([])

	tempTags = []
	currCue = -1

	if isTrain:
		for i in range(len(featureArray)):
			# print len(featureArray[i])
			# if len(featureArray[i]) == 1: print featureArray[i]
			t = featureArray[i][2]
			# print t[-1]
			if t == '_':
				currCue = -1
				if len(tempTags) != 0:
					if tempTags[-1] == 'B': 
						tempTags[-1] = 'U'
					elif tempTags[-1] == 'I': 
						tempTags [-1] = 'L'
				tempTags.append('O')
			else:
				if t[-1] == currCue:
					tempTags.append('I')
				else:
					if tempTags[-1] == 'B': 
						tempTags[-1] = 'U'
					elif tempTags[-1] == 'I': 
						tempTags [-1] = 'L'
					tempTags.append('B')
					currCue = t[-1]

		if tempTags[-1] == 'B': 
			tempTags[-1] = 'U'
		elif tempTags[-1] == 'I': 
			tempTags[-1] = 'L'

		tags = np.array(tagsToIntArr(tempTags))

	# if isTrain == 0:
		# print len(featureArray)

	words = [row[0] for row in featureArray]
	pos = [row[1] for row in featureArray]
	words = myIterHash(words)
	# pos = myIterHash(pos)
	# featureArray = zip(words, pos)
	featureArray = [[word] for word in words]
	return (np.array(featureArray), tags, lengths)


def read(trainPath='train', testPath='test-public'):  
	(X, y, lengths1) = createFeatures(trainPath, 1)
	# print([revTagArr[tag] for tag in y])
	print y
	model = MultinomialHMM(decode = "bestfirst")
	model.fit(X, y, lengths1)
	# model.fit(X,y,[len(X)])
	(X2, y2,lengths2) = createFeatures(testPath, 0)

	# print len(X)
	# print sum(lengths2)
	# test = model.predict(X2, lengths2)
	# print [t for t in test]

	confirm = model.predict(X)

	# test = [revTagArr[tag] for tag in confirm]
	# test = [revTagArr[tag] for tag in test]
	print model.score(X, y, lengths1)
	# print([revTagArr[tag] for tag in ])
	#test = model.predict(Y)

read()

