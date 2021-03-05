import pandas as pd
from aux_funcs.set_path import path_drive

# Funções de criação de variáveis


def teste(run_id):
    df = pd.read_csv(f"{path_drive}/Prepoc/{run_id}.csv")
    df["teste"] = "teste de função"
    return df


def blabla(run_id):
    df = pd.read_csv(f"{path_drive}/Prepoc/{run_id}.csv")
    df["blabla"] = "blabla"
    return df
