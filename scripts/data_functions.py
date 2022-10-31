import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
import numpy as np
import Constants as C
import scipy.stats as stats
import df2img
import ast
from optuna import create_study

from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor, plot_tree
from sklearn.metrics import mean_absolute_error, mean_squared_error, accuracy_score, classification_report
from sklearn.model_selection import KFold, cross_val_score
from sklearn.preprocessing import MinMaxScaler

img_url = f"{C.DATA_URL}/cat-analyst/data/img"
prepdata_url = f"{C.DATA_URL}/cat-analyst/data/prep_data"
input_url = f"{C.DATA_URL}/cat-analyst/data/inputs"
button_text = 122121218821827178

pd.set_option('display.float_format', lambda x: '%.3f' % x)

def read_data(ID):
    data = pd.read_csv(f"{C.DATA_URL}/cat-analyst/data/inputs/D{ID}.csv", index_col=False)
    return data

def get_data_variables(data, ID):
    data = data.copy()
    n_nan = data.isna().sum().sum()

    for col in data.columns:
        data[col] = data[col].fillna(data[col].mode()[0])

    n_samples, n_features = data.shape
    cat_features = []
    num_features = []
    bin_features = []

    for col in data.columns:
        if data[col].dtypes == "O" or data[col].nunique()==2:
            cat_features.append(col)
            if data[col].nunique()==2:
                bin_features.append(col)
        else:
            num_features.append(col)

    n_bin_features = len(bin_features)
    n_cat_features = len(cat_features)
    n_num_features = len(num_features)

    var_dict = {"n_samples":n_samples, "n_features":n_features,
    "cat_features":cat_features, "n_cat_features":n_cat_features,
    "num_features":num_features, "n_num_features":n_num_features,
    "bin_features":bin_features, "n_bin_features":n_bin_features, "n_nan":n_nan}

    with open(f"{C.DATA_URL}/cat-analyst/data/prep_data/data_vars{ID}.txt", "w") as file:
        file.write(str(var_dict))

    return var_dict

def auto_preproccecing(data, data_vars, ID):
    data = data.copy()
    isna_df = data.isna().sum()/len(data)
    na_features_to_drop = isna_df[isna_df >= 0.7].index.values
    
    #imputation
    for feature in data_vars["cat_features"]:
        data[feature] = data[feature].fillna(data[feature].mode()[0])
    for feature in data_vars["num_features"]:
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
            #data = data.drop([feature], axis=1)
    skew_df["skew_new"] = stats.skew(data.select_dtypes(np.number))
    rows_before = data.shape[0]
    rows_after = data.shape[0]

    """ rows_before = data.shape[0]
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
        data = data.drop(data[data[feature] < (q1 - 2.5 * iqr)].index)
        data = data.drop(data[data[feature] > (q3 + 2.5 * iqr)].index)
    rows_after = data.shape[0] """

    skew_df.to_csv(f"{C.DATA_URL}/cat-analyst/data/prep_data/skew_df{ID}.csv")
    data.to_csv(f"{C.DATA_URL}/cat-analyst/data/prep_data/D{ID}.csv")

    return data, na_features_to_drop, many_unique_values_features_to_drop, rows_before, rows_after, data_vars["cat_features"], data_vars["num_features"], data_vars["bin_features"]

def get_twov(data, ID, bf):
    data = data.copy()
    f1 = data[bf].unique()[0]
    f2 = data[bf].unique()[1]
    df1 = data[data[bf]==f1]
    df2 = data[data[bf]==f2]
    
    with open(f"{C.DATA_URL}/cat-analyst/data/prep_data/data_vars{ID}.txt", "r") as file:
        data_vars = ast.literal_eval(file.read())
    num_features = data_vars["num_features"]
    
    twov_df = pd.DataFrame({"Features":num_features}).set_index("Features")
    text_output = {}
    
    for col in num_features:
        if stats.shapiro(data[col])[1] > 0.05:
            value, p_val = stats.ttest_ind(df1[col], df2[col])
            value, p_val = np.round(value, 4), np.round(p_val, 4)
            twov_df.loc[col, "Two-Sided p-value"] = "test_value: " + str(value) + "-" + "p_val: " + str(p_val)
            
            value, p_val = stats.ttest_ind(df1[col], df2[col], alternative="greater")
            value, p_val = np.round(value, 4), np.round(p_val, 4)
            twov_df.loc[col, f"{f1} greater {f2} p-value"] = "test_value: " + str(value) + "-" + "p_val: " + str(p_val)
            
            value, p_val = stats.ttest_ind(df1[col], df2[col], alternative="less")
            value, p_val = np.round(value, 4), np.round(p_val, 4)
            twov_df.loc[col, f"{f1} less {f2} p-value"] = "test_value: " + str(value) + "-" + "p_val: " + str(p_val)
            text_output[col] = "t-test"
            
        else:
            value, p_val = stats.mannwhitneyu(df1[col], df2[col])
            value, p_val = np.round(value, 4), np.round(p_val, 4)
            twov_df.loc[col, "Two-Sided p-value"] = "test_value: " + str(value) + "-" + "p_val: " + str(p_val)
            
            value, p_val = stats.mannwhitneyu(df1[col], df2[col], alternative="greater")
            value, p_val = np.round(value, 4), np.round(p_val, 4)
            twov_df.loc[col, f"{f1} greater {f2} p-value"] = "test_value: " + str(value) + "-" + "p_val: " + str(p_val)
            
            value, p_val = stats.mannwhitneyu(df1[col], df2[col], alternative="less")
            value, p_val = np.round(value, 4), np.round(p_val, 4)
            twov_df.loc[col, f"{f1} less {f2} p-value"] = "test_value: " + str(value) + "-" + "p_val: " + str(p_val)
            text_output[col] = "mannwhitneyu"
    
    twov_df = twov_df.round(4)
    
    ax = plt.subplot(111, frame_on=False) 
    ax.xaxis.set_visible(False)  
    ax.yaxis.set_visible(False)
    pd.plotting.table(ax, twov_df)
    plt.savefig(f"{C.DATA_URL}/cat-analyst/data/img/twov{ID}.png")
    
    twov_df.to_csv(f"{C.DATA_URL}/cat-analyst/data/prep_data/twov{ID}.csv")
    
    return text_output
    
def get_ttest(data, ID, bf):
    data = data.copy()
    f1 = data[bf].unique()[0]
    f2 = data[bf].unique()[1]
    df1 = data[data[bf]==f1]
    df2 = data[data[bf]==f2]
    
    with open(f"{C.DATA_URL}/cat-analyst/data/prep_data/data_vars{ID}.txt", "r") as file:
        data_vars = ast.literal_eval(file.read())
    num_features = data_vars["num_features"]
    
    twov_df = pd.DataFrame({"Features":num_features}).set_index("Features")
    
    for col in num_features:
        value, p_val = stats.ttest_ind(df1[col], df2[col])
        value, p_val = np.round(value, 4), np.round(p_val, 4)
        twov_df.loc[col, "Two-Sided p-value"] = "test_value: " + str(value) + "-" + "p_val: " + str(p_val)
        
        value, p_val = stats.ttest_ind(df1[col], df2[col], alternative="greater")
        value, p_val = np.round(value, 4), np.round(p_val, 4)
        twov_df.loc[col, f"{f1} greater {f2} p-value"] = "test_value: " + str(value) + "-" + "p_val: " + str(p_val)
        
        value, p_val = stats.ttest_ind(df1[col], df2[col], alternative="less")
        value, p_val = np.round(value, 4), np.round(p_val, 4)
        twov_df.loc[col, f"{f1} less {f2} p-value"] = "test_value: " + str(value) + "-" + "p_val: " + str(p_val)
    
    twov_df = twov_df.round(4)
    
    ax = plt.subplot(111, frame_on=False) 
    ax.xaxis.set_visible(False)  
    ax.yaxis.set_visible(False)
    pd.plotting.table(ax, twov_df)
    plt.savefig(f"{C.DATA_URL}/cat-analyst/data/img/twov{ID}.png")
    
    twov_df.to_csv(f"{C.DATA_URL}/cat-analyst/data/prep_data/twov{ID}.csv")
    
def get_manna(data, ID, bf):
    data = data.copy()
    f1 = data[bf].unique()[0]
    f2 = data[bf].unique()[1]
    df1 = data[data[bf]==f1]
    df2 = data[data[bf]==f2]
    
    with open(f"{C.DATA_URL}/cat-analyst/data/prep_data/data_vars{ID}.txt", "r") as file:
        data_vars = ast.literal_eval(file.read())
    num_features = data_vars["num_features"]
    
    twov_df = pd.DataFrame({"Features":num_features}).set_index("Features")
    
    for col in num_features:
        value, p_val = stats.mannwhitneyu(df1[col], df2[col])
        value, p_val = np.round(value, 4), np.round(p_val, 4)
        twov_df.loc[col, "Two-Sided p-value"] = "test_value: " + str(value) + "-" + "p_val: " + str(p_val)
        
        value, p_val = stats.mannwhitneyu(df1[col], df2[col], alternative="greater")
        value, p_val = np.round(value, 4), np.round(p_val, 4)
        twov_df.loc[col, f"{f1} greater {f2} p-value"] = "test_value: " + str(value) + "-" + "p_val: " + str(p_val)
        
        value, p_val = stats.mannwhitneyu(df1[col], df2[col], alternative="less")
        value, p_val = np.round(value, 4), np.round(p_val, 4)
        twov_df.loc[col, f"{f1} less {f2} p-value"] = "test_value: " + str(value) + "-" + "p_val: " + str(p_val)
    
    twov_df = twov_df.round(4)
    
    ax = plt.subplot(111, frame_on=False) 
    ax.xaxis.set_visible(False)  
    ax.yaxis.set_visible(False)
    pd.plotting.table(ax, twov_df)
    plt.savefig(f"{C.DATA_URL}/cat-analyst/data/img/twov{ID}.png")
    
    twov_df.to_csv(f"{C.DATA_URL}/cat-analyst/data/prep_data/twov{ID}.csv")

def get_corr_pearson(data, data_vars, ID):
    data = data.copy()
    
    with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
    
    corr = data[data_vars["num_features"]].corr()
    corr = corr.round(4)
    
    cols = data[data_vars["num_features"]].columns.array
    pval_df = pd.DataFrame()
    for col1 in cols:
        for col2 in cols:
            _, p_val = stats.pearsonr(data[col1], data[col2])
            pval_df.loc[col1, col2] = p_val
    pval_df = pval_df.round(4)
    
    plt.clf()
    fig_corr = sns.heatmap(corr, annot=True, center=True)
    fig = fig_corr.get_figure()
    
    fig.savefig(f"{C.DATA_URL}/cat-analyst/data/img/snscorr{ID}.png")
    corr.to_csv(f"{C.DATA_URL}/cat-analyst/data/prep_data/corr{ID}.csv")
    pval_df.to_csv(f"{C.DATA_URL}/cat-analyst/data/prep_data/p_val{ID}.csv")

def get_corr_spearman(data, data_vars, ID):
    data = data.copy()
    
    with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
    
    corr = data[data_vars["num_features"]].corr(method = "spearman")
    corr = corr.round(4)
    
    cols = data[data_vars["num_features"]].columns.array
    pval_df = pd.DataFrame()
    for col1 in cols:
        for col2 in cols:
            _, p_val = stats.spearmanr(data[col1], data[col2])
            pval_df.loc[col1, col2] = p_val
    pval_df = pval_df.round(4)
    
    plt.clf()
    fig_corr = sns.heatmap(corr, annot=True, center=True)
    fig = fig_corr.get_figure()
    
    fig.savefig(f"{C.DATA_URL}/cat-analyst/data/img/snscorr{ID}.png")
    corr.to_csv(f"{C.DATA_URL}/cat-analyst/data/prep_data/corr{ID}.csv")
    pval_df.to_csv(f"{C.DATA_URL}/cat-analyst/data/prep_data/p_val{ID}.csv")

def get_corr_auto(data, data_vars, ID):
    data = data.copy()
    N = len(data)
    
    with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
    
    corr = data[data_vars["num_features"]].corr()
    corr = corr.round(4)
    
    cols = data[data_vars["num_features"]].columns.array
    pval_df = pd.DataFrame()
    text_corr_return = {}
    seen_pairs = set()
    for col1 in cols:
        for col2 in cols:
            _, pn1 = stats.shapiro(data[col1])
            _, pn2 = stats.shapiro(data[col2])
            if (pn1 > 0.05) and (pn2 > 0.05) or (N > 2000):
                _, p_val = stats.pearsonr(data[col1], data[col2])
                print(pn1, pn2)
                if ((col1, col2) not in seen_pairs) and ((col2, col1) not in seen_pairs) and (col1 != col2):
                    text_corr_return[f"{col1}---{col2}"] = "pearson"
                    seen_pairs.add((col1, col2))
            else:
                _, p_val = stats.spearmanr(data[col1], data[col2])  
                if ((col1, col2) not in seen_pairs) and ((col2, col1) not in seen_pairs) and (col1 != col2): 
                    text_corr_return[f"{col1}---{col2}"] = "spearman"
                    seen_pairs.add((col1, col2)) 
                       
            pval_df.loc[col1, col2] = p_val
            
    pval_df = pval_df.round(4)
    
    plt.clf()
    fig_corr = sns.heatmap(corr, annot=True, center=True)
    fig = fig_corr.get_figure()
    
    fig.savefig(f"{C.DATA_URL}/cat-analyst/data/img/snscorr{ID}.png")
    corr.to_csv(f"{C.DATA_URL}/cat-analyst/data/prep_data/corr{ID}.csv")
    pval_df.to_csv(f"{C.DATA_URL}/cat-analyst/data/prep_data/p_val{ID}.csv")
    
    return text_corr_return
    
def get_tree_regression(data, ID, target):
    data = data.copy()
    train = data.loc[~data[target].isna(), :]
    #test = data.loc[data[target].isna(), :]
    
    with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
    
    target_df = train[target]
    X_TRAIN = train.drop(target, axis=1)
    #X_TEST = test.drop(target, axis=1)
    num_features = data_vars["num_features"]
    num_features = num_features.copy()
    num_features.remove(target)
    X_TRAIN = pd.concat([X_TRAIN[num_features], pd.get_dummies(X_TRAIN[num_features])], axis=1)
    #X_TEST = pd.concat([X_TEST[num_features], pd.get_dummies(X_TEST[num_features])], axis=1)
    
    kf = KFold(n_splits=10)
    
    def objective(trial):
        params = {"criterion": trial.suggest_categorical("criterion",['squared_error', 'absolute_error']),
                 # "max_features": trial.suggest_categorical("max_features",['auto', 'sqrt', 'log2']),
                  "max_depth": trial.suggest_int("max_depth", 2,14),
                  "min_samples_split": trial.suggest_int("min_samples_split",2,12),
                  "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1,12),}
        tree = DecisionTreeRegressor(**params)
        tree.fit(X_TRAIN, target_df)
        score = -(cross_val_score(tree, X_TRAIN, target_df, scoring="neg_mean_squared_error")).mean()
        return score
    
    tree_study = create_study(direction="minimize")
    tree_study.optimize(objective, n_trials=40)
    
    best_model = DecisionTreeRegressor(**tree_study.best_params)
    best_model.fit(X_TRAIN, target_df)
    best_score = tree_study.best_trial
    #prediction = best_model.predict(X_TEST)
    plot_tree(best_model)
    plt.savefig(f"{C.DATA_URL}/cat-analyst/data/img/reg{ID}.png")
    return best_score

def descriptive(data, ID): 
    data = data.copy()
    data_d = data.describe().round(3)
    v=1
    for i in range(0, data_d.shape[1], 9):
        plt.clf()
        fig_descriptive = df2img.plot_dataframe(
        data_d.iloc[:, i:i+9],
        title=dict(
                font_color="black",
                font_family="Times New Roman",
                font_size=16,
                text=f"Описательная статистика количественных признаков {str(v*(data_d.shape[1]>9)).replace('0', ' ')}",
            ),
            tbl_header=dict(
                align="right",
                fill_color="pink",
                font_color="black",
                font_size=10,
                line_color="black",
            ),
            tbl_cells=dict(
                align="right",
                line_color="black",
            ),
            row_fill_color=("#ffffff", "#ffffff"),
            fig_size=(data_d.iloc[:, i:i+9].shape[1]*120, 300),
        )
        fig_descriptive.write_image(file=f"{C.DATA_URL}/cat-analyst/data/img/descriptive{v}_{ID}.png", format='png')
        v+=1






    
    
    
