from datetime import date
import pandas as pd
from Vars.var_funcs import *
from os import path
import pickle as pk
from aux_funcs.set_path import path_drive


def save_run_variable(func_name, min_df=0.001, max_features=10000, run_id=""):

    # min_df --> minimum TF-IDF value to keep in DataFrame
    # max_features --> max number of variables

    # Getting today's date
    data = str(date.today())

    # Running var function with eval
    var_10, var_90 = eval(func_name)(path_drive, min_df, max_features, run_id)

    # Pickle with preproc info
    info = {"preproc": run_id,
            "min_df": min_df,
            "max_features": max_features}

    # Checando se arquivo já existe para determinar o run id
    for i in range(0, 1000):
        path_file_10 = f'{path_drive}/Variables/{func_name}_10_{data}_{i}.csv'
        path_file_90 = f'{path_drive}/Variables/{func_name}_90_{data}_{i}.csv'
        if not path.exists(path_file_10) and not path.exists(path_file_90):
            var_10.to_parquet(f'{path_drive}/Variables/{func_name}_10_{data}_{i}.parquet')
            var_90.to_parquet(f'{path_drive}/Variables/{func_name}_90_{data}_{i}.parquet')
            info["variable"] = [f'{func_name}_10_{data}_{i}', f'{func_name}_90_{data}_{i}']
            with open(f'{path_drive}/Variables/info_{func_name}_{data}_{i}.pickle', 'wb') as file:
                pk.dump(info, file)
            break

    print("Arquivo salvo e processo finalizado.")

# # save_run_variable("teste", "2021-03-05_0")  # # EXEMPLO
