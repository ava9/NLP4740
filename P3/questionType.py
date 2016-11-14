#!/usr/bin/env python
# http://www.nltk.org/book/ch07.html
f = open('question.txt','r')
whereCount = 0
whoCount = 0
whatCount = 0
whenCount = 0
num = 0
x = True
while x:
    text = f.readline()
    if 'Number: ' in text:
    	num = num + 1
    if 'Where' in text:
    	whereCount = whereCount + 1
    if "Where's" in text:
    	print text
    if 'Who' in text:
    	whoCount = whoCount + 1
    if "Who's" in text:
    	print text
    if 'What' in text:
    	whatCount = whatCount + 1
    if "What's" in text:
    	print text
    if 'When' in text:
    	whenCount = whenCount + 1
    if "When's" in text:
    	print text
    if not text:
    	x = False
total = whoCount + whereCount + whatCount + whenCount
print(total)
print(num)

# output is: 
#Where's Montenegro?
#Who's the lead singer of the Led Zeppelin band?
#232
#232