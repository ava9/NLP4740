###CS 4740 PROJECT 2 README

Installation:

1) to run part2.py you need to install CRFsuite Python module and it's dependecies.  The link for the CRFsuite Python module is posted here: https://python-crfsuite.readthedocs.io/en/latest/
2) to run hmm.py you need to install numpy and seqlearn along with seqlearn's dependencies.  The link for seqlearn is posted here: https://github.com/larsmans/seqlearn

part2.py takes in various options to train a CRF library 

This utility reads a data set from STDIN, and outputs attributes to STDOUT.
Each line of a data set must consist of field values separated by SEPARATOR
characters. The names and order of field values can be specified by -f option.
The separator character can be specified with -s option. Instead of outputting
attributes, this utility tags the input data when a model file is specified by
-t option (CRFsuite Python module must be installed).

The options for part2.py are:
   -m which Determine mode of program, which could be parse (default), train, or tag (a validation file or a test file)
   -t which tags the input using the model (requires "crfsuite" module)
   -f which specifies field names of input data [default: "%default"]
   -s which specifies the separator of columns of input data [default: "%default"]
   -T which specifies whether the input is a test file (has no labels) or not [default: "%default"]
   -o which specifies an output file. Default is sys.stdout

in UNIX:
To train and output a model (to stanardModel.model), run:
>> cat ./train/* | python part2.py -o trained.txt -m train 

To tag a test set with a trained model (default = standardModelP4.model), run:
>> cat ./test-public/* | python part2.py -o taggedPublic.txt -m tag -T 1

Then, the post processing was done with the postProcess script (just run ./postProcess.py)

in Windows:
No support.  Use cygwin or another similar tool to run the above commands.



to run hmm.py, simply use python to run the hmm.py script:

in UNIX:
>> python hmm.py

in Windows:
>> py hmm.py


The output for the phrases and sentences are in the CRFkaggleSubmission1.csv and CRFkaggleSubmission2.csv files respectively