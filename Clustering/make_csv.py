import random
import math
import sys

# Each center consists of two coordinates, and for each coordinate we have the 
# base value and range. Values are randomly generated between "base value" and "base value + range"
clusters1 = [((0.25,0.75), (0.4,0.6)),
             ((0.05,0.4), (0.1,0.8)),
             ((0.1,0.35), (0.55,0.45))]
             
clusters2 = [((0.3,0.7), (0.05,0.7)),
             ((0.1,0.6), (0.4,0.6))]
   
# Each cluster uses different weights to sample the possible outcomes 
# Each outcome is chosen with the given probability
clusters3 = [(0.7,0.2,0.1), (0.05,0.15,0.8)]

clusters4 = [(0.9, 0.1), (0.15,0.85)]

REPEATS = 4

def sample(centers):
    result = []
    for c in centers:
        (where,rang) = c
        result.append("%.2f"%(where + sum([random.random()*rang/REPEATS for i in range(REPEATS)])))
    return result
    
def sample_cat(p, n, outcomes):
    result = []
    for i in range(n):
        result.extend(random.choices(outcomes, weights=p))
    return result

def main(fname):
    f = open(fname, "w")
    print("id,x1,x2,x3,x4,cat1,cat2,cat3,cat4,bin1,bin2,bin3,bin4,bin5,cls1,cls2,cls3,cls4", file=f)
    for i in range(300):
        # choose cluster centers at random
        cls1 = random.randint(0,2)
        cls2 = random.randint(0,1)
        cls3 = random.randint(0,1)
        cls4 = random.randint(0,1)
        row = [str(i)]
        # Sample data points depending on the selected clusters
        row.extend(sample(clusters1[cls1]))
        row.extend(sample(clusters2[cls2]))
        row.extend(sample_cat(clusters3[cls3], 4, ["high", "medium", "low"]))
        row.extend(sample_cat(clusters4[cls4], 5, ["true", "false"]))
        row.extend(str(cls1))
        row.extend(str(cls2))
        row.extend(str(cls3))
        row.extend(str(cls4))
        print(",".join(row), file=f)
        
    f.close()
    
if __name__ == "__main__":
    main(sys.argv[1])