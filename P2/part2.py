#!/usr/bin/env python
"""Featuring spaghetti

"""
import sys

separator = '\t'

def toBIOLU(v, p = {'y':-1}, prevCNum = -1):
	if v['y'] == "_":
		v['y'] = "O"
		if p['y'] == 'I':
			p['y'] = 'L'
		elif p['y'] == 'B':
			p['y'] = 'U'
	#This is a cue, must be BILU
	elif v['y'][0] == 'C':
		currCNum = v['y'][-1]
		if prevCNum == currCNum:
			v['y'] = 'I'
		else:
			v['y'] = 'B'
		return currCNum
	return -1
U = ['w', 'pos']
B = ['w', 'pos']

templates = (
    (('w', -2), ),
    (('w', -1), ),
    (('w',  0), ),
    (('w',  1), ),
    (('w',  2), ),
    (('w', -2), ('w',  -1)),
    (('w', -1), ('w',  0)),
    (('w',  0), ('w',  1)),
    (('w',  1), ('w',  2)),
    (('pos', -2), ),
    (('pos', -1), ),
    (('pos',  0), ),
    (('pos',  1), ),
    (('pos',  2), ),
    (('pos', -2), ('pos', -1)),
    (('pos', -1), ('pos',  0)),
    (('pos',  0), ('pos',  1)),
    (('pos',  1), ('pos',  2)),
    )

import crfutils

def feature_extractor(X):
    if 'y' in X[0]:
        first = 1
        for x in X:
            if first:
                prevCNum = toBIOLU(x)
                first = 0
            else:
                prevCNum = toBIOLU(x, p, prevCNum)
        p = x

        if p['y'] == 'I':
            p['y'] = 'L'
        elif p['y'] == 'B':
            p['y'] = 'U'
	

    # Apply the feature templates.
	crfutils.apply_templates(X, templates)

    # Append BOS and EOS features.
	if X:
		X[0]['F'].append('__BOS__')
		X[-1]['F'].append('__EOS__')

if __name__ == '__main__':
    isTestFile = sys.argv[1];
    fields = ''
    if isTestFile == '1':
        fields = 'w pos'
    else:
        fields = 'w pos y'
	crfutils.main(feature_extractor, fields=fields, sep=separator)