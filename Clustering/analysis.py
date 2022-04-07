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
    # min_max_scaler = preprocessing.MinMaxScaler()
    
    # scaled_df = pd.DataFrame(min_max_scaler.fit_transform(df.loc[:, ~df.columns.isin(['STATE', 'YEAR', 'CITY'])]))
    
    # df = pd.concat([scaled_df, df['STATE'], df['YEAR'], df['CITY']], axis = 1)
    
    # print(df)
    
    col_start = len(df.columns)
    
    crime_start = df.columns.get_loc("aggravated-assault")
    crime_df = df.iloc[:, range(crime_start, len(df.columns))].reset_index(drop=True)
    
    min_max_scaler = preprocessing.MinMaxScaler()
    df = df.join(pd.DataFrame(min_max_scaler.fit_transform(crime_df)))
    
    print(df)
    
    data = [item for (idx, item) in df.iterrows()]
    k = 2
    columns = range(col_start, len(data[0]))
    
    centers = lloyds(data, k, columns, n=2) # Cols skip STATE, YEAR, CITY
    clusters = determine_cluster(data, centers, k, columns)
     
    
    cluster_df = pd.DataFrame()
    colors = ["Green", "Red", "Blue"]
    for (i, cluster) in enumerate(clusters):
        elems = pd.DataFrame(cluster)
        elems["Color"] = colors[i]
        cluster_df = cluster_df.append(elems)
    
    print(cluster_df)
    pca = pca = PCA(n_components=len(cluster_df.columns) - 4) # Exclude non-numerical data

    pcs = pca.fit_transform(cluster_df.loc[:, ~cluster_df.columns.isin(['STATE', 'YEAR', 'CITY', 'Color'])])
    
    pc_df = pd.DataFrame(data = pcs[:, 0:2], columns = ['pc 1', 'pc 2'])
    pc_df = pd.concat([pc_df, cluster_df[['Color']]], axis = 1)
    print(pc_df)
    pc_df.dropna(inplace=True)
    plot_reduced(pc_df, colors, ["pc 1", "pc 2"], "PCA")
    
    
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

if __name__ == "__main__":
    main()