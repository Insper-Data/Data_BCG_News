import pandas as pd
from aux_funcs.set_path import path_drive


# Funções de criação de variáveis
def teste(run_id):
    df = pd.read_csv(f"{path_drive}/Preproc/{run_id}.csv", index_col=0)
    df["teste"] = "teste de função"
    return df


def blabla(run_id):
    df = pd.read_csv(f"{path_drive}/Preproc/{run_id}.csv", index_col=0)
    df["blabla"] = "blabla"
    return df
