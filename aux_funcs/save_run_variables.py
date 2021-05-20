from datetime import date
import pandas as pd
from Vars.var_funcs import *
from os import path
import pickle as pk
import ast

# # USUÁRIO
USUARIO = "RODRIGO"

# # Lendo arquivo com paths
path_atual = os.getcwd()
arquivo_path = open('set_path.py', 'r')
ler_arquivo = arquivo_path.read()
dicionario = ast.literal_eval(ler_arquivo)
path_drive = dicionario[USUARIO]


def save_run_variable(termo_de_busca, func_name, min_df=0.001, max_features=10000, run_id=""):

    # min_df --> minimum TF-IDF value to keep in DataFrame
    # max_features --> max number of variables

    # Getting today's date
    data = str(date.today())

    # Running var function with eval
    df10,df90 = eval(func_name)(termo_de_busca, min_df, max_features, run_id)

    # Pickle with preproc info
    info = {"termo_buscado": termo_de_busca,
            "preproc": run_id,
            "min_df": min_df,
            "max_features": max_features}

    # Verificando existencia da pasta de path
    path_pasta = f"{path_drive}/Variables/{termo_de_busca.capitalize()}"
    if not path.isdir(path_pasta):
        os.mkdir(path_pasta)

    # Checando se arquivo já existe para determinar o run id
    for i in range(0, 1000):
        path_pickle = f'{path_pasta}/info_{func_name}_{termo_de_busca.lower()}_{data}_{i}.pickle'
        if not path.exists(path_pickle):
            df10.to_parquet(f'{path_pasta}/{func_name}_{termo_de_busca.lower()}_10_{data}_{i}.parquet')
            df90.to_parquet(f'{path_pasta}/{func_name}_{termo_de_busca.lower()}_90_{data}_{i}.parquet')
            info["variable"] = [f'{func_name}_{termo_de_busca.lower()}_10_{data}_{i}', f'{func_name}_{termo_de_busca.lower()}_90_{data}_{i}']
            with open(f'{path_pasta}/info_{func_name}_{termo_de_busca.lower()}_{data}_{i}.pickle', 'wb') as file:
                pk.dump(info, file)
            break

    print("Arquivo salvo e processo finalizado.")

#save_run_variable(termo_de_busca="Bolsonaro", func_name="var_tfidf", run_id="Bolsonaro_2021-05-10_0.csv")  # # EXEMPLO
