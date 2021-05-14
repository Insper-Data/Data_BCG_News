from datetime import date
from numpy import nan
import pandas as pd
from Preproc.funcs_preproc import *
from os import path
import os
import ast
from tqdm import tqdm

# # USUÁRIO
USUARIO = "MAX"

# # Lendo arquivo com paths
path_atual = os.getcwd()
arquivo_path = open('set_path.py', 'r')
ler_arquivo = arquivo_path.read()
dicionario = ast.literal_eval(ler_arquivo)
path_drive = dicionario[USUARIO]

def save_run_preproc(tema="", drop_punct=False, strip_accents=False, drop_stopwords=False, stem_and_lem=False, clean_text=True):
    df = pd.read_csv(path_drive + "/Raw/Values/index.csv", index_col=0)
    df = df[df['unique_identifier'].str.contains(tema)]
    coluna_run_id = list(df.unique_identifier)
    lista_artigo_limpo = []
    for index_run_id in tqdm(range(len(coluna_run_id))):
        text_file = f'{path_drive}/Raw/data/{coluna_run_id[index_run_id]}.txt'
        with open(text_file, 'r') as text:
            texto = text.read()
        if len(texto) < 4:
            lista_artigo_limpo.append(nan)
        elif bool(re.search(tema, texto)) == False:
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
    df = df.dropna()

    # Checando se arquivo já existe para determinar o run id
    for i in range(0, 1000):
        path_file = f'{path_drive}/Preproc/{tema}_{data_do_dia}_{i}.csv'
        if not path.exists(path_file):
            df.to_csv(f'{path_drive}/Preproc/{tema}_{data_do_dia}_{i}.csv')
            break

# save_run_preproc(tema="Bolsonaro")  # # Exemplo -> Sem mais parâmetros pega clean_text como default = Faz tudo
