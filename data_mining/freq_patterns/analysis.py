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
    df.drop(crime_attributes.columns, axis=1, inplace=True) # drop all crime attributes except total crime
    
    df = create_binned_df(df)
    print(df)
    
    data = [to_set(item) for (_,item) in df.iterrows()]
    freq_itemsets = patterns.apriori(data, .3, constraints=["Total Crime Low", "Total Crime Medium", "Total Crime High"], exclude={"NULL"})
   
    print("-----Freq Itemsets-----")
    testcases.show_itemsets(freq_itemsets)
    rules = patterns.association_rules(data, freq_itemsets, "cosine", .3)
    print("-----RULES-----")
    testcases.show_rules(rules)
    
def create_binned_df(df):
    exclude_cols = ["STATE", "YEAR", "CITY"]
    df = df.drop(exclude_cols, axis=1)
    
    binned_df = pd.DataFrame()
    labels = ["Low", "Medium", "High"]
    
    for col_name, _ in df.iteritems():
        col_labels = ["NULL"] + [col_name + " " + label for label in labels]
        
        quantiles = df[col_name].quantile([0.25, .5, 0.75])
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
                
        binned_df[col_name] = pd.cut(df[col_name], bins=cleaned_q, labels=col_labels, include_lowest=True)
        binned_df[col_name].fillna(col_labels[-1], inplace=True)
    
    return binned_df

def to_set(row):
    result = set()
    for x in row:
        result.add(x)
    return result
    
if __name__ == "__main__":
    main()