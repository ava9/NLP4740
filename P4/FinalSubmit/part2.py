#!/usr/bin/env python
"""Featuring super crf task completion from the best (jk)

"""
import sys
import optparse

# adapted from http://english-language-skills.com/item/177-writing-skills-hedge-words.html
wordSet = {'about','apparently','appear','around','basically','can','could','effectively','evidently','fairly','generally','hopefully','largely','likely','mainly','may','maybe','mostly','overall','perhaps','presumably','probably','quite','rather','really','seem','somewhat','supposedly'}
twoWordSet = {'in general','kind of','quite clearly','really quite','sort of'}

separator = '\t'
fields = 'w pos y'

def toBIOLU(v, p = {'y': 1}, prevCNum = -1):
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

templates = [
    (('w', -2)),
    (('w', -1)),
    (('w',  0)),
    (('w',  1)),
    (('w',  2)),
    (('w', -1), ('w',  0)),
    (('w',  0), ('w',  1)),
    (('pos', -2)),
    (('pos', -1)),
    (('pos',  0)),
    (('pos',  1)),
    (('pos',  2)),
    (('pos', -2), ('pos', -1)),
    (('pos', -1), ('pos',  0)),
    (('pos',  0), ('pos',  1)),
    (('pos',  1), ('pos',  2)),
    (('pos',  1), ('w',  1)),
    (('pos', -1), ('w', -1)),
    (('inDict', 0))
    ]

import crfutils

def feature_extractor(X):
    # Converting the tags to BILOU
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
    
    # Adding feature for in predefined dict
    for i in range(len(X)):
        X[i]['inDict'] = X[i]['w'] in wordSet 
        X[i]['inDict'] = X[i]['inDict'] or (i > 0 and X[i-1]['w'] + " " + X[i]['w'] in twoWordSet)
        X[i]['inDict'] = X[i]['inDict'] or (i < len(X)-1 and X[i]['w'] + " " + X[i+1]['w'] in twoWordSet)
        X[i]['inDict'] = str(X[i]['inDict'])

    # Apply the feature templates.
    print "Applying Templates"
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
        '-m', dest = 'mode', default='parse',
        help='Determine mode of program, which could be parse (default), train, or tag (a validation file or a test file)')
    parser.add_option(
        '-t', dest='model',
        help='tag the input using the model (requires "crfsuite" module)')
    parser.add_option(
        '-f', dest='fields', default=fields,
        help='specify field names of input data [default: "%default"]')
    parser.add_option(
        '-s', dest='separator', default=sep,
        help='specify the separator of columns of input data [default: "%default"]')
    parser.add_option(
        '-T', dest='test', default=0,
        help='specify whether the input is a test file (has no labels) or not [default: "%default"]')
    parser.add_option(
        '-o', dest='fo', default= None,
        help = 'specify an output file. Default is sys.stdout')
    parser.add_option(
        '-a', dest='algo', default = 'lbfgs',
        help = 'specify the algo to train on')
    (options, args) = parser.parse_args()

    # The fields of input: ('w', 'pos', 'y') by default.
    F = options.fields.split(' ')
    if options.test and 'y' in F:
        F.remove('y')

    if options.fo:
        fo = open(options.fo,'w')
    if options.algo:
        algo = options.algo

    #process input
    X = crfutils.readiter(fi, F, options.separator)
    feature_extractor(X)
    if options.mode == "parse":
        crfutils.output_features(fo, X, 'y')
    elif options.mode == "train":
        crfutils.train(X, .8, verbose = 0, model = options.model, algo = algo)
    elif options.mode == "tag":
        crfutils.tag(X, fo, model = options.model, F = F)
    else:
        raise ValueError("Unexpected Mode")

if __name__ == '__main__':
    main(fields=fields, sep=separator)