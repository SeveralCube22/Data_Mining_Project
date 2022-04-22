from clustering import lloyds, determine_cluster
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.decomposition import PCA
from sklearn import preprocessing
import numpy as np
import sys
from os.path import abspath


def main():
    sys.path.append(abspath("./data_mining/data_analysis"))
    print(sys.path)
    import data_analysis
    df = data_analysis.data_clean()
    
    crime_start = df.columns.get_loc("aggravated-assault")
    crime_end = crime_start + 11 # Num crime attributes
    
    crime_df = df.iloc[:, range(crime_start, len(df.columns))]
    
    min_max_scaler = preprocessing.MinMaxScaler()
    crime_df = pd.DataFrame(min_max_scaler.fit_transform(crime_df))
    
    df.reset_index(drop=True, inplace=True)
    df = df.join(crime_df)
    
    print(df)
    
    data = [item for (idx, item) in df.iterrows()]
    
    k = 5
    columns = range(0, 11) # Scaled crime attributes 0-10
    
    centers = lloyds(data, k, columns, n=100, eps=0) 
    clusters = determine_cluster(data, centers, k, columns)
     
    
    cluster_df = pd.DataFrame()
    colors = ["Green", "Red", "Blue", "Yellow", "Orange"]
    for (i, cluster) in enumerate(clusters):
        elems = pd.DataFrame(cluster)
        elems["Color"] = colors[i]
        cluster_df = cluster_df.append(elems)
    
    pca = PCA(n_components=len(crime_df.columns)) 

    pcs = pca.fit_transform(crime_df)
    
    pc_df = pd.DataFrame(data = pcs[:, 0:2], columns = ['pc 1', 'pc 2'])
    pc_df = pd.concat([pc_df, cluster_df[['Color']]], axis = 1)
    print(pc_df)
    
    plot_reduced(pc_df, colors, ["pc 1", "pc 2"], "PCA")            
    plot_crime_hist(cluster_df, colors, crime_start, crime_end)
    plot_crime_pie_chart(cluster_df, colors, crime_start, crime_end)
    plot_all_city_clusters(cluster_df, colors, crime_start)
    plot_all_city_clusters(cluster_df, colors, crime_start, attribs=["Gini Index", "Total Population"], same=False)
    
    for c in colors:
        print("%s: %d" % (c, cluster_df.loc[cluster_df['Color'] == c]))

        
def plot_reduced(df, colors, col_names, title):
    for color in colors:
        indicesToKeep = df['Color'] == color
        plt.scatter(df.loc[indicesToKeep, col_names[0]],
                    df.loc[indicesToKeep, col_names[1]],
                    c = color,
                    s = 40)
    plt.title(title)
    plt.xlabel(col_names[0])
    plt.ylabel(col_names[1])
    plt.show()
    
def get_city_cluster(cluster_df, color, crime_start):
    cluster = cluster_df.loc[cluster_df['Color'] == color]
    cluster = cluster.iloc[:, range(3, crime_start)] # Skip State, Year, City and get all city attribs until crime attribs
    
    city_attribs = {}
    for (i, name) in enumerate(cluster):
        x = cluster[name].mean()
        min = cluster_df[name].min()
        max = cluster_df[name].max()
        city_attribs[name] = (x, (x - min) / (max - min))
        
    return city_attribs

def get_attribs_diffs(cluster_data): # [{attrib1: val}, {attrib1: val}, ..] list of city data belonging to each cluster
    average_diff = 0
    city_attribs_diffs = {}
    for key in cluster_data[0].keys():
        attrib_diff = cluster_data[0][key][1] # normalized attribute
        avg = 0
        for city in range(1, len(cluster_data) + 1): # cycle around and calculate diffs attrib 1 - attrib 2, attr 2 - attr 3, etc.
            city %= len(cluster_data)
            val = cluster_data[city][key][1]
            attrib_diff = abs(attrib_diff - val)
            avg += attrib_diff
            attrib_diff = val
        
        avg = (avg / len(cluster_data[0]))
        average_diff += avg
        city_attribs_diffs[key] = avg
    
    return average_diff / len(cluster_data[0].keys()), city_attribs_diffs

def get_best_attribs(cluster_data):
    average_diff, attribs_diffs = get_attribs_diffs(cluster_data)
    attribs = []
    for attrib in attribs_diffs:
        if attribs_diffs[attrib] > average_diff:
            attribs.append(attrib)
    return attribs
        
def plot_all_city_clusters(cluster_df, colors, crime_start, attribs=None, same=True):   
    city_cluster_data = []
    for i in range(len(colors)):
        city_cluster_data.append(get_city_cluster(cluster_df, colors[i], crime_start))
    
    attribs = get_best_attribs(city_cluster_data) if attribs is None else attribs
    if same:
        plot_on_same_hist(city_cluster_data, attribs, colors)
    else:
        for attrib in attribs:
            values = [city_cluster_data[i][attrib][0] for i in range(len(colors))]
            plt.bar(colors, values, color=colors)
            plt.title(attrib)
            plt.show()
   
def plot_on_same_hist(city_cluster_data, attribs, colors):
    data = {}
    for i in range(len(colors)):
        values = [city_cluster_data[i][attrib][1] for attrib in attribs]    
        data[colors[i]] = values
    
    plot_data_hist(data, attribs, colors)

def plot_crime_pie_chart(cluster_df, colors, crime_start, crime_end):
    for c in colors:
        cluster = cluster_df.loc[cluster_df['Color'] == c]
        crime = cluster.iloc[:, range(crime_start, crime_end)]
        
        cluster["Total"] = crime.sum(axis=1)
        print(cluster)
        total_crimes = cluster["Total"].sum()
        print(cluster["Total"])
        attribs = []
        vals = []
        
        for i in range(len(crime.columns)):
            name = crime.columns[i]
            attribs.append(name)
            vals.append(crime[name].sum() / total_crimes) 
        
        plt.pie(vals, labels=attribs, autopct='%1.1f%%')
        plt.title(c)
        plt.show()
        
def plot_crime_hist(cluster_df, colors, crime_start, crime_end):
    attribs = []
    data = {}
    for c in colors:
        cluster = cluster_df.loc[cluster_df['Color'] == c]
        crime = cluster.iloc[:, range(crime_start, crime_end)]
        crime["Total"] = crime.sum(axis=1)
        
        vals = []
        
        for i in range(len(crime.columns)):
            name = crime.columns[i]
            if len(attribs) < 11:
                attribs.append(name)
            vals.append(crime[name].mean()) 
        
        data[c] = vals
    
    attribs.append("Total")
    plot_data_hist(data, attribs, colors)
    
    
def plot_data_hist(data, labels, colors):
    hist = pd.DataFrame(data, index=labels)
    hist.plot.bar(rot=0, color=colors, legend=False)
    plt.show()

if __name__ == "__main__":
    main()