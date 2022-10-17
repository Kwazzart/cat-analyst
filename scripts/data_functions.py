import pandas as pd
import numpy as np
import Constants

def read_data(ID):
    
    data = pd.read_csv(f"{Constants.DATA_URL}/cat-analyst/data/inputs/D{ID}.csv")
    return data

def get_data_variables(data):
    n_samples, n_features = data.shape
    cat_features = list(data.select_dtypes("O").columns.array)
    n_cat_features = len(cat_features)
    num_features = list(data.select_dtypes(np.number).columns.array)
    n_num_features = len(num_features)
    
    var_dict = {"n_samples":n_samples, "n_features":n_features,
            "cat_features":" ".join(cat_features), "n_cat_features":n_cat_features,
            "num_features":" ".join(num_features), "n_num_features":n_num_features}
    print(var_dict)
    return var_dict
    
