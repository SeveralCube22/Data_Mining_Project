from ast import pattern
from copyreg import remove_extension
from distutils.command.clean import clean
import enum
import sys
from os.path import abspath
from xml.etree.ElementInclude import include
import pandas as pd
import patterns
import testcases

def main():
    sys.path.append(abspath("./data_mining/data_analysis"))
    import data_analysis
    df = data_analysis.data_clean()
    
    crime_start = df.columns.get_loc("aggravated-assault")
    crime_attributes = df.iloc[:, range(crime_start, len(df.columns))]
    
    df["Total Crime"] =  crime_attributes.iloc[:, range(len(crime_attributes.columns))].sum(axis=1)
    total_df = df
    total_df = df.drop(crime_attributes.columns, axis=1) # drop all crime attributes except total crime
    
    total_df = create_binned_df(total_df)
    print(total_df)
    print(total_df["Total Crime"].value_counts())
    
    categories = list(total_df["Total Crime"].cat.categories)
    pattern_mine(total_df, "Total Crime", .18, "kulczynski", .5, constraints=categories, exclude={"NULL"}, consequents=categories)
    
    categories = ["Total Crime Low"]
    pattern_mine(total_df, "Total Crime Low", .14, "kulczynski", .4, constraints=categories, exclude={"NULL"}, consequents=categories)
    
    categories = ["Total Crime Medium"]
    pattern_mine(total_df, "Total Crime Medium", .14, "kulczynski", .4, constraints=categories, exclude={"NULL"}, consequents=categories)
   
    all_crime_df = df.drop("Total Crime", axis=1)
    all_crime_df = create_binned_df(all_crime_df)
    
    categories = []
    for crime in crime_attributes.columns:
        categories += list(all_crime_df[crime].cat.categories)
        
    categories = [cat for cat in categories if cat != "NULL"]
    
    pattern_mine(all_crime_df, "ALL Crime", .2, "cosine", .5, constraints=categories, exclude={"NULL"}, consequents=categories)

def pattern_mine(df, title, support, metric, metric_threshold, constraints=None, exclude=None, antecedents=None, consequents=None):
    data = [to_set(item) for _, item in df.iterrows()]
    freq_itemsets = patterns.apriori(data, support, constraints=constraints, exclude=exclude)
    
    print("-----Freq Itemsets {}-----".format(title))
    testcases.show_itemsets(freq_itemsets)
    rules = patterns.association_rules(data, freq_itemsets, metric, metric_threshold, antecedents=None, consequents=consequents)
    print("-----RULES {}-----".format(title))
    testcases.show_rules(rules)
       
def create_binned_df(df):
    exclude_cols = ["STATE", "YEAR", "CITY"]
    df = df.drop(exclude_cols, axis=1)
    
    binned_df = pd.DataFrame()
    labels = ["Low", "Medium", "High"]
    
    for col_name, _ in df.iteritems():
        col_labels = ["NULL"] + [col_name + " " + label for label in labels]
        
        quantiles = df[col_name].quantile([0.33, .66, 1])
        cleaned_q = []
        
        remove_label = 1 # start at LOW
        exclude = {}
        for k, val in quantiles.items():
            if val == -1:
                del col_labels[remove_label]
                exclude[k] = 1
                remove_label += 1
        
        for k, _ in quantiles.items():
            if k not in exclude:
                cleaned_q += [quantiles[k]]
        
        cleaned_q = [-1, 0] + cleaned_q
            
        for (i, q) in enumerate(cleaned_q):
            if i < len(cleaned_q) - 1 and q == cleaned_q[i + 1]:
                cleaned_q[i + 1] = q + 1
                
        binned_df[col_name] = pd.cut(df[col_name], bins=cleaned_q, labels=col_labels)
        binned_df[col_name].fillna(col_labels[0], inplace=True)
    
    return binned_df

def to_set(row):
    result = set()
    for x in row:
        result.add(x)
    return result
    
if __name__ == "__main__":
    main()