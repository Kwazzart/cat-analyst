import pandas as pd
import numpy as np
import Constants
import scipy.stats as stats

def read_data(ID):
    data = pd.read_csv(f"{Constants.DATA_URL}/cat-analyst/data/inputs/D{ID}.csv", index_col=0)
    return data

def get_data_variables(data):
    n_samples, n_features = data.shape
    cat_features = list(data.select_dtypes("O").columns.array)
    n_cat_features = len(cat_features)
    num_features = list(data.select_dtypes(np.number).columns.array)
    n_num_features = len(num_features)
    n_nan = data.isna().sum().sum()
    
    var_dict = {"n_samples":n_samples, "n_features":n_features,
            "cat_features":" ".join(cat_features), "n_cat_features":n_cat_features,
            "num_features":" ".join(num_features), "n_num_features":n_num_features, "n_nan":n_nan}
    
    return var_dict

def auto_preproccecing(data):
    data = data.copy()
    isna_df = data.isna().sum()/len(data)
    na_features_to_drop = isna_df[isna_df >= 0.7].index.values
    
    cat_features = data.select_dtypes("O").columns.array
    num_features = data.select_dtypes(np.number).columns.array
    
    for feature in cat_features:
        data[feature] = data[feature].fillna(data[feature].mode()[0])
    for feature in num_features:
        data[feature] = data[feature].fillna(data[feature].median())
        
    nunique_df = pd.DataFrame()
    for feature in data.drop(na_features_to_drop, axis=1).select_dtypes("O").columns.values:
        nunique_df.loc[feature, "n_unique"] = data[feature].nunique()
    
    many_unique_values_features_to_drop = nunique_df.loc[nunique_df["n_unique"] > 30, "n_unique"].index.values
    
    data = data.drop(na_features_to_drop, axis=1)
    data = data.drop(many_unique_values_features_to_drop, axis = 1)
    
    skew_df = pd.DataFrame({"features":data.select_dtypes(np.number).columns.values}).set_index("features")
    skew_df["skew"] = stats.skew(data.select_dtypes(np.number))
    for feature in skew_df.loc[np.abs(skew_df["skew"]) > 1.5].index.values:
        if data[feature].min() >= 0:
            data[feature] = np.log1p(data[feature])
    skew_df["skew_new"] = stats.skew(data.select_dtypes(np.number))
    Constants.SKEW_DF = skew_df
    return data
    
    
