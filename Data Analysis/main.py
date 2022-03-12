import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn import preprocessing
from sklearn.decomposition import PCA

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

def populate_summary_statistics(df, statistics):
    crime_start = df.columns.get_loc("aggravated-assault")
    for (i, col) in enumerate(df.columns):
        if col == "YEAR":
            continue
        try:
            value = (df[col].mean(), df[col].std())
            if i < crime_start:
                statistics[col] = value
            else:
                statistics["CRIME"][col] = value 
        except:
            pass # STATE, CITY
        
def get_summary_stats(df):
    statistics = {} # overall statisitcs 
    statistics["CRIME"] = {}

    populate_summary_statistics(df, statistics)
    
    year_statistics = {}

    for name, group in df.groupby("YEAR"):
        year_statistics[name] = {}
        year_statistics[name]["CRIME"] = {}
        populate_summary_statistics(group, year_statistics[name])
      
    return statistics, year_statistics

def plot_stats(year_statistics):
    plot_crime = {}
    for year in year_statistics:
        for crime_statistic, crime_value in year_statistics[year]["CRIME"].items():
            if crime_statistic in plot_crime:
                plot_crime[crime_statistic].append(crime_value[0]) # only get the mean
            else:
                plot_crime[crime_statistic] = [crime_value[0]]
        
    for crime_statistic, mean in plot_crime.items():
        plt.plot(year_statistics.keys(), mean, '.-', label=crime_statistic)

    plt.legend()
    plt.show()  
    
def plot_reduced(df, bin_names, colors, col_names):
    for bin, color in zip(bin_names, colors):
        indicesToKeep = df['Bin'] == bin
        plt.scatter(df.loc[indicesToKeep, col_names[0]],
                    df.loc[indicesToKeep, col_names[1]],
                    c = color,
                    s = 40)
    plt.xlabel(col_names[0])
    plt.ylabel(col_names[1])
    plt.legend(bin_names)  
    plt.show()

def principal_components(scaled_city, crime_attributes, statistics, bin_names, colors):
                                                                         # covar(x1, x1) Just represents variance in that attribute
    pca = PCA(n_components = len(scaled_city.columns)) # Covariance matrix ([covar(x1,x1), covar(x1, x2), etc.]). Finding eigenvectors and eigenvalues from this matrix. Eigenvectors are sorted according to eigenvalues. Eigenvalues represents how much variance that eigenvector accounts for. Variance meaning how spread out the points are along that vector. 

    pcs = pca.fit_transform(scaled_city)

    variance = np.cumsum(np.round(pca.explained_variance_ratio_, decimals=3)*100)
    print("DATA REDUCTION OUTPUT")
    print("Variance = ", variance) # OBSERVATION: first 3 components account for 91% of variance

    weights = pd.DataFrame(data = pca.components_[0], columns = ['eigenvector']) # weights or loadings of the first eigenvector. First eigenvector = eigenvector with highest absolute eigenvalue. Can use n eigenvectors to form a new matrix which can be used to calculate the new dataset. Transformed dataset = Normalized matrix * eigenmatrix?

    print("TOP WEIGHTS IN EIGENVECTOR PC 1")
    for index, value in weights[(weights > .15).any(1)].iterrows():
        name = city_attributes.columns[index]
        print("Weight: {} Index: {} Col Name: {} Mean: {}".format(value[0], index, name, statistics[name][0]))

    print()
    weights = pd.DataFrame(data = pca.components_[1], columns = ['eigenvector'])
    print("TOP WEIGHTS IN EIGENVECTOR PC 2")
    for index, value in weights[(weights > .15).any(1)].iterrows():
        name = city_attributes.columns[index]
        print("Weight: {} Index: {} Col Name: {} Mean: {}".format(value[0], index, name, statistics[name][0]))
    
    print()
    pc_df = pd.DataFrame(data = pcs[:, 0:2], columns = ['pc 1', 'pc 2'])
    pc_df = pd.concat([pc_df, crime_attributes[['Bin']]], axis = 1)
    
    return pc_df

if(__name__ == "__main__"):
    df = data_clean()
    stats, year_stats = get_summary_stats(df)
    
    crime_start = df.columns.get_loc("aggravated-assault")

    city_attributes = df.iloc[:, range(3, crime_start)].reset_index(drop=True) # Starting from 3 to skip STATE, CITY, YEAR
    crime_attributes = df.iloc[:, range(crime_start, len(df.columns))].reset_index(drop=True)

    min_max_scaler = preprocessing.MinMaxScaler()
    scaled_city = pd.DataFrame(min_max_scaler.fit_transform(city_attributes.iloc[:, :]))
    
    bin_names = ["Low", "Medium", "High"]
    colors = ["lightcoral", "blue", "red"]
    
    crime_attributes["Total"] = crime_attributes.iloc[:, range(len(crime_attributes.columns))].sum(axis=1) # Exclude approximations from total
    crime_attributes["Bin"] = pd.qcut(crime_attributes["Total"], [0, .33, .66, 1], labels=bin_names) # [0, 3000, 10000, np.inf]
    
    pc_df = principal_components(scaled_city, crime_attributes, stats, bin_names, colors)
    plot_reduced(pc_df, bin_names, colors, ["pc 1", "pc 2"])  # So for each row the city attribs can now be reduced down to just these two components. Plotting each city according to these two components in this new basis(Years has no effect, so essentilly plotting the same cities at different years). Not using the city names to identify each point instead binning crime in each city and color coding to see if there are clusters of cities with similar crime. For ex. L.A, 12000(tot pop), 5000(# males), High -> L.A, -2, -3, High. Point at -2, -3 is identified by high crime instead of city name