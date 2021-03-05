from datetime import date
import pandas as pd
from Vars.var_funcs import *
from os import path
import pickle as pk

def save_run_variable(path_drive, run_id, func_name):

    df = pd.read_csv(f"{path_drive}/{run_id}.csv")
    data = str(date.today())
    var = eval(func_name)(path_drive, run_id)
    df = df["unique_identifier"].join(var, how="left", on="unique_identifier")

    # Pickle with preproc info
    info = {"preproc": run_id}
    

    # Checando se arquivo já existe para determinar o run id
    for i in range(0, 1000):
        path_file = f'{path_drive}/Variables/{func_name}_{data}_{i}.csv'
        if not path.exists(path_file):
            df.to_csv(f'{path_drive}/Variables/{func_name}_{data}_{i}.csv')
            info["variable"] = f'{func_name}_{data}_{i}'
            with open(f'{path_drive}/Variables/dict_{func_name}_{data}_{i}.pickle', 'wb') as file:
                pk.dump(info, file)
            break
