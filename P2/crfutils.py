"""
A miscellaneous utility for sequential labeling.
Copyright 2010,2011 Naoaki Okazaki.
"""

import optparse
import sys

import time
def apply_templates(X, templates):
    """
    Generate features for an item sequence by applying feature templates.
    A feature template consists of a tuple of (name, offset) pairs,
    where name and offset specify a field name and offset from which
    the template extracts a feature value. Generated features are stored
    in the 'F' field of each item in the sequence.

    @type   X:      list of mapping objects
    @param  X:      The item sequence.
    @type   template:   tuple of (str, int)
    @param  template:   The feature template.
    """
    totLen = len(templates)*len(X)
    i = 0
    for template in templates:
        # start = time.time()
        if isinstance(template[0], tuple):
            name = '|'.join(['%s[%d]' % (f, o) for f, o in template])
        else:
            name = '%s[%d]' % template
        for t in range(len(X)):
            values = []
            if isinstance(template[0], tuple):
                for field, offset in template:
                    p = t + offset
                    if p >= 0 and p < len(X):
                        values.append(X[p][field])
            else:
                p = t + template[1]
                if p >= 0 and p < len(X):
                    values.append(X[p][template[0]])
            if values:
                X[t]['F'].append('%s=%s' % (name, '|'.join(values)))
            i +=1
            if i % (totLen/10) == 0: 
                # print(time.time()-start)
                # start = time.time()
                print "we are at " + str(i) + " out of " + str(totLen)


def readiter(fi, names, sep=' ', isTest = 0):
    """
    Return all of the item sequences read from a file object.
    This function reads a sequence from a file object L{fi}, and
    returns the sequence as a list of mapping objects. Each line
    (item) from the file object is split by the separator character
    L{sep}. Separated values of the item are named by L{names},
    and stored in a mapping object. Every item has a field 'F' that
    is reserved for storing features.

    @type   fi:     file
    @param  fi:     The file object.
    @type   names:  tuple
    @param  names:  The list of field names.
    @type   sep:    str
    @param  sep:    The separator character.
    @rtype          list of mapping objects
    @return         All the sequences.
    """
    X = []
    print "Reading Files"
    foundEnd = 0
    prev = None
    for line in fi:
        line = line.strip('\n')
        if line:
            fields = line.split(sep)
            if len(fields) < len(names):
                raise ValueError(
                    'Too few fields (%d) for %r\n%s' % (len(fields), names, line))
            item = {'F': []}    # 'F' is reserved for features.
            for i in range(len(names)):
                item[names[i]] = fields[i]
            if foundEnd:
                item['F'].append('__BOS__')
                foundEnd = 0
            X.append(item)
        else:
            foundEnd = 1
            X[-1]['F'].append('__EOS__')
    return X

def output_features(fo, X, field=''):
    """
    Output features (and reference labels) of a sequence in CRFSuite
    format. For each item in the sequence, this function writes a
    reference label (if L{field} is a non-empty string) and features.

    @type   fo:     file
    @param  fo:     The file object.
    @type   X:      list of mapping objects
    @param  X:      The sequence.
    @type   field:  str
    @param  field:  The field name of reference labels.
    """
    for t in range(len(X)):
        if field:
            fo.write('%s' % X[t][field])
        for a in X[t]['F']:
            if isinstance(a, str):
                fo.write('\t%s' % a)
            else:
                fo.write('\t%s:%f' % (a[0], a[1]))
        fo.write('\n')
    fo.write('\n')

#method to train a model using crfsuite
def train(X, validatePerc, verbose = 1, model = None):
    """
    Train a model and output it using features and labels.
    """
    import pycrfsuite as crfsuite
    print "Training Model"
    trainer = crfsuite.Trainer(verbose=True)
    XSEQ = [x['F'] for x in X]
    YSEQ = [x['y'] for x in X]

    # For my sanity
    # print trainer.get_params()
    # for p in  trainer.params():
    #     print p + " :  " + trainer.help(p)

    i=0
    thresh = validatePerc * len(YSEQ)
    gr = 0
    for x, y in zip(XSEQ, YSEQ):
        if i > thresh:
            gr = 1
        trainer.append([x],[y],group = gr)
        i+=1

    trainer.set_params({
        'c1': 1.0,   # coefficient for L1 penalty
        'c2': 1e-3,  # coefficient for L2 penalty
        'feature.possible_transitions': True #not sure if this should be allowed
    })
    if not model:
        model = 'standardModel.model'
    trainer.train(model, holdout = 1)

def tag(X, fo, model = None, F='w pos y'):
    if not model:
        model = 'standardModel.model'
    # Create a tagger with an existing model.
    import pycrfsuite as crfsuite
    tagger = crfsuite.Tagger()
    tagger.open(model)

    XSEQ = [x['F'] for x in X]
    yseq = tagger.tag(XSEQ)
    for t in range(len(X)):
        v = X[t]
        fo.write('\t'.join([v[f] for f in F]))
        fo.write('\t%s' % yseq[t])
        if "__EOS__" in v['F']:
            fo.write('\n')
        fo.write('\n')
    fo.write('\n')

