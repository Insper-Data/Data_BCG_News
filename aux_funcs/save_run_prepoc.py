from datetime import date
from numpy import nan
import pandas as pd
from Preproc.funcs_prepoc import *
from os import path
from aux_funcs.set_path import path_drive

def save_run_prepoc(drop_punct=False, strip_accents=False, drop_stopwords=False, stem_and_lem=False,
                    clean_text=True):
    df = pd.read_csv(path_drive + "/Raw/Values/index.csv")
    coluna_run_id = list(df.unique_identifier)
    lista_artigo_limpo = []
    for run_id in coluna_run_id:
        with open(f'{path_drive}"/Raw/data/"{run_id}.txt', 'r') as text:
            texto = text.read()
        if len(texto) < 4:
            lista_artigo_limpo.append(nan)
        else:
            try:
                if drop_punct:
                    texto = remove_punctuation(texto)
                if strip_accents:  # NÃO PODE SER ELIF PQ PRECISA CHECAR TODAS AS CONDIÇÕES!!!
                    texto = remove_accents(texto)
                if drop_stopwords:
                    texto = remove_stopwords(texto)
                if stem_and_lem:
                    texto = stem_and_lemmatize(texto)
                if clean_text:
                    texto = clean_text_func(texto)
                lista_artigo_limpo.append(texto)
            except:
                print('HOUVE UM ERRO DURANTE O PRÉ-PROCESSAMENTO')

    df['artigo'] = lista_artigo_limpo
    data_do_dia = str(date.today())
    
    # Checando se arquivo já existe para determinar o run id
    for i in range(0, 1000):
        path_file = f'{path_drive}/Prepoc/{data_do_dia}_{i}.csv'
        if not path.exists(path_file):
            df.to_csv(f'{path_drive}/Prepoc/{data_do_dia}_{i}.csv')
            break
