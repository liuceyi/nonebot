import os 
import pandas as pd

def local_save(fpath:str, fname:str, df: pd.DataFrame):
    if not (os.path.exists(fpath) and os.path.isfile(f'{fpath}/{fname}')):
        os.makedirs(fpath)
    df.to_pickle(f'{fpath}/{fname}')

def local_load(fpath:str, fname:str) -> pd.DataFrame:
    if not (os.path.exists(fpath) and os.path.isfile(f'{fpath}/{fname}')):
        return pd.DataFrame(columns=['server_id', 'channel_id'])

    return pd.read_pickle(f'{fpath}/{fname}')