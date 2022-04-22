import random
import math
import numpy as np

def lloyds(data, k, columns, centers=None, n=None, eps=None):
    # Initial Cluster centers
    if centers == None:
        centers = random.sample(list(data), k)
    
        for i in range(k):
            centers[i] = [centers[i][c] for c in columns]
    
    curr_iter = 0
    curr_eps = 0

    if n == None:
        n = math.inf
    if eps == None:
        eps = -math.inf
        
    while curr_iter < n and curr_eps >= eps:
        print(curr_iter, curr_eps)
        # Assign data points based on centers
        clusters = determine_cluster(data, centers, k, columns)
        
        # Compute new centers
        avg_dist = 0
        for (i, cluster) in enumerate(clusters):
            new_center = average(cluster, columns)
            avg_dist += np.sqrt(np.sum(np.power(centers[i] - new_center, 2)))
            centers[i] = new_center
    
        curr_iter += 1
        curr_eps = avg_dist / k
    
    return centers
    
    
def determine_cluster(data, centers, k, columns):
    clusters = [[] for i in range(0, k)]
    for elem in data:
            min = math.inf
            index = -1
            for j in range(0, k):
                dist = distance(centers[j], elem, columns)
                if dist < min:
                    min = dist
                    index = j
            clusters[index].append(elem)
    return clusters

def distance(center, instance, columns):
    instance_data = [instance[c] for c in columns]
   
    center_data = np.array(center)
    instance_data = np.array(instance_data)

    return np.sqrt(np.sum(np.power(center_data - instance_data, 2)))

def average(cluster, columns):
    cluster_data = []
    
    for elem in cluster:
        cluster_data.append([elem[c] for c in columns])
    
    cluster_data = np.array(cluster_data)
    return np.average(cluster_data, axis=0)
    
# DO NOT CHANGE THE FOLLOWING LINE
def kmedoids(data, k, distance, centers=None, n=None, eps=None):
# DO NOT CHANGE THE PRECEDING LINE
    # This function has to return a list of k cluster centroids (data instances!)
    pass

