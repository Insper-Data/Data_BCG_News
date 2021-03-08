from datetime import date
import pandas as pd
from Vars.var_funcs import *
from os import path
import pickle as pk
from aux_funcs.set_path import path_drive


def save_run_variable(func_name, run_id=""):

    # Getting today's date
    data = str(date.today())

    # Running var function with eval
    var = eval(func_name)(run_id)

    # Pickle with preproc info
    info = {"preproc": run_id}

    # Checando se arquivo já existe para determinar o run id
    for i in range(0, 1000):
        path_file = f'{path_drive}/Variables/{func_name}_{data}_{i}.csv'
        if not path.exists(path_file):
            var.to_csv(f'{path_drive}/Variables/{func_name}_{data}_{i}.csv')
            info["variable"] = f'{func_name}_{data}_{i}'
            with open(f'{path_drive}/Variables/info_{func_name}_{data}_{i}.pickle', 'wb') as file:
                pk.dump(info, file)
            break


# # save_run_variable("teste", "2021-03-05_0")  # # EXEMPLO
