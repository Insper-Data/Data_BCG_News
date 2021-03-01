from datetime import date
import pandas as pd
from Vars.var_funcs import *


def save_run_variable(path_drive, run_id, func_name):

    df = pd.read_csv(f"{path_drive}/{run_id}.csv")
    data = str(date.today())

    var = eval(func_name)(path_drive, run_id)
    df = df["unique_identifier"].join(var, how="left", on="unique_identifier")

    df.to_csv(f"{path_drive}/Variables/{func_name}_{data}.csv")
