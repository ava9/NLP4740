#!/usr/local/bin/perl
$#ARGV==1 || die "Usage: eval.pl patterns submission\n";
$patterns = $ARGV[0];
$submission = $ARGV[1];

# mark the questions that have been thrown out of the evaluation
@thrown_out = ();
foreach $q (@thrown_out) {
    $gone{$q} = 1;
}


if ( (! -e $patterns) || (! open PATTERNS, "<$patterns") ) {
    die "Can't find/open patterns file `$patterns': $!\n";
}
while ($line = <PATTERNS>) {
    chomp $line;
    ($qid, $pattern) = split " ", $line, 2;
	#printf "the length of the pattern %s,%d\n", substr($pattern,0,(length($pattern)-1)), length($pattern);
	$pattern=substr($pattern,0,(length($pattern)-1));
    push @{$patterns[$qid]}, $pattern;
}
close PATTERNS || die "can't close pattern file: $!\n";

# process submission file in sorted order
if ( (! -e $submission) ||
     (! open INPUT, "$submission")){   #, "sort +0 -1n +3 -4n $submission |") ) {
    die "Can't find/open/sort submission file `$submission': $!\n";
}
$oldq = -1;
$sum = 0;
$num_notfound = 0;
$num_qs = 0;
while ($line = <INPUT>) {
    chomp $line;
    ($qid, $docid, $response) =
		split " ", $line, 3;
    next if ($gone{$qid});
    #printf "%d-%d.Working on %d-%s-%s\n", $rank, $answer_rank, $qid, $docid, $response;
    if ($qid != $oldq) {
	# print oldq's score and add to running sum for average
	# re-initialize for current qid
	if ($oldq != -1) { # i.e., not very first query
	    if ($answer_rank != 0) { # had a correct answer
		$recip = 1 / $answer_rank;
	        printf "Question %3d: Correct answer found at rank %d (%.2f).\n",
			$oldq, $answer_rank, $recip;
		$sum += $recip;
	    }
	    else { 
	        printf "Question %3d: No correct answer found. \n", $oldq;
		$num_notfound++;
	    }
	}
	$rank = 0;
	$answer_rank = 0;
	$num_qs++;
	$oldq = $qid;
    }

    $rank++;    # make sure ranks are 1-5, not 0-4
    if (0 == $answer_rank) { # if still looking for a correct answer
        foreach $p (@{$patterns[$qid]}) {
		printf "the pattern is (%s)\n", $p;
		printf "the response is (%s)\n", $response;
		printf "lenght1 %d\n",length($p);
		printf "lenght2 %d\n",length($response);
		#$response=$p;
	    #if ($p =~ /(?:\W|^)$response(?:\W|$)/i) 
	    if ($response =~ /(?:\W|^)$p(?:\W|$)/i) {
	    #if ($response =~ m/$p/) {
		printf "get into the condition\n";
		$answer_rank = $rank;
		last;
	    }
	}
    }
}
if ($qid != 0) { # i.e., submission file not empty
    if ($answer_rank != 0) { # last question had a correct answer
	$recip = 1 / $answer_rank;
        printf "Question %3d: Correct answer found at rank %d (%.2f).\n",
		$qid, $answer_rank, $recip;
	$sum += $recip;
    }
    else { 
        printf "Question %3d: No correct answer found. \n", $oldq;
		$num_notfound++;
    }
}

$ave = $sum / $num_qs;
printf "\nMean reciprocal rank over %d questions is %.3f\n", $num_qs, $ave;
print "$num_notfound questions had no answers found in top 5 responses.\n";


