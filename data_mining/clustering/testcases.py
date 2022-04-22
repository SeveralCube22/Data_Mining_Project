import math
import matplotlib.pyplot as plt
import numpy as np
import random
import clustering
import pandas
import sys

random.seed(0)

# Show a 2D scatterplot using two dimensions of the data 
# Each point is colored based on which cluster center it is closest to 
def plot(data, centers, x, y, scale=None):
    def dist(point,center):
        return math.sqrt((point[x] - center[0])**2 + (point[y] - center[1])**2)
    xs, ys, colors = [], [], []
    for d in data:
        mind = None 
        cluster = None 
        for i,c in enumerate(centers):
            delta = dist(d, c)
            if mind is None or delta < mind:
                mind = delta
                cluster = i
        xs.append(d[x])
        ys.append(d[y])
        colors.append(cluster)
        
    cxs, cys, ccolors = [], [], []
    for i,c in enumerate(centers):
        cxs.append(c[0])
        cys.append(c[1])
        ccolors.append(i)
    if scale is None:
        fr = min(min(xs), min(ys), min(cxs), min(cys))
        to = max(max(xs), max(ys), max(cys), max(cys))
        range = (to-fr)
        fr -= 0.01*range
        to += 0.01*range
    else:
        fr,to = scale
    plt.scatter(xs, ys, c=colors)
    plt.scatter(cxs, cys, c=ccolors, marker = "+")
    plt.xlim((fr,to))
    plt.ylim((fr,to))
    plt.show()
    
def show_centers(centers):
    for i,c in enumerate(centers):
        print(f"   cluster center {i+1}: {tuple(c)}")
    
LLOYD_TESTS = ["Array test", "Two clusters single step (before/after comparison)", "Two clusters 2 steps", "Three clusters single step (before/after comparison)", "Three clusters 5 steps", "Two clusters w/ epsilon", "Three clusters w/ epsilon", "Six clusters (4D)", "Two clusters on 3-cluster data"]
    
def lloyds_testcase(data, n, visualize=True):
    print("running test:", LLOYD_TESTS[n])
    if n == 0:
        rdata = [[name, random.random()*random.random(), random.random()*0.45 + 0.2] for i,name in enumerate("abcdefghijklmnopqrstuvxyz")]
        clusters = clustering.lloyds(data, 3, [1,2], n=10)
        if visualize:
            plot(rdata, clusters, 1, 2, scale=(0,1))
        show_centers(clusters)
    elif n == 1:
        centers = [[0.1,0.05], [0.8,0.9]]
        if visualize:
            plot(data, centers, 3, 4, scale=(0,1))
        centers = clustering.lloyds(data, 2, [3,4], centers=centers, n=1)
        if visualize:
            plot(data, centers, 3, 4, scale=(0,1))
        show_centers(centers)
    elif n == 2:
        centers = [[0.1,0.05], [0.8,0.9]]
        centers = clustering.lloyds(data, 2, [3,4], centers=centers, n=2)
        if visualize:
            plot(data, centers, 3, 4, scale=(0,1))
        show_centers(centers)
    elif n == 3:
        centers = [[0.5,0.1], [0.1,0.1], [0.8,0.4]]
        if visualize:
            plot(data, centers, 1, 2, scale=(0,1))
        centers = clustering.lloyds(data, 3, [1,2], centers=centers, n=1)
        if visualize:
            plot(data, centers, 1, 2, scale=(0,1))
        show_centers(centers)
    elif n == 4:
        centers = [[0.5,0.1], [0.1,0.1], [0.8,0.4]]
        centers = clustering.lloyds(data, 3, [1,2], centers=centers, n=5)
        if visualize:
            plot(data, centers, 1, 2, scale=(0,1))
        show_centers(centers)
    elif n == 5:
        centers = clustering.lloyds(data, 2, ["x3","x4"], eps=0.01)
        if visualize:
            plot(data, centers, "x3", "x4", scale=(0,1))
        show_centers(centers)
    elif n == 6:
        centers = clustering.lloyds(data, 3, ["x1","x2"], eps=0.01)
        if visualize:
            plot(data, centers, "x1", "x2", scale=(0,1))
        show_centers(centers)
    elif n == 7:
        centers = clustering.lloyds(data, 6, ["x1","x2", 3, "x4"], n=10)
        show_centers(centers)
    elif n == 8:
        centers = clustering.lloyds(data, 2, ["x1","x2"], n=5)
        if visualize:
            plot(data, centers, "x1", "x2", scale=(0,1))
        show_centers(centers)
        
    
def lloyds_test(df, steps):
    test_menu(df, steps, LLOYD_TESTS, lloyds_testcase)

KMEDOIDS_TESTS = ["Compare categories, single step", "Compare categories, 5 steps", "Compare binary, single step", "Compare binary, 5 steps", "Compare category and binary, single step", "Compare category and binary, 5 steps (this does not cluster well)"]

CATEGORY_MAP = {"low": 0, "medium": 0.5, "high": 1}

def compare_categories(a,b):
    def compare(cata, catb):
        if cata == catb: return 0
        return abs(CATEGORY_MAP[cata] - CATEGORY_MAP[catb])
    return sum([compare(a[col],b[col]) for col in ["cat1", "cat2", "cat3", "cat4"]])/4.0

def compare_binary(a,b):
    def compare(cata, catb):
        if cata == catb: return 0
        return 1
    return sum([compare(a[col],b[col]) for col in ["bin1", "bin2", "bin3", "bin4", "bin5"]])/5.0
    
def compare_both(a,b):
    return (compare_categories(a,b) + compare_binary(a,b))/2.0
    
def evaluate(data, centroids, distance, ground_truth):
    clusters = [[] for c in centroids]
    for d in data:
        mind = distance(centroids[0], d)
        idx = 0
        for i,c in enumerate(centroids[1:]):
            delta = distance(c, d)
            if delta < mind: 
                mind = delta 
                idx = i + 1
        clusters[idx].append(d)
        
    for c in clusters:
        ids = [tuple(d[ground_truth]) for d in c]
        counts = []
        for id in set(ids):
            counts.append(ids.count(id))
        if not counts:
            print("No data instances in cluster")
        else:
            print("Agreement: %.2f%%"%(max(counts)*100.0/sum(counts)))
         
    
def kmedoids_testcase(data, n, visualize=True):
    print("running test:", KMEDOIDS_TESTS[n])
    if n == 0:
        centroids = clustering.kmedoids(data, 2, compare_categories, n=1)
        evaluate(data, centroids, compare_categories, ["cls3"])
    if n == 1:
        centroids = clustering.kmedoids(data, 2, compare_categories, n=5)
        evaluate(data, centroids, compare_categories, ["cls3"]) 
    elif n == 2:
        centroids = clustering.kmedoids(data, 2, compare_binary, n=1)
        evaluate(data, centroids, compare_binary, ["cls4"])
    elif n == 3:
        centroids = clustering.kmedoids(data, 2, compare_binary, n=5)
        evaluate(data, centroids, compare_binary, ["cls4"])
    elif n == 4:
        centroids = clustering.kmedoids(data, 4, compare_binary, n=1)
        evaluate(data, centroids, compare_binary, ["cls3", "cls4"])
    elif n == 5:
        centroids = clustering.kmedoids(data, 4, compare_binary, n=5)
        evaluate(data, centroids, compare_binary, ["cls3", "cls4"])
    

def kmedoids_test(df, steps):
    test_menu(df, steps, KMEDOIDS_TESTS, kmedoids_testcase)
    
    
    
def test_menu(df, steps, tests, function):
    while True:
        print("Which test case do you want to run?")
        for i,t in enumerate(tests):
            print(f"   {i} {t}")
        print("   r return to main menu")    
        print("   q exit")
        if steps:
            x = steps[0]
            del steps[0]
        else:
            x = input("> ")
        if x in [str(i) for i,_ in enumerate(tests)]:
            function(df, int(x))
        elif x == "r":
            print()
            return
        elif x == "q":
            print("Bye")
            exit(0)
        else:
            print("Please select a test case, r or q")
        print()
    
def main(auto=False, all=False, steps=[]):
    df = pandas.read_csv("./Clustering/testdata.csv")
    data = [item for (idx,item) in df.iterrows()]
    print(data)
    if auto:
        for i,t in enumerate(LLOYD_TESTS):
            lloyds_testcase(data, i, False)
        if all:
            for i,t in enumerate(KMEDOIDS_TESTS):
                kmedoids_testcase(data, i, False)
        return
    while True:
        print("Which algorithm do you want to test?")
        print("   0 Lloyd's")
        print("   1 k-medoids")
        print("   q none, exit")
        if steps:
            x = steps[0]
            del steps[0]
        else:
            x = input("> ")
        if x == "0":
            lloyds_test(data, steps)
        elif x == "1":
            kmedoids_test(data, steps)
        elif x == "q":
            return 
        else:
            print("Please select 0, 1 or q")
    
    
    
if __name__ == "__main__":
    if "--help" in sys.argv:
        print("Usage: testcases.py [--auto] [--all] [-a|--auto-all] steps")
        print("   --auto runs the tests automatically")
        print("   --all only works in combination with --auto and runs all tests (lloyds and kmedoids) together")
        print("   -a and --auto-all are aliases for '--auto --all'")
        print("   <steps> is a sequence of inputs that are passed to the menu before it accepts manual input.")
        print("           This allows you to run e.g. 'python testcases.py 02q' to select option 0 in the")
        print("           main menu, followed by 2 in the Lloyd's test case menu, followed by q(uit)")
        print("           Essentially, this allows you to repeatedly run any test/combination of tests without")
        print("           having to navigate the menu every time.")
        sys.exit(0)
    else:
        main("--auto" in sys.argv or "--auto-all" in sys.argv or "-a" in sys.argv, 
             "--all" in sys.argv or "--auto-all" in sys.argv or "-a" in sys.argv, 
             list("".join([arg for arg in sys.argv[1:] if "--" not in arg])))
        