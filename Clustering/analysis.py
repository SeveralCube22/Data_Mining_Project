from clustering import lloyds, determine_cluster
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.decomposition import PCA
from sklearn import preprocessing

def data_clean():
    # Some attributes have null values, since the range are values > 0, the null values will become -1.
    df = pd.read_csv("./Data Acquisition/data.csv", sep=",", encoding="latin1")
    df.columns = df.columns.str.strip()

    for rowI, row in df.iterrows(): #iterate over rows
        colI = 0
        for col, value in row.items():
            if isinstance(value, str):
                value = value.strip()
                if value == "null":
                    df.iat[rowI, colI] = -1 # Note: iat returns some object that overloads [] or setitem dunder
                else:
                    try:
                        df.iat[rowI, colI] = float(value) 
                    except:
                        pass
            colI += 1

    df.dropna(inplace=True)
    df.drop("human-trafficing", 1, inplace=True) # mean and std are 0
    return df 

def main():
    df = data_clean()
    
    crime_start = df.columns.get_loc("aggravated-assault")
    crime_end = crime_start + 11 # Num crime attributes
    
    crime_df = df.iloc[:, range(crime_start, len(df.columns))]
    
    min_max_scaler = preprocessing.MinMaxScaler()
    crime_df = pd.DataFrame(min_max_scaler.fit_transform(crime_df))
    
    df.reset_index(drop=True, inplace=True)
    df = df.join(crime_df)
    
    print(df)
    
    data = [item for (idx, item) in df.iterrows()]
    
    k = 3
    columns = range(0, 11) # Scaled crime attributes 0-10
    
    centers = lloyds(data, k, columns, n=50) 
    clusters = determine_cluster(data, centers, k, columns)
     
    
    cluster_df = pd.DataFrame()
    colors = ["Green", "Red", "Blue"]
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
    
    cluster_df["Total Crimes"] = cluster_df.iloc[:, range(crime_start, crime_end)].sum(axis=1)
    
    print(cluster_df)
    
    for i, row in cluster_df.iterrows():
        if row["Gini Index"] > 1:
            cluster_df.drop(i, inplace=True)
            
    plot_all_city_clusters(cluster_df, colors, crime_start)

    
def plot_cluster_city(cluster_df, city_attrib):
    plt.scatter(cluster_df[city_attrib], cluster_df["Total Crimes"], c=cluster_df["Color"])
    plt.show()
    
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
        city_attribs[name] = cluster[name].mean()
        
    return city_attribs

def get_city_attribs_diffs(city_cluster_data): # [{attrib1: val}, {attrib1: val}, ..] list of city data belonging to each cluster
    average_diff = 0
    city_attribs_diffs = {}
    for key in city_cluster_data[0].keys():
        attrib_diff = city_cluster_data[0][key]
        avg = 0
        for city in range(1, len(city_cluster_data) + 1): # cycle around and calculate diffs attrib 1 - attrib 2, attr 2 - attr 3, etc.
            city %= len(city_cluster_data)
            val = city_cluster_data[city][key]
            attrib_diff = abs(attrib_diff - val)
            avg += attrib_diff
            attrib_diff = val
        
        avg = (avg / len(city_cluster_data[0]))
        average_diff += avg
        city_attribs_diffs[key] = avg
    
    return average_diff / len(city_cluster_data[0].keys()), city_attribs_diffs

def get_best_city_attribs(city_cluster_data):
    average_diff, city_attribs_diffs = get_city_attribs_diffs(city_cluster_data)
    attribs = []
    for attrib in city_attribs_diffs:
        if city_attribs_diffs[attrib] > average_diff:
            attribs.append(attrib)
    return attribs
        
def plot_all_city_clusters(cluster_df, colors, crime_start):
    fig, axs = plt.subplots(1, 1, figsize=(9, 3), sharey=True)
    
    city_cluster_data = []
    for i in range(len(colors)):
        city_cluster_data.append(get_city_cluster(cluster_df, colors[i], crime_start))
    
    attribs = get_best_city_attribs(city_cluster_data)
    for i in range(len(colors)):
        values = [city_cluster_data[i][attrib] for attrib in attribs]
        axs.bar(attribs, values, color=colors[i])
        
    plt.show()

if __name__ == "__main__":
    main()