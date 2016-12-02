In order to run the final version of project 3 (on a unix system), run:
>> ./part2.py

or a similar python command (supported by windows and unix):
Unix:
>> python part2.py
Windows:
>> py part2.py

This will output a file called part2output.txt, which can be 
run against the pattern.txt with the perl script:

Unix:
>> perl eval.pl pattern.txt part2output.txt

Note that there are a couple dependent libraries needed, please check 
part2.py to see the imported libraries

Also, there are a couple parameters tweaked which are accessed at the top of part2.py
TOPFILES represents the top number of files used in our algorithm.
INFILENAME represents the input name for the questions file to be read.
TRAINFOLDER represents the training data folder to be trained on.
OUTPUTFILENAME represents the output file name.
