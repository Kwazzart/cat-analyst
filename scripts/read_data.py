import pandas as pd

def read_data():

    with open('D:/pet-projects/cat-analyst/id.txt', "r") as file:
        ID = file.read()
    
    data = pd.read_csv(f"D:/pet-projects/cat-analyst/data/inputs/D{ID}.csv")
    return data