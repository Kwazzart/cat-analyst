import pandas as pd
import Constants

def read_data():

    with open(f'{Constants.DATA_URL}/cat-analyst/id.txt', "r") as file:
        ID = file.read()
    
    data = pd.read_csv(f"{Constants.DATA_URL}/cat-analyst/data/inputs/D{ID}.csv")
    return data