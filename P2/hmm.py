import sys
import glob
#from hmmlearn.hmm import GaussianHMM
#from hmmlearn.hmm import MultinomialHMM
import numpy as np
from seqlearn.hmm import MultinomialHMM


def toIntArr(strarr):
	uniqueW, locs = np.unique(strarr, return_inverse = True)
	return (locs.reshape(-1,1) == np.arange(len(uniqueW))).astype(int)

def createFeatures(path, isTrain):
	files = glob.glob(path)   
	featureArray = []
	lengths = []
	currLen = 0
	for name in files:
		with open(name) as f:
			fd = f.read()
			for line in fd:
				print (fd)
				print '.....'
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
			t = featureArray[i][2]
			if t[0] == 'C':
				if t[-1] == currCue:
					tempTags.append('I')
				else:
					tempTags.append('B')
					currCue = t[-1]
			else:
				currCue = -1
				if len(tempTags) != 0:
					if tempTags[-1] == 'B': 
						tempTags[-1] = 'U'
					elif tempTags[-1] == 'I': 
						tempTags [-1] = 'L'
				tempTags.append('O')

			if tempTags[-1] == 'B': 
				tempTags[-1] = 'U'
			elif tempTags[-1] == 'I': 
				tempTags[-1] = 'L'
		#make better stringtoint
		tags = np.array(toIntArr(tempTags))

		# features.append(taggggggs)
	words = [row[0] for row in featureArray]
	pos = [row[1] for row in featureArray]
	words = toIntArr(words)
	pos = toIntArr(pos)
	featureArray = zip(words, pos)
	print "EXTRACTED FEATURES"
	return (np.array(featureArray), tags, lengths)


def read(trainPath='train/*.txt', testPath='test-public/*txt'):  
	(X, y, lengths1) = createFeatures(trainPath, 1)
	#model = GaussianHMM(n_components=2, covariance_type='spherical', params=set(X.ravel())).fit(X)
	#model = MultinomialHMM(n_components=3).fit(X)
	#fo = open("hmmModel.model",'w')
	#o.write('%s' % model)
	model = MultinomialHMM()
	#print("X is:" str(X))
	#print("Y is" + str(y))
	#print("lengths is: " + str(lengths1))
	print "TRAINING MODEL"
	# model.fit(X, y, lengths1)
	# (X2, y2,lenghts2) = createFeatures(testPath, 0)

	# test = model.predict(X2, lengths2)


	# print(str(test))
	#test = model.predict(Y)
	#print(test)
	#print(X.ravel())

read()

