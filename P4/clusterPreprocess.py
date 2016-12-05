#!/usr/bin/env python
# Preprocess any cluster files to only contain one cluster of uncertain words given a preseeded set

import os

# from website: http://english-language-skills.com/item/177-writing-skills-hedge-words.html
# preSet = {'about','apparently','appear','around','basically','can','could','effectively','evidently','fairly','generally','hopefully','largely','likely','mainly','may','maybe','mostly','overall','perhaps','presumably','probably','quite','rather','really','seem','somewhat','supposedly'}
# from paper in wikipedia set
# preSet = {'probable', 'likely', 'possible', 'unsure', 'often', 'possibly', 'allegedly', 'apparently', 'perhaps', 'widely', 'traditionally', 'generally', 'broadly-accepted', 'widespread', 'global', 'superior', 'excellent', 'immensely', 'legendary', 'best', 'clearly', 'obviously', 'arguably', 'may', 'might', 'would', 'should', 'suggest', 'question', 'presume', 'suspect', 'indicate', 'suppose', 'seem', 'appear', 'favor', 'certain', 'numerous', 'many', 'most', 'some', 'much', 'everyone', 'few', 'various', 'of', 'speculation', 'proposal', 'consideration'}
# from paper in biology set
preSet = {'may', 'might', 'can', 'would', 'should', 'could', 'suggest', 'question', 'presume', 'suspect', 'indicate', 'suppose', 'seem', 'appear', 'favor', 'probable', 'likely', 'possible', 'unsure'}

inPath = './clusterPaths/'
outPath = './biologyPresetClusters/'


def readFile(fileName):
	if os.path.exists(fileName):
		with open(fileName) as f:
			content = f.readlines()
			f.close()
			return content
	raise Exception(fileName + ' not found')

def clustererer(content):
	currCluster = 'INITIAL FAKE CLUSTER'
	currSet = set()
	totalSet = set()
	totalSet.update(preSet)
	for line in content:
		line = line.split('\t')
		if len(line) < 3:
			raise Exception(str(line) + '\n Invalid line detected')
		lineCluster = line[0]
		lineToken = line[1]
		if lineCluster == currCluster:
			currSet.add(lineToken)
		else:
			if totalSet & currSet:
				totalSet.update(currSet)
			currCluster = lineCluster
			currSet = {lineToken}
	if totalSet & currSet:
		totalSet.update(currSet)
	return totalSet

def main():
	allClusters = os.listdir(inPath)
	if ".DS_Store" in allClusters:
		allClusters.remove(".DS_Store")
	if "README" in allClusters:
		allClusters.remove("README")

	if not os.path.exists(outPath):
		os.makedirs(outPath)

	fileName = allClusters[0]
	for fileName in allClusters:
		print fileName +' is being processed'
		content = readFile(inPath+fileName)

		totalSet = clustererer(content)

		fOut = open(outPath+fileName, 'w')

		for token in list(totalSet):
			fOut.write("%s\n" % token)

		fOut.close()

if __name__ == '__main__':
	main()