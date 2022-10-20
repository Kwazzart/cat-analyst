import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
import numpy as np
import Constants
import scipy.stats as stats

pd.set_option('display.float_format', lambda x: '%.3f' % x)

def read_data(ID):
    data = pd.read_csv(f"{Constants.DATA_URL}/cat-analyst/data/inputs/D{ID}.csv", index_col=0)
    return data

def get_data_variables(data, ID):
    data = data.copy()
    n_samples, n_features = data.shape
    cat_features = list(data.select_dtypes("O").columns.array)
    n_cat_features = len(cat_features)
    num_features = list(data.select_dtypes(np.number).columns.array)
    n_num_features = len(num_features)
    n_nan = data.isna().sum().sum()
    
    var_dict = {"n_samples":n_samples, "n_features":n_features,
            "cat_features":" ".join(cat_features), "n_cat_features":n_cat_features,
            "num_features":" ".join(num_features), "n_num_features":n_num_features, "n_nan":n_nan}
    
    #with open(f"{Constants.DATA_URL}/cat-analyst/data/prep_data/data_vars{ID}.txt", "r") as file:
    #    file.write(var_dict)
    return var_dict

def auto_preproccecing(data, ID):
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
        nunique_df.loc[feature, "n_unique"] = data[feature].nunique()/len(data)
    
    many_unique_values_features_to_drop = nunique_df.loc[nunique_df["n_unique"] > 0.03, "n_unique"].index.values
    
    data = data.drop(na_features_to_drop, axis = 1)
    data = data.drop(many_unique_values_features_to_drop, axis = 1)
    
    skew_df = pd.DataFrame({"features":data.select_dtypes(np.number).columns.values}).set_index("features")
    skew_df["skew"] = stats.skew(data.select_dtypes(np.number))
    for feature in skew_df.loc[np.abs(skew_df["skew"]) > 1.5].index.values:
        if data[feature].min() >= 0:
            data[feature] = np.log1p(data[feature])
    skew_df["skew_new"] = stats.skew(data.select_dtypes(np.number))
    
    
    
    skew_df.to_csv(f"{Constants.DATA_URL}/cat-analyst/data/prep_data/skew_df{ID}.csv")
    data.to_csv(f"{Constants.DATA_URL}/cat-analyst/data/prep_data/D{ID}.csv")
    
    rows_before = data.shape[0]
    common_mode = []
    for feature in data.select_dtypes(np.number).columns.values:
        moda = data[feature].mode()
        data_n = data[data[feature] == moda.values[0]].shape[0]/data.shape[0] 
        if data_n < 0.5:
                common_mode.append(feature)
    for feature in common_mode:
        q1 = data[feature].quantile(q=0.25)
        q3 = data[feature].quantile(q=0.75)
        iqr = q3-q1
        data = data.drop(data[data[feature] < (q1 - 2.25 * iqr)].index)
        data = data.drop(data[data[feature] > (q3 + 2.25 * iqr)].index)
    rows_after = data.shape[0]

    return data, na_features_to_drop, many_unique_values_features_to_drop, rows_before, rows_after

def get_corr_pearson(data, ID):
    data = data.copy()
    corr = data.select_dtypes(np.number).corr()
    corr = corr.round(4)
    
    cols = data.select_dtypes(np.number).columns.array
    pval_df = pd.DataFrame()
    for col1 in cols:
        for col2 in cols:
            _, p_val = stats.pearsonr(data[col1], data[col2])
            pval_df.loc[col1, col2] = p_val
    pval_df = pval_df.round(4)
    
    plt.clf()
    fig_corr = sns.heatmap(corr, annot=True, center=True)
    fig = fig_corr.get_figure()
    
    fig.savefig(f"{Constants.DATA_URL}/cat-analyst/data/img/snscorr{ID}.png")
    corr.to_csv(f"{Constants.DATA_URL}/cat-analyst/data/prep_data/corr{ID}.csv")
    pval_df.to_csv(f"{Constants.DATA_URL}/cat-analyst/data/prep_data/p_val{ID}.csv")

def get_corr_spearman(data, ID):
    data = data.copy()
    corr = data.select_dtypes(np.number).corr(method = "spearman")
    corr = corr.round(4)
    
    cols = data.select_dtypes(np.number).columns.array
    pval_df = pd.DataFrame()
    for col1 in cols:
        for col2 in cols:
            _, p_val = stats.spearmanr(data[col1], data[col2])
            pval_df.loc[col1, col2] = p_val
    pval_df = pval_df.round(4)
    
    plt.clf()
    fig_corr = sns.heatmap(corr, annot=True, center=True)
    fig = fig_corr.get_figure()
    
    fig.savefig(f"{Constants.DATA_URL}/cat-analyst/data/img/snscorr{ID}.png")
    corr.to_csv(f"{Constants.DATA_URL}/cat-analyst/data/prep_data/corr{ID}.csv")
    pval_df.to_csv(f"{Constants.DATA_URL}/cat-analyst/data/prep_data/p_val{ID}.csv")

def get_corr_auto(data, ID):
    data = data.copy()
    corr = data.select_dtypes(np.number).corr()
    corr = corr.round(4)
    
    cols = data.select_dtypes(np.number).columns.array
    pval_df = pd.DataFrame()
    for col1 in cols:
        for col2 in cols:
            _, p_val = stats.pearsonr(data[col1], data[col2])
            pval_df.loc[col1, col2] = p_val
    pval_df = pval_df.round(4)
    
    plt.clf()
    fig_corr = sns.heatmap(corr, annot=True, center=True)
    fig = fig_corr.get_figure()
    #plt.cla()
    
    fig.savefig(f"{Constants.DATA_URL}/cat-analyst/data/img/snscorr{ID}.png")
    corr.to_csv(f"{Constants.DATA_URL}/cat-analyst/data/prep_data/corr{ID}.csv")
    pval_df.to_csv(f"{Constants.DATA_URL}/cat-analyst/data/prep_data/p_val{ID}.csv")
    
    
    
    
