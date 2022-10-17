import pandas as pd
import Constants

def read_data(ID):
    
    data = pd.read_csv(f"{Constants.DATA_URL}/cat-analyst/data/inputs/D{ID}.csv")
    return data