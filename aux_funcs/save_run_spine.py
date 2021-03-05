import pandas as pd
import pickle
from datetime import date
import os
from aux_funcs.set_path import path_drive


def save_run_spine(run_id_list):

    # Getting today's date
    data = str(date.today())

    # Getting paths for variables
    paths_vars = []
    paths_dicts = []
    for var in run_id_list:
        paths_vars.append(f"{path_drive}/Variables/{var}.csv")
        paths_dicts.append(f"{path_drive}/Variables/dict_{var}.pickle")

    # Merging variables
    df_list = []
    for path in paths_vars:
        df_i = pd.read_csv(path, index_col=[0])
        df_list.append(df_i)

    df_list = [df.set_index(["unique_identifier", "sigla", "nome_jornal", "termo_de_busca",
                           "data", "manchete"]) for df in df_list]
    df_spine = pd.concat(df_list, axis=1).reset_index()

    # Saving spine info on list of dictionaries
    spine_info = []
    for i in range(len(paths_dicts)):
        with open(paths_dicts[i], "rb") as f:
            dict_i = pickle.load(f)
            spine_info.append(dict_i)

    # Checando se arquivo já existe para determinar o run id
    for i in range(0, 1000):
        path_file = f'{path_drive}/Spine/spine_{data}_{i}.csv'
        if not os.path.exists(path_file):
            df_spine.to_csv(f'{path_drive}/Spine/spine_{data}_{i}.csv')
            with open(f'{path_drive}/Spine/dict_spine_{data}_{i}.pickle', 'wb') as file:
                pickle.dump(spine_info, file)
            break


# save_run_spine(["blabla_2021-03-05_0", "teste_2021-03-05_9"])  # # EXEMPLO
