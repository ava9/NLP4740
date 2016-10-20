#!/usr/bin/env python
"""Featuring spaghetti

"""
import sys

separator = '\t'
fields = 'w pos y'

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


#The main run for our training and testing
def main(fields='w pos y', sep=' ', test = False):
    fi = sys.stdin
    fo = sys.stdout

    # Parse the command-line arguments.
    parser = optparse.OptionParser(usage="""usage: %prog [options]
This utility reads a data set from STDIN, and outputs attributes to STDOUT.
Each line of a data set must consist of field values separated by SEPARATOR
characters. The names and order of field values can be specified by -f option.
The separator character can be specified with -s option. Instead of outputting
attributes, this utility tags the input data when a model file is specified by
-t option (CRFsuite Python module must be installed)."""
        )
    parser.add_option(
        '-t', dest='model',
        help='tag the input using the model (requires "crfsuite" module)'
        )
    parser.add_option(
        '-f', dest='fields', default=fields,
        help='specify field names of input data [default: "%default"]'
        )
    parser.add_option(
        '-s', dest='separator', default=sep,
        help='specify the separator of columns of input data [default: "%default"]'
        )
    parser.add_option(
        '--test', dest='test', default=0,
        help='specify whether the input is a test file (has no labels) or not [default: "%default"]'
        )
    parser.add_option(
    	'--train', dest= 'train', default=0,
		help='specify whether a model is to be created and trained [default: "%default"]'
    	)
    (options, args) = parser.parse_args()

    # The fields of input: ('w', 'pos', 'y') by default.
    F = options.fields.split(' ')
    if options.test and 'y' in F:
    	F.remove('y')

    if not options.model:
    	# This will generate a crfsuite compatible text file
        for X in crfutils.readiter(fi, F, options.separator):
            feature_extractor(X)
            crfutils.output_features(fo, X, 'y')

    else:
        # Create a tagger with an existing model.
        import pycrfsuite as crfsuite
        tagger = crfsuite.Tagger()
        tagger.open(options.model)

        # For each sequence from STDIN.
        for X in readiter(fi, F, options.separator):
            # Obtain features.
            feature_extractor(X)
            xseq = crfutils.to_crfsuite(X)
            yseq = tagger.tag(xseq)
            for t in range(len(X)):
                v = X[t]
                fo.write('\t'.join([v[f] for f in F]))
                fo.write('\t%s\n' % yseq[t])
            fo.write('\n')

if __name__ == '__main__':
	main(fields=fields, sep=separator)