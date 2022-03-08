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

print(df)    
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
import pywt 


def normalize(df, crime=False):
    result = df.copy()
    for name in df.columns:
        (mean, std) = statistics[name] if not crime else statistics["CRIME"][name]
        result[name] = (df[name] - mean) / std # z-score
    return result

def reduce_vector(data_vector):
    (approx, detail) = pywt.dwt(data_vector, 'haar', mode='zpd')
    if len(approx) == 1:
        return (approx, detail)
    else:
        return reduce_vector(approx)
        
def calculate_wavelet_coeff(df):
    coeff = pd.DataFrame()
    approximations = []
    details = []
    for i, row in df.iterrows():
        (approx, detail) = reduce_vector(row.tolist())
        approximations.append(approx[0])
        details.append(detail[0])
        
    coeff["Approximations"] = approximations
    coeff["Details"] = details
    
    return coeff

def plot(df, bins, colors, col_names):
    for bin, color in zip(binNames, colors):
        indicesToKeep = pc_df['Bin'] == bin
        plt.scatter(df.loc[indicesToKeep, col_names[0]],
                    df.loc[indicesToKeep, col_names[1]],
                    c = color,
                    s = 40)
    plt.xlabel(col_names[0])
    plt.ylabel(col_names[1])
    plt.legend(binNames)  
    plt.show()

crime_start = df.columns.get_loc("aggravated-assault")

city_attributes = df.iloc[:, range(3, crime_start)] # Starting from 3 to skip STATE, CITY, YEAR
crime_attributes = df.iloc[:, range(crime_start, len(df.columns))]

scaled_city = normalize(city_attributes)
print(scaled_city)
                                                                         # covar(x1, x1) Just represents variance in that attribute
pca = PCA(n_components = len(scaled_city.columns)) # Covariance matrix ([covar(x1,x1), covar(x1, x2), etc.]). Finding eigenvectors and eigenvalues from this matrix. Eigenvectors are sorted according to eigenvalues. Eigenvalues represents how much variance that eigenvector accounts for. Variance meaning how spread out the points are along that vector. 

pcs = pca.fit_transform(scaled_city)

variance = np.cumsum(np.round(pca.explained_variance_ratio_, decimals=3)*100)
print("DATA REDUCTION OUTPUT")
print("Variance = ", variance) # OBSERVATION: first 3 components account for 91% of variance

print(pd.DataFrame(data = pca.components_[0], columns = ['eigenvector'])) # weights or loadings of the first eigenvector. First eigenvector = eigenvector with highest absolute eigenvalue. Can use n eigenvectors to form a new matrix which can be used to calculate the new dataset. Transformed dataset = Normalized matrix * eigenmatrix?

pc_df = pd.DataFrame(data = pcs[:, 0:2], columns = ['pc 1', 'pc 2'])
print(pc_df)

crime_attributes["Total"] = crime_attributes.iloc[:, range(len(crime_attributes.columns))].sum(axis=1) # Exclude approximations from total

binNames = ["Low", "Medium", "High"]
crime_attributes["Bin"] = pd.cut(crime_attributes["Total"], 3, labels=binNames)

print("----------CRIME ATTRIBUTES----------")
print(crime_attributes)

pc_df = pd.concat([pc_df, crime_attributes[['Bin']]], axis = 1)
print(pc_df)


colors = ["lightcoral", "blue", "red"]

plot(pc_df, binNames, colors, ["pc 1", "pc 2"])  # So for each row the city attribs can now be reduced down to just these two components. Plotting each city according to these two components in this new basis(Years has no effect, so essentilly plotting the same cities at different years). Not using the city names to identify each point instead binning crime in each city and color coding to see if there are clusters of cities with similar crime. For ex. L.A, 12000(tot pop), 5000(# males), High -> L.A, -2, -3, High. Point at -2, -3 is identified by high crime instead of city name

# Plotting wavelet
wavelet_df = calculate_wavelet_coeff(scaled_city)

wavelet_df = pd.concat([wavelet_df, crime_attributes[['Bin']]], axis = 1)
print(wavelet_df)

plot(wavelet_df, binNames, colors, ["Approximations", "Details"]) # plotting wavelet
