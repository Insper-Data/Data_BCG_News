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
path_preproc = f"{path_drive}/Preproc"

# # Lendo dicionário Léxico
df_lexicon = pd.read_csv(f"{path_preproc}/Lexicon/oplexicon_v3.csv")

def save_run_preproc(tema="", drop_punct=False, strip_accents=False, drop_stopwords=False, stem_and_lem=False, clean_text=True, polaridade=True):
    df = pd.read_csv(path_drive + "/Raw/Values/index.csv", index_col=0)
    df = df[df['unique_identifier'].str.contains(tema)]
    path_pickle = f'{path_drive}/Preproc/dic_stemm_{tema}.pickle'
    coluna_run_id = list(df.unique_identifier)
    lista_artigo_limpo = []
    lista_artigo_original = []
    lista_polaridade = []
    dic_stemm = {}
    dic_semifinal = {}
    dic_final = {}
    for index_run_id in tqdm(range(len(coluna_run_id))):
        text_file = f'{path_drive}/Raw/data/{coluna_run_id[index_run_id]}.txt'
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

        # Passando dics parciais de conversão para um dic geral de todos os artigos
        for key, value in dic_stemm_parcial.items():
            if key not in dic_stemm.keys():
                dic_stemm[key] = value
            else:
                dic_stemm[key] += value

        if index_run_id % 10000 == 0 or index_run_id == len(coluna_run_id):
            for key, value in dic_stemm.items():
                dic_parcial = {}
                for v in value:
                    if v in dic_parcial.keys():
                        dic_parcial[v] += 1
                    else:
                        dic_parcial[v] = 1

                if key not in dic_semifinal.keys():
                    dic_semifinal[key] = dic_parcial

                else:
                    for k, v in dic_parcial.items():
                        if k in dic_semifinal[key].keys():
                            dic_semifinal[key][k] += v
                        else:
                            dic_semifinal[key] = {k: v}

            dic_stemm={}

    for key, value in dic_semifinal.items():
        max_v = 0
        max_k = ""
        for k, v in value.items():
            if v > max_v:
                max_v = v
                max_k = k

        dic_final[key] = max_k

    # Adicionando novos valores a um dicionario geral guardado na propria pasta preproc
    if os.path.isfile(path_pickle):
        with open(path_pickle, "rb") as file:
            dic_salvo = pk.load(file)
            for key, value in dic_final.items():
                if key not in dic_salvo:
                    dic_salvo[key] = value

        with open(path_pickle, "wb") as file:
            pk.dump(dic_salvo, file)

    else:
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
        path_file = f'{path_drive}/Preproc/{tema}_{data_do_dia}_{i}.csv'
        if not path.exists(path_file):
            df.to_csv(f'{path_drive}/Preproc/{tema}_{data_do_dia}_{i}.csv')
            break

# save_run_preproc(tema="Bolsonaro")  # # Exemplo -> Sem mais parâmetros pega clean_text como default = Faz tudo