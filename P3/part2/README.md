In order to run the final version of project 3 (on a unix system), run:
>> ./part2.py

or a similar python command (supported by windows and unix):
Unix:
>> python part2.py
Windows:
>> py part2.py

This will output a file called baselineOutput.txt, which can be 
run against the pattern.txt with the perl script:

Unix:
>> perl eval.pl pattern.txt baselineOutput.txt

Note that there are a couple dependent libraries needed, please check 
part2.py to see the imported libraries