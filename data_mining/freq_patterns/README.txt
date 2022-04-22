Files contained in this framework:

  patterns.py: This is where apriori and the association rule extractions 
               are to be implemented. DO NOT CHANGE THE FUNCTION SIGNATURES
  
  testcases.py: Provides a few test cases you can run to test your 
                implementation of lloyds and kmedoids. If you just run the 
                script it will open a (text-based) menu where you can select 
                which test case to run.
                  
  testdata.csv: Is a (randomly) generated csv file, i.e. the data has no 
                meaning. Columns x1, x2 are drawn from one of three clusters 
                (recorded in cls1), columns x3, x4 from one of two clusters 
                (recorded in cls2). The categorical attributes cat1-cat4 are 
                chosen from two different probability distributions, 
                corresponding to two clusters, recorded in cls3, and similarly
                for the five binary attributes bin1-bin5, recorded in cls4. 
                This is the same file as in lab 3.
                
Once you have the algorithms implemented, try the following:

python testcases.py 0q
python testcases.py 1q

These two test cases run Apriori on a set of words, i.e. each "itemset" is a
set of letters. The first one has a very low threshold, and therefore should 
find itemsets containing many letters. The second one uses a much higher 
threshold and will therefore return an itemset with only two letters.

python testcases.py 4q

This will run Apriori and then extract association rules using each of the 
five evaluation metrics. The returned rules should be different between the 
different metrics, and not all metrics may return association rules. 

python testcases.py 6q

This will apply Apriori and the association rule extraction to the given 
csv file. The csv file is converted to sets as follows: The numerical 
attributes are discretized into high and low (above and below 0.5), and
only included if they have a high value. The categorical attributes are 
included with their name and the value concatenated, and the binary attributes
are only included if they are true. You can refer to testcases.py (around line
82) to see how I did this, in case you want to do something similar for your 
dataset.

If all of these tests worked, explore the other test cases more, before you 
apply the algorithm(s) to your own data.