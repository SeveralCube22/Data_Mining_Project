import pandas as pd
import matplotlib.pyplot as plt

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
        
# Data Clean

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
        
# Summary Statistics

statistics = {} # overall statisitcs 
statistics["CRIME"] = {}

populate_summary_statistics(df, statistics)
    
# print(statistics["CRIME"])
df = df.drop("human-trafficing", 1) # mean and std are 0

year_statistics = {}

for name, group in df.groupby("YEAR"):
    year_statistics[name] = {}
    year_statistics[name]["CRIME"] = {}
    populate_summary_statistics(group, year_statistics[name])
   
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
print("---------------------------------------------------------")

# Data Reduction

import numpy as np
from sklearn.decomposition import PCA

def normalize(df):
    result = df.copy()
    for name in df.columns:
        result[name] = (df[name] - statistics[name][0]) / statistics[name][1] # z-score
    return result

crime_start = df.columns.get_loc("aggravated-assault")

city_attributes = df.iloc[:, range(3, crime_start)] # Starting from 3 to skip STATE, CITY, YEAR
crime_attributes = df.iloc[:, range(crime_start, len(df.columns))]

scaled_city = normalize(city_attributes)
                                                                         # covar(x1, x1) Just represents variance in that attribute
pca = PCA(n_components = len(scaled_city.columns)) # Covariance matrix ([covar(x1,x1), covar(x1, x2), etc.]). Finding eigenvectors and eigenvalues from this matrix. Eigenvectors are sorted according to eigenvalues. Eigenvalues represents how much variance that eigenvector accounts for. Variance meaning how spread out the points are along that vector. 

pcs = pca.fit_transform(scaled_city)

variance = np.cumsum(np.round(pca.explained_variance_ratio_, decimals=3)*100)
print("DATA REDUCTION OUTPUT")
print("Variance = ", variance) # OBSERVATION: first 3 components account for 91% of variance

print(pd.DataFrame(data = pca.components_[0], columns = ['eigenvector'])) # weights or loadings of the first eigenvector. First eigenvector = eigenvector with highest absolute eigenvalue

pc_df = pd.DataFrame(data = pcs[:, 0:2], columns = ['pc 1', 'pc 2'])
print(pc_df)

crime_attributes['Total'] = crime_attributes.iloc[:, range(len(crime_attributes.columns))].sum(axis=1)

crime_quantiles = crime_attributes.Total.quantile([0.33,0.66])

def bin(crime_rows):
    if crime_rows["Total"] <= crime_quantiles[.33]:
        return 'Low'
    elif crime_rows["Total"] <= crime_quantiles[.66]:
        return "Medium"
    else:
        return "High"
    
crime_attributes["Bin"] = crime_attributes.apply(bin, axis = 1)
print(crime_attributes)

pc_df = pd.concat([pc_df, crime_attributes[['Bin']]], axis = 1)
print(pc_df)

bins = ["Low", "Medium", "High"]
colors = ["lightcoral", "gold",  "red"]

for bin, color in zip(bins, colors):
    indicesToKeep = pc_df['Bin'] == bin
    plt.scatter(pc_df.loc[indicesToKeep, 'pc 1'],
                pc_df.loc[indicesToKeep, 'pc 2'],
                c = color,
                s = 50)

plt.legend(bins)  
plt.show() # So for each row the city attribs can now be reduced down to just these two components. Plotting the cities accoring to these two components (Years has no affect, so essentilly plotting same cities at different years). Binning crime in each city and color coding to see if there are clusters of cities with similar crime. 

