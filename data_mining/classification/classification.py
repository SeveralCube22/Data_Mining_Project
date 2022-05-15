import numpy
import math


# These are suggested helper functions
# You can structure your code differently, but if you have
# trouble getting started, this might be a good starting point

# Create the decision tree recursively
def make_node(previous_ys, xs, ys, columns, curr_depth, max_depth=None):
    # WARNING: lists are passed by reference in python
    # If you are planning to remove items, it's better 
    # to create a copy first
    columns = columns[:]
    # First, check the three termination criteria:
    
    if len(xs) == 0 and len(ys) == 0:
        return {"type": "class", "class": majority(previous_ys)}
    
    if same(ys):
        return {"type": "class", "class": ys[0]}

    if len(columns) == 0:
        return {"type": "class", "class": majority(ys)}
    
    if max_depth != None and curr_depth + 1 >= max_depth:
        if len(ys) == 0: mys = majority(previous_ys)
        else: mys = majority(ys)
        return {"type": "class", "class": mys}
    
    # Otherwise:
    # Compute the entropy of the current ys 
    # For each column:
    #     Perform a split on the values in that column 
    #     Calculate the entropy of each of the pieces
    #     Compute the overall entropy as the weighted sum 
    #     The gain of the column is the difference of the entropy before
    #        the split, and this new overall entropy 
    # Select the column with the highest gain, then:
    # Split the data along the column values and recursively call 
    #    make_node for each piece 
    # Create a split-node that splits on this column, and has the result 
    #    of the recursive calls as children.
    
    # Note: This is a placeholder return value
    
    current_entropy = entropy(ys)
    max_gain = -1
    max_split = None
    remove_i = None 
    remove_col = None 
    
    for i, c in enumerate(columns):
        split = split_dataset(xs, ys, c)
        entropies = []
        for piece in split:
            s_ys = split[piece][1] # get labels from split
            entropies.append(len(s_ys) / len(ys) * entropy(s_ys))
        
        gain = current_entropy - sum(entropies)
        if gain > max_gain:
            max_gain = gain
            max_split = split
            remove_i = i
    
    remove_col = columns[remove_i]
    del columns[remove_i]
    
    children = {}
    for piece in max_split:
        children[piece] = make_node(ys, max_split[piece][0], max_split[piece][1], columns, curr_depth + 1, max_depth=max_depth)
          
    return {"type": "split", "split": remove_col, "majority": majority(ys), "children": children}


def split_dataset(xs, ys, c):
    split = {}
    for i, row in enumerate(xs):
        if row[c] in split:
            split[row[c]][0].append(row)
            split[row[c]][1].append(ys[i])
        else:
            split[row[c]] = [row], [ys[i]]
    return split
    
# Determine if all values in a list are the same 
# Useful for the second basecase above
def same(values):
    if not values: return True
    else: return all(e == values[0] for e in values)
  
# Determine how often each value shows up 
# in a list; this is useful for the entropy
# but also to determine which values is the 
# most common
def counts(values):
    val_counts = {v: 0 for v in values}
    for v in values:
        val_counts[v] = val_counts[v] + 1
    return val_counts

# Return the most common value from a list 
# Useful for base cases 1 and 3 above.
def majority(values):
    val_counts = counts(values)
    max = -1
    val = None
    for v in val_counts:
        if val_counts[v] > max:
            max = val_counts[v]
            val = v
    return val
    
    
# Calculate the entropy of a set of values 
# First count how often each value shows up 
# When you divide this value by the total number 
# of elements, you get the probability for that element 
# The entropy is the negation of the sum of p*log2(p) 
# for all these probabilities.
def entropy(values):
    val_counts = counts(values)
    entropies = [(-val_counts[v] / len(values)) * math.log(val_counts[v] / len(values)) for v in val_counts]
    return sum(entropies)

# This is the main decision tree class 
# DO NOT CHANGE THE FOLLOWING LINE
class DecisionTree:
# DO NOT CHANGE THE PRECEDING LINE
    def __init__(self, tree={}):
        self.tree = tree
    
    # DO NOT CHANGE THE FOLLOWING LINE    
    def fit(self, x, y, max_depth=None):
    # INEDO NOT CHANGE THE PRECEDING L
    
        self.majority = majority(y)
        self.tree = make_node(y, x, y, list(range(len(x[0]))), 0, max_depth)
    
    def classify(self, current_node, x):
        if current_node["type"] == "class":
            return current_node["class"]
        else:
            split_attribute = x[current_node["split"]]
            if split_attribute not in current_node["children"]:
                return self.majority
            return self.classify(current_node["children"][split_attribute], x)
        
    # DO NOT CHANGE THE FOLLOWING LINE    
    def predict(self, x):
    # DO NOT CHANGE THE PRECEDING LINE    
        if not self.tree:
            return None

        return [self.classify(self.tree, instance) for instance in x]
    
    def prune(self, ys, num_leaves_to_prune):
        self.init_node_errors(self.tree)
        self.classify_validation_data(ys)
        twigs = []
        self.collect_twigs(self.tree, twigs)
        
        get_twig_error = lambda node: node['Node Error']
        twigs = sorted(twigs, key=get_twig_error, reverse=True)
        
        num_leaves_pruned = 0
        while True:
            if num_leaves_pruned >= num_leaves_to_prune:
                break
            else:
                if len(twigs) == 0:
                    twigs = []
                    self.collect_twigs(self.tree, twigs)
                    twigs = sorted(twigs, key=get_twig_error, reverse=True)
                    
                    if len(twigs) == 0:
                        break # No more twigs
                else:
                    twig = twigs.pop(0)
                    twig["type"] = "class"
                    twig["class"] = twig["majority"]
                    num_leaves_pruned += len(twig["children"])
                    num_leaves_pruned -= 1 # adding back in the twig
                    del twig["children"]
                    del twig["split"]
        
    def calculate_height(self, node):
        if node["type"] == "class":
            return 1
        else:
            heights = []
            for child in node["children"]:
                heights.append(1 + self.calculate_height(node["children"][child]))    
            return max(heights)
        
    def init_node_errors(self, node):
        node["Node Error"] = 0
        if node["type"] == "split":
            for child in node["children"]:
                self.init_node_errors(node["children"][child])

    def is_twig(self, node):
        if node["type"] == "split":
            for child in node["children"]:
                if node["children"][child]["type"] == "split":
                    return False
            return True
        return False
    
    def count_leaves(self, node):
        if node["type"] == "class":
            return 1
        else:
            n = 0
            for child in node["children"]:
                n += self.count_leaves(node["children"][child])
            return n 
            
    def collect_twigs(self, node, twigs):
        if(self.is_twig(node)):
            twig_error = node["Node Error"]
            for child in node["children"]:
                twig_error -= (node["children"][child]["Node Error"]) # twig error if this twig became a leaf instead
            node["Node Error"] = twig_error
            twigs.append(node)
        else:
            if node["type"] == "split":
                for child in node["children"]:
                    self.collect_twigs(node["children"][child], twigs)
        
    def classify_validation_data(self, ys):
        for y in ys:
            self.classify_validation_instance(self.tree, y)
            
    def classify_validation_instance(self, node, y):
        if node["type"] == "split":
            if node["majority"] != y:
                node["Node Error"] += 1
            for child in node["children"]:
                self.classify_validation_instance(node["children"][child], y)
        else:
            if node["class"] != y:
                node["Node Error"] += 1
     
    # DO NOT CHANGE THE FOLLOWING LINE
    def to_dict(self):
    # DO NOT CHANGE THE PRECEDING LINE
        # change this if you store the tree in a different format
        return self.tree
       