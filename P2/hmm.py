import sys
import glob
from hmmlearn.hmm import GaussianHMM
from hmmlearn.hmm import MultinomialHMM
import numpy as np
from seqlearn.perceptron import StructuredPerceptron


def stringToInt(string):
	return int(''.join(str(ord(c)) for c in string))

def createFeatures(path, isTrain):
	files = glob.glob(path)   
	featureArray = []
	for name in files:
		try:
			with open(name) as f:
				for line in f:
					line = line.strip('\n')
					if line:
						fields = line.split("\t")
						if (len(fields) > len(featureArray)):
							for i in range(0, len(fields)):
								featureArray.append([])
						else:
							pass
						for i in range(0, len(featureArray)):
							featureArray[i].append(fields[i])
					else:
						pass
		except IOError as exc:
			if exc.errno != errno.EISDIR: 
				raise
			else:
				pass

	features = []
	words = np.array([stringToInt(l[0]) for l in featureArray])
	features.append(words)
	pos = np.array([stringToInt(l[1]) for l in featureArray])
	features.append(pos)
	tags = np.array([stringToInt(l[2]) for l in featureArray]) #need to change this to BILOU tags
	tags = []
	currCue = -1
	taggggggs = np.array([])
	if isTrain:
		for i in range(len(featureArray)):
			t = featureArray[i][2]
			if t[0] == 'C':
				if t[-1] == currCue:
					tags.append('I')
				else:
					tags.append('B')
					currCue = t[-1]
			else:
				currCue = -1
				if len(tags) != 0:
					if tags[-1] == 'B': 
						tags[-1] = 'U'
					elif tags[-1] == 'I': 
						tags [-1] = 'L'
				tags.append('O')

			if tags[-1] == 'B': 
				tags[-1] = 'U'
			elif tags[-1] == 'I': 
				tags[-1] = 'L'

		taggggggs = np.array([stringToInt(tags[l])] for l in tags)
		# features.append(taggggggs)
	return (features, taggggggs)


def read(trainPath='train/*.txt', testPath='test-public/*txt'):  
	(X, y) = createFeatures(trainPath, 1)
	#model = GaussianHMM(n_components=2, covariance_type='spherical', params=set(X.ravel())).fit(X)
	#model = MultinomialHMM(n_components=3).fit(X)
	#fo = open("hmmModel.model",'w')
	#o.write('%s' % model)
	model = StructuredPerceptron()
	model.fit(X, y, [4])
	(X2, y2) = createFeatures(testPath, 0)

	test = model.predict(X2, [4])


	print(str(test))
	#test = model.predict(Y)
	#print(test)
	#print(X.ravel())

read()

