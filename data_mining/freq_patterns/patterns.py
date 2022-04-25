import math
from itertools import chain, combinations

from numpy import fromregex

def apriori(itemsets, threshold, constraints=None, exclude=None):
    curr_itemset = set()
    for itemset in itemsets:
        for item in itemset:
            temp = set()
            temp.add(item)
            
            if exclude != None and item not in exclude or exclude == None:
                curr_itemset.add(frozenset(temp)) # init itemset with k = 1
    
    k = 2
    prev_itemset, prev_supports = None, None
    while True:
        curr_itemset, supports = prune(itemsets, threshold, curr_itemset)
        
        if(len(curr_itemset) == 0):
            break
        prev_itemset, prev_supports = curr_itemset, supports
        curr_itemset = join(prev_itemset, k, constraints)
        print(k, len(prev_itemset), len(curr_itemset))
        k += 1
    
    
    # Should return a list of pairs, where each pair consists of the frequent itemset and its support 
    # e.g. [(set(items), 0.7), (set(otheritems), 0.74), ...]
    return list(zip(prev_itemset, prev_supports))


def join(prev_lk, k, constraints):
    lk = set()
    prev_lk = list(prev_lk)
    
    for i, item in enumerate(prev_lk):
        for pot in prev_lk[i+1:]:
            if len(item.intersection(pot)) >= k - 2:
                union = item.union(pot)
                if constraints != None:
                    count = 0
                    for c in constraints:
                        if c in union:
                            count += 1
                    if count == 1:
                        lk.add(union)
                else:
                    lk.add(union)
    return lk

def prune(itemsets, threshold, pot_sets):
    lk = set()
    supports = []
    for s in pot_sets:
        support = support_count(itemsets, s) / len(itemsets)
        if support >= threshold:
            lk.add(s)
            supports.append(support)
    return lk, supports
    
def association_rules(itemsets, frequent_itemsets, metric, metric_threshold, antecedents=None, consequents=None):
    rules = []

    for itemset in frequent_itemsets:
        sets = powerset(itemset[0])
        for A in sets:
            A = frozenset(A)
            B = itemset[0].difference(A)
            
            if (len(A) == 0 or len(B) == 0):
                continue
            
            if antecedents != None and not check_if_contains(A, antecedents):
                continue
            
            if consequents != None and not check_if_contains(B, consequents):
                continue
                        
            
            metric_val = None
            if metric.lower() == "lift":
                metric_val = calc_lift_metric(itemsets, A, B)
            elif metric.lower() == "all":
                metric_val = calc_all_metric(itemsets, A, B)
            elif metric.lower() == "max":
                metric_val = calc_max_metric(itemsets, A, B)
            elif metric.lower() == "kulczynski":
                metric_val = calc_kulczynski_metric(itemsets, A, B)
            elif metric.lower() == "cosine":
                metric_val = calc_cosine_metric(itemsets, A, B)
                        
            if metric_val >= metric_threshold:
                rules.append((A, B, metric_val))
                
    # Should return a list of triples: condition, effect, metric value 
    # Each entry (c,e,m) represents a rule c => e, with the matric value m
    # Rules should only be included if m is greater than the given threshold.    
    # e.g. [(set(condition),set(effect),0.45), ...]
    return rules

def powerset(set):
    s = list(set)
    return chain.from_iterable(combinations(s, r) for r in range(1, len(s)+1))

def check_if_contains(items, constraint):
    for i in items:
        if i not in constraint:
            return False
    return True

def support_count(itemsets, item):
    count = 0
    for itemset in itemsets:
        if item.issubset(itemset):
            count += 1
    return count

def calc_lift_metric(itemsets, A, B):
    conf = support_count(itemsets, A.union(B)) / support_count(itemsets, A)
    return conf / (support_count(itemsets, B) / len(itemsets))

def calc_conditional_prob(itemsets, A, B):
    return support_count(itemsets, A.union(B)) / support_count(itemsets, B)

def calc_all_metric(itemsets, A, B):
    return min(calc_conditional_prob(itemsets, A, B), calc_conditional_prob(itemsets, B, A))

def calc_max_metric(itemsets, A, B):
    return max(calc_conditional_prob(itemsets, A, B), calc_conditional_prob(itemsets, B, A))

def calc_kulczynski_metric(itemsets, A, B):
    return (calc_conditional_prob(itemsets, A, B) + calc_conditional_prob(itemsets, B, A)) / 2

def calc_cosine_metric(itemsets, A, B):
    return math.sqrt(calc_conditional_prob(itemsets, A, B) * calc_conditional_prob(itemsets, B, A))