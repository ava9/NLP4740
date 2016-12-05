#!/usr/bin/env python
"""Featuring super crf task completion from the best (jk)

"""
import sys
import os
import optparse

# adapted from http://english-language-skills.com/item/177-writing-skills-hedge-words.html
# wordSet = {'about','apparently','appear','around','basically','can','could','effectively','evidently','fairly','generally','hopefully','largely','likely','mainly','may','maybe','mostly','overall','perhaps','presumably','probably','quite','rather','really','seem','somewhat','supposedly'}
# twoWordSet = {'in general','kind of','quite clearly','really quite','sort of'}

# file name to make new word set over
allClusters = ['gha.1M-c10-p1.paths',
                'gha.1M-c40-p1.paths',
                'gha.1M-c320-p1.paths',
                'gha.1M-c1280-p1.paths',
                'gha.1M-c10240-p1.paths']
clusterFileName = allClusters[4]
clusterFolder = 'wikiPresetClusters'

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

templates = [
    # (('w', -2)),
    # (('w', -1)),
    (('w',  0)),
    # (('w',  1)),
    # (('w',  2)),
    # (('w', -2), ('w', -1)),
    (('w', -1), ('w',  0)),
    (('w',  0), ('w',  1)),
    # (('w',  1), ('w',  2)),
    # (('pos', -2)),
    # (('pos', -1)),
    (('pos',  0)),
    # (('pos',  1)),
    # (('pos',  2)),
    # (('pos', -2), ('pos', -1)),
    (('pos', -1), ('pos',  0)),
    (('pos',  0), ('pos',  1)),
    # (('pos',  1), ('pos',  2)),
    # (('pos',  1), ('w',  1)),
    # (('pos',  0), ('w',  0)),
    # (('pos', -1), ('w', -1)),
    (('inCluster', 0))
    ]
# (0.676623, 0.364579, 0.436437): 45, 49, 50, 54, 58, 59
# (0.678949, 0.366530, 0.439435): 45, 49, 50, 54, 58, 59, 64 [0]
# (0.677460, 0.365555, 0.438083): 45, 49, 50, 54, 58, 59, 64 [1]
# (0.677460, 0.365555, 0.438083): 45, 49, 50, 54, 58, 59, 64 [2]
# (0.680385, 0.367506, 0.440777): 45, 49, 50, 54, 58, 59, 64 [3]
# (0.682937, 0.370221, 0.444084): 45, 49, 50, 54, 58, 59, 64 [4]

import crfutils

def readFile(fileName):
    if os.path.exists(fileName):
        with open(fileName) as f:
            return f.read()
    else:
        print 'file not found: ' + fileName

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
    
    # read file contents
    uncCluster = set(readFile(clusterFolder + '/' + clusterFileName))
    # Adding feature for in predefined cluster
    for i in range(len(X)):
        X[i]['inCluster'] = str(X[i]['w'] in uncCluster)

    # Apply the feature templates.
    print "Applying Templates"
    crfutils.apply_templates(X, templates)

    # Append BOS and EOS features.
    if X:
        X[0]['F'].append('__BOS__')
        X[-1]['F'].append('__EOS__')

    return X


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
    X = feature_extractor(X)
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