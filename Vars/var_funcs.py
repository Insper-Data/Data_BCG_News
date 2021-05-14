from aux_funcs.set_path import path_drive
from Vars.aux_funcs_var import *
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import os
from tqdm import tqdm

# Funções de criação de variáveis

def var_tfidf (termo_de_busca, path_drive, min_df, max_features, run_id):
    # Abrindo arquivo
    path = f"{path_drive}/Preproc/"
    arquivos = os.listdir(path)

    # Encontrando mais recente
    if run_id == "":
        arquivo = arquivo_mais_recente(arquivos)

    # Criando e limpando DF (retirnado linhas de artigos vazios)
    df = pd.read_csv(f"{path}{arquivo}", index_col=0)
    df = df[df.termo_de_busca == termo_de_busca.capitalize()]
    if df.empty:
        return "O termo buscado não está na nossa base de dados"
    df.dropna(subset=['artigo'], inplace=True)
    df.reset_index(inplace=True, drop=True)

    # Criando TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(min_df=min_df, max_features=max_features)
    analyze = vectorizer.build_analyzer()

    # Analisando com TF-IDF
    print("Fazendo a análise dos artigos")
    for artigo in df.artigo:
        analyze(artigo)

    print("Criando DataFrame denso")
    variaveis = vectorizer.fit_transform(df.artigo)
    df_tfidf = pd.DataFrame(variaveis.todense(), columns=vectorizer.get_feature_names())

    print("Convertendo variáveis para float32")
    df_tfidf = df_tfidf.astype('float32')

    print("Concatenando DataFrames")
    df_final = pd.concat([df, df_tfidf], axis=1)

    print("Limpando DF final")
    df_final.drop(["nome_jornal","termo_de_busca","manchete", "artigo"], axis=1, inplace=True)

    print("Dividindo DF final em 10/90")
    df10 = df_final.sample(frac=0.1)
    df90 = df_final.drop(df10.index)

    print("Criação de variáveis por TF-IDF finalizada")
    return df10, df90