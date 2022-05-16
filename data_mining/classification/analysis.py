import random
import sys
from os.path import abspath
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import RandomizedSearchCV
from sklearn.preprocessing import OrdinalEncoder
from classification import DecisionTree
import testcases
from sklearn import metrics

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
    
    x_cols = total_df.columns[:-1]
    y_col = total_df.columns[-1:]
    
    training, validation, testing = split(total_df)
    (train_x, train_y, validation_x, validation_y, test_x, test_y) = get_data(training, validation, testing, x_cols, y_col)
    
    print("DECISION TREE WITHOUT PRUNE")
    decision_tree(train_x, train_y, validation_x, validation_y, test_x, test_y)
    print("DECISION TREE WITH PRUNE")
    decision_tree(train_x, train_y, validation_x, validation_y, test_x, test_y, prune=True)
    
    print("RANDOM TREE BASE")
    important_features = random_forests(train_x, train_y, validation_x, validation_y, test_x, test_y, x_cols)
    important_features = important_features[:30] # use only top 30 most important features
    
    print("RANDOM TREE WITH BEST FEATURES")
    x_cols = important_features.keys()
    (train_x, train_y, validation_x, validation_y, test_x, test_y) = get_data(training, validation, testing, x_cols, y_col)
    random_forests(train_x, train_y, validation_x, validation_y, test_x, test_y, x_cols, n_estimators=2000)

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

def split(df):
    training = []
    validation = []
    testing = []
    
    #random.seed(1337)
    for i,row in df.iterrows():
        if random.random() >= 0.80:
            testing.append(row)
        elif random.random() >= .60:
            validation.append(row)
        else:
            training.append(row)
    
    print("Training: ", len(training) / df.shape[0])
    print("Validation: ", len(validation) / df.shape[0])
    print("Testing: ", len(testing) / df.shape[0])
    print()
    
    
    return training, validation, testing

def get_data(training, validation, testing, x_cols, y_cols):
    train_x, train_y = get_x_y_data(training, x_cols, y_cols)
    validation_x, validation_y = get_x_y_data(validation, x_cols, y_cols)
    test_x, test_y = get_x_y_data(testing, x_cols, y_cols)
    
    return (train_x, train_y, validation_x, validation_y, test_x, test_y)
        
def get_x_y_data(dataset, x_cols, y_cols):
    return testcases.get_columns(dataset, x_cols), testcases.get_columns(dataset, y_cols, single=True)

def calc_precision(y, pred_y):
    return metrics.precision_score(y, pred_y, average="weighted", zero_division=1)

def calc_recall(y, pred_y):
    return metrics.recall_score(y, pred_y, average="weighted", zero_division=1)

def print_model_debug(mssg, y, y_hat):
    testcases.evaluate("{} Accuracy: ".format(mssg), y, y_hat)
    print(mssg, " Precision: ", calc_precision(y, y_hat))
    print(mssg, " Recall: ", calc_recall(y, y_hat))
    print()
    
def decision_tree(train_x, train_y, validation_x, validation_y, test_x, test_y, prune=False, max_depth=None, leaves_to_prune=None):
    classifier = DecisionTree()

    classifier.fit(train_x, train_y)
    print("Height of Tree: ", classifier.calculate_height(classifier.tree))  
    
    train_y_hat = classifier.predict(train_x)
    print_model_debug("Decision Tree Training", train_y, train_y_hat)
    
    print("Initial Leaves: ", classifier.count_leaves(classifier.tree))
    if prune:
        classifier.prune(validation_x, validation_y, num_leaves_to_prune=leaves_to_prune)
        if max_depth != None: classifier.prune_max_depth(max_depth)
        print("Leaves After Prune: ", classifier.count_leaves(classifier.tree))
        print("Height After Prune: ", classifier.calculate_height(classifier.tree))
    
    validation_y_hat = classifier.predict(validation_x)
    print_model_debug("Decision Tree Validation", validation_y, validation_y_hat)
    
    test_y_hat = classifier.predict(test_x)   
    print_model_debug("Decision Tree Testing", test_y, test_y_hat)
    
def random_forests(train_x, train_y, validation_x, validation_y, test_x, test_y, feature_names, n_estimators=100, max_depth=None):

    encoder = OrdinalEncoder()
    xenc = encoder.fit_transform(train_x)
    
    classifier = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth)
    
    classifier.fit(xenc, train_y)
    
    train_y_hat = classifier.predict(encoder.fit_transform(train_x))
    print_model_debug("Random Forests Tree Training", train_y, train_y_hat)
    
    validation_y_hat = classifier.predict(encoder.fit_transform(validation_x))
    print_model_debug("Random Forests Tree Validation", validation_y, validation_y_hat)
    
    test_y_hat = classifier.predict(encoder.fit_transform(test_x))   
    print_model_debug("Random Forests Tree Testing", test_y, test_y_hat)
    
    result = permutation_importance(classifier, encoder.fit_transform(test_x), test_y, n_repeats=10, random_state=42, n_jobs=2)
    
    feature_importances = pd.Series(result.importances_mean, index=feature_names)
    feature_importances.sort_values(ascending=False, inplace=True)
    print(feature_importances.head(30))
    print()
    
    return feature_importances
    
if __name__ == "__main__":
    main()