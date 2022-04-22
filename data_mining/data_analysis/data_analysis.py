from cmath import isnan
from tkinter import font
from matplotlib.cm import ScalarMappable
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn import preprocessing
from sklearn.decomposition import PCA
import pywt
import geopandas as gpd
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.colors as plt_colors

def data_clean():
    # Some attributes have null values, since the range are values > 0, the null values will become -1.
    df = pd.read_csv("./data_mining/data_acquisition/data.csv", sep=",", encoding="latin1")
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
    for i, row in df.iterrows():
        if row["Gini Index"] > 1:
            df.drop(i, inplace=True)
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
    
def plot_reduced(df, bin_names, colors, col_names, title):
    for bin, color in zip(bin_names, colors):
        indicesToKeep = df['Bin'] == bin
        plt.scatter(df.loc[indicesToKeep, col_names[0]],
                    df.loc[indicesToKeep, col_names[1]],
                    c = color,
                    s = 40)
    plt.title(title)
    plt.xlabel(col_names[0])
    plt.ylabel(col_names[1])
    plt.legend(bin_names)  
    plt.show()

def principal_components(city_attributes, scaled_city, crime_attributes, statistics):
                                                                         # covar(x1, x1) Just represents variance in that attribute
    pca = PCA(n_components = len(scaled_city.columns)) # Covariance matrix ([covar(x1,x1), covar(x1, x2), etc.]). Finding eigenvectors and eigenvalues from this matrix. Eigenvectors are sorted according to eigenvalues. Eigenvalues represents how much variance that eigenvector accounts for. Variance meaning how spread out the points are along that vector. 

    pcs = pca.fit_transform(scaled_city)

    variance = np.cumsum(np.round(pca.explained_variance_ratio_, decimals=3) * 100)
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

def wavelet(scaled_city, crime_attributes):
    wavelet_df = calculate_wavelet_coeff(scaled_city)
    wavelet_df = pd.concat([wavelet_df, crime_attributes[['Bin']]], axis = 1)
    
    return wavelet_df

def infographic(df, crime_start):
    gdf = gpd.read_file("./Data Analysis/shapefiles/States_shapefile.shp")
    gdf.drop(gdf.index[gdf["State_Name"] == "ALASKA"], inplace=True)
    gdf.drop(gdf.index[gdf["State_Name"] == "HAWAII"], inplace=True)
    
    state_totals = pd.DataFrame()
    state_names = []
    totals = []
    
    for name, group in df.groupby("STATE"):
        state_names.append(name.upper())
        total = group.iloc[:, range(crime_start, len(df.columns))].sum(axis=1) # totals in each city
        total = total.sum() # add up totals in each city
        totals.append(total)
    
    state_totals["State_Name"] = state_names
    state_totals["TOTAL"] = totals
    
    gdf = pd.merge(gdf, state_totals, on="State_Name")
    
    color = "YlOrRd"  
    fig, (state_plot, states) = plt.subplots(1, 2, figsize=(15, 5))
    
    gdf.apply(lambda x: states.annotate(text=x["State_Name"], xy=x.geometry.centroid.coords[0], ha='center', fontsize=6, color='grey'),axis=1)
    norm = plt_colors.Normalize(vmin=gdf['TOTAL'].min(), vmax=gdf['TOTAL'].max())
    cbar = plt.cm.ScalarMappable(norm=norm, cmap=color)
    cax = fig.colorbar(cbar, fraction=0.05, pad=0.06)
    cax.set_label("Low to High Crime", loc="center")
    gdf.plot(column='TOTAL', cmap=color, ax=states)
    
    # Showcasing how total crime varies with total population in Californa
    state_df = df.loc[df['STATE'] == "California"]
    state_df["Total"] = state_df.iloc[:, range(crime_start, len(state_df.columns))].sum(axis=1)
    
    average_attr = []
    average_total = []
    for name, group in state_df.groupby("CITY"):
        attr = group["Gini Index"].mean()
        total = group.iloc[:, range(crime_start, len(df.columns))].sum(axis=1) 
        total = total.mean()
        
        average_attr.append(attr)
        average_total.append(total)
    
    bar_df = pd.DataFrame()
    bar_df["Attr"] = average_attr
    bar_df["Total"] = average_total
    
    bar_df["Bin"] = pd.cut(bar_df["Attr"], bins=6)
    bin_names = []
    heights = []
    for name, group in bar_df.groupby("Bin"):
        mean = group["Total"].mean()
        if not isnan(mean):
            heights.append(group["Total"].mean())
            bin_names.append(str(name))
    
    state_plot.set_title("Gini Index vs Crime in California")
    state_plot.set_xlabel("Gini Index Bins")
    state_plot.set_ylabel("Average Crime Totals")
    
    state_plot.bar(bin_names, heights)
    plt.show()
    
def visualize(df, crime_start, bin_names, colors):
    attributes = pd.DataFrame()
    
    tot_pop = []
    households = []
    tot_crime = []
    for name, group in df.groupby("CITY"):
        tot_pop.append(group["Total Population"].mean())
        households.append(group["Households"].mean())
        crime = group.iloc[:, range(crime_start, len(df.columns))].sum(axis=1)
        tot_crime.append(crime.mean())
        
    attributes["Total Population"] = tot_pop
    attributes["Households"] = households
    attributes["Total Crime"] = tot_crime
    attributes["Bin"] = pd.qcut(attributes["Total Crime"], [0, .33, .66, 1], labels=bin_names)
    
    columns = ["Median", "Mean", "STD"]
    rows = ["Total Population", "Households", "Total Crime"]
    
    values = []
    for row in rows:
        row_val = []
        for col in columns:
            if col == "Median":
                val = attributes[row].median()
            elif col == "Mean":
                val = attributes[row].mean()
            elif col == "STD":
                
                val = attributes[row].std()
            else:
                val = "-"
            row_val.append(val)
        values.append(row_val)
    
    fig, (table, scatter) = plt.subplots(2)
    fig.patch.set_visible(False)
    table.axis('off')
    table.axis('tight')
    
    table.table(cellText=values, rowLabels=rows, colLabels=columns, loc="center")
    fig.tight_layout()
    
    print(attributes)
    attributes.drop("Total Crime", inplace=True, axis=1) # dropping to plot
    plot_reduced(attributes, bin_names, colors, ["Total Population", "Households"], "Total Population vs. Households")
    plt.show()    

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
    crime_attributes["Bin"] = pd.qcut(crime_attributes["Total"], [0, .33, .66, 1], labels=bin_names) 
    
    pc_df = principal_components(city_attributes, scaled_city, crime_attributes, stats) # need city attributes for debug purposes
    
    plot_reduced(pc_df, bin_names, colors, ["pc 1", "pc 2"], "Principal Components")  # So for each row the city attribs can now be reduced down to just these two components. Plotting each city according to these two components in this new basis(Years has no effect, so essentilly plotting the same cities at different years). Not using the city names to identify each point instead binning crime in each city and color coding to see if there are clusters of cities with similar crime. For ex. L.A, 12000(tot pop), 5000(# males), High -> L.A, -2, -3, High. Point at -2, -3 is identified by high crime instead of city name
    
    # wavelet_df = wavelet(scaled_city, crime_attributes)
    # plot_reduced(wavelet_df, bin_names, colors, ["Approximations", "Details"])
    
    infographic(df, crime_start)
    visualize(df, crime_start, bin_names, colors)