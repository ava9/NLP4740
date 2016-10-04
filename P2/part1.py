# Project 2 Part 1
import os

def preProcess(content):
	outArr = []
	lines = content.split('\n')
	for line in lines:
		words = line.split('\t')
		outArr.append(words)
	return outArr

def getFileContents(folder, fileName):
	fileName = folder + "/" + fileName
	if os.path.exists(fileName):
		with open(fileName) as f:
			content = f.read()
			return preProcess(content)

def getAllFileContents(folder):
	allWords = []
	docs = os.listdir(folder)
	for fileName in docs:
		fileWords = getFileContents(folder, fileName)
		allWords += fileWords
	return allWords

# build lexicons
def lexGenerator (wordList):
	# define variables
	uncertainList = dict()
	lex = dict()
	lexArray = []

	# update uncertainList
	for word in wordList:
		if (len(word) != 3):
			pass
		else:
			if ("CUE" not in word[2]):
				pass
			else:
				curWord = word[0]
				uncertainList[curWord] = uncertainList.get(curWord, 0)
				uncertainList[curWord] = uncertainList[curWord] + 1

	# sort list
	sortedList = sorted(uncertainList, key=uncertainList.get)
	sortedList.reverse()

	# initialize variables
	count = 0
	length = 100

	#update lexicon
	for word in sortedList:
		if (count >= length):
			break
		else:
			lex[word] = uncertainList[word]
			lexArray.append(word)
			count = count + 1

	# return lexicon and lexicon array
	return (lex, lexArray)
# end lexGenerator

# main function
if __name__ == '__main__':
	wordList = getAllFileContents("train")
	lex, lexArray = lexGenerator(wordList)
else:
	pass
