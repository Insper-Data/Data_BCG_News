from datetime import date
from numpy import nan
from oficial import retorna_texto_limpo
import pandas as pd
import os
from Prepoc.prepoc_funcs import *


def save_run_prepoc(path_drive, drop_punct=False, strip_accents=False, drop_stopwords=False, stem_and_lem=False, clean_text=True):
	
    df = pd.read_csv(path_drive + "/Raw/Values/index.csv")
    coluna_run_id = list(df.unique_identifier)
    lista_artigo_limpo = []
    for run_id in coluna_run_id:
        with open(f'{cwd_path}"/Raw/data/"{run_id}.txt', 'r') as text:
            texto = text.read()
        if len(texto) < 4:
            lista_artigo_limpo.append(nan)
        else:
            try:
		if drop_punct:  
			texto = remove_punctuation(texto)
		if strip_accents:  # NÃO PODE SER ELIF PQ PRECISA CHECAR TODAS AS CONDIÇÕES!!!
			texto = strip_accents(texto)
		if drop_stopwords:
			texto = remove_stop_words(texto)
		if stem_and_lem:
			texto = stem_and_lemmatize(texto)
		if clean_text:
                	texto = retorna_texto_limpo(texto)
            except:
                print('HOUVE UM ERRO DURANTE O PRÉ-PROCESSAMENTO')

    df['artigo'] = lista_artigo_limpo
    data_do_dia = date.today()
    df.to_csv(f'{path_drive}/Prepoc/{data_do_dia}.csv')
