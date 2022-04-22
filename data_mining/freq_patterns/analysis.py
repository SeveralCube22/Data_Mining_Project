import sys
from os.path import abspath
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
    df.drop(crime_attributes.columns, axis=1, inplace=True)
    
    
    df.drop(range(crime_start, len(df.columns) - 1), inplace=True) # drop all crime attributes
    df = create_binned_df(df)
    print(df)
    data = [to_set(item) for (_,item) in df.iterrows()]
    freq_itemsets = patterns.apriori(data, .8, constraints=["Total Crime Low", "Total Crime Medium", "Total Crime High"])
   
    testcases.show_itemsets(freq_itemsets)
    rules = patterns.association_rules(data, freq_itemsets, "cosine", .996)
    print("----------RULES-------------------")
    testcases.show_rules(rules)
    
def create_binned_df(df):
    exclude_cols = ["STATE", "YEAR", "CITY"]
    df = df.drop(exclude_cols, axis=1)
    
    binned_df = pd.DataFrame()
    labels = ["Low", "Medium", "High"]
    
    for col_name, _ in df.iteritems():
        col_labels = [col_name + " " + label for label in labels]
        binned_df[col_name] = pd.cut(df[col_name], bins=3, labels=col_labels)
    
    return binned_df

def to_set(row):
    result = set()
    for x in row:
        result.add(x)
    return result
    
if __name__ == "__main__":
    main()