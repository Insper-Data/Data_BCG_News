from datetime import date
from numpy import nan
import pandas as pd
from Preproc.funcs_preproc import *
from os import path
import os
import ast
from tqdm import tqdm
import pickle as pk

# # USUÁRIO
USUARIO = "RODRIGO"

# # Lendo arquivo com paths
path_atual = os.getcwd()
arquivo_path = open('set_path.py', 'r')
ler_arquivo = arquivo_path.read()
dicionario = ast.literal_eval(ler_arquivo)
path_drive = dicionario[USUARIO]
path_preproc = os.path.abspath(f"{path_drive}/Preproc")

# # Lendo dicionário Léxico
df_lexicon = pd.read_csv(os.path.abspath(f"{path_preproc}/Lexicon/oplexicon_v3.csv"))

def save_run_preproc(tema="", drop_punct=False, strip_accents=False, drop_stopwords=False, stem_and_lem=False, clean_text=True, polaridade=True):
    df = pd.read_csv(os.path.abspath(path_drive + "/Raw/Values/index.csv"), index_col=0)
    df = df[df['unique_identifier'].str.contains(tema)]
    path_pickle = os.path.abspath(f'{path_drive}/Preproc/dic_stemm_{tema}.pickle')
    coluna_run_id = list(df.unique_identifier)
    lista_artigo_limpo = []
    lista_artigo_original = []
    lista_polaridade = []
    dic_stemm = {}
    dic_final = {}
    for index_run_id in tqdm(range(len(coluna_run_id))):
        text_file = os.path.abspath(f'{path_drive}/Raw/data/{coluna_run_id[index_run_id]}.txt')
        with open(text_file, 'r') as text:
            texto = text.read()
        if len(texto) < 4:
            lista_artigo_limpo.append(nan)
            lista_artigo_original.append(nan)
        elif bool(re.search(tema, texto)) == False:
            lista_artigo_limpo.append(nan)
            lista_artigo_original.append(nan)
        else:
            try:
                lista_artigo_original.append(texto)
                if drop_punct:
                    texto = remove_punctuation(texto)
                if strip_accents:  # NÃO PODE SER ELIF PQ PRECISA CHECAR TODAS AS CONDIÇÕES!!!
                    texto = remove_accents(texto)
                if drop_stopwords:
                    texto = remove_stopwords(texto)
                if stem_and_lem:
                    texto = stem_and_lemmatize(texto)
                if clean_text:
                    texto, dic_stemm_parcial = clean_text_func(texto)
                lista_artigo_limpo.append(texto)
            except:
                print('HOUVE UM ERRO DURANTE O PRÉ-PROCESSAMENTO')

        for wordStemmatizada, listReverseStemm in dic_stemm_parcial.items():
            if wordStemmatizada not in dic_stemm.keys():
                dic_stemm[wordStemmatizada] = {}

            for wordReverseStemm in listReverseStemm:
                if wordReverseStemm not in dic_stemm[wordStemmatizada].keys():
                    dic_stemm[wordStemmatizada][wordReverseStemm] = 1
                else:
                    dic_stemm[wordStemmatizada][wordReverseStemm] += 1



    for w, dicStemm in dic_stemm.items():
        max_v = 0
        max_k = ""
        for stemm, v in dicStemm.items():
            if v > max_v:
                max_v = v
                max_k = stemm

        dic_final[w] = max_k

    # Adicionando novos valores a um dicionario geral guardado na propria pasta preproc
    with open(path_pickle, "wb") as file:
        pk.dump(dic_final, file)

    df['artigo'] = lista_artigo_limpo
    df["artigo_original"] = lista_artigo_original
    data_do_dia = str(date.today())
    df = df.dropna()

    # Verificando a polaridade dos artigos
    if polaridade:
        for texto in df["artigo_original"]:
            lista_polaridade.append(get_polarity(texto))
        df["sentimento"] = lista_polaridade

    # Checando se arquivo já existe para determinar o run id
    for i in range(0, 1000):
        path_file = os.path.abspath(f'{path_drive}/Preproc/{tema}_{data_do_dia}_{i}.csv')
        if not path.exists(path_file):
            df.to_csv(os.path.abspath(f'{path_drive}/Preproc/{tema}_{data_do_dia}_{i}.csv'))
            break

# save_run_preproc(tema="Bolsonaro")  # # Exemplo -> Sem mais parâmetros pega clean_text como default = Faz tudo