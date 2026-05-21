import pandas as pd
from pathlib import Path

DATA_FILE = "hog_settlements.xlsx"

def load_data():
    data_file = Path(DATA_FILE)
    if not data_file.is_file():
        raise FileNotFoundError("Data file '{0}' not found. Please place it in the project root.".format(DATA_FILE))
    print("Loading data from '{0}'...".format(DATA_FILE))
    df = pd.read_excel(DATA_FILE, index_col=0)
    return df
