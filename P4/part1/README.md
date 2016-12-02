In order to run this baseline (on a unix system), run:
>> ./baseline.py

or a similar python command (supported by windows and unix):
Unix:
>> python baseline.py
Windows:
>> py baseline.py

This will output a file called baselineOutput.txt, which can be 
run against the pattern.txt with the perl script:

Unix:
>> perl eval.pl pattern.txt baselineOutput.txt