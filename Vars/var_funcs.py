from Vars.aux_funcs_var import *
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import os
from tqdm import tqdm
import ast


# # USUÁRIO
USUARIO = "MAX"

# # Lendo arquivo com paths
path_atual = os.getcwd()
path_aux = path_atual.replace("Vars", r"aux_funcs/")
arquivo_path = open(f'{path_aux}/set_path.py', 'r')
ler_arquivo = arquivo_path.read()
dicionario = ast.literal_eval(ler_arquivo)
path_drive = dicionario[USUARIO]

# Funções de criação de variáveis
def var_tfidf (termo_de_busca, min_df, max_features, run_id=""):

    path_preproc = f"{path_drive}/Preproc"

    # Encontrando mais recente
    if run_id == "":
        arquivo = arquivo_mais_recente(termo_de_busca, USUARIO)
    else:
        arquivo = run_id

    # Criando e limpando DF (retirnado linhas de artigos vazios)
    df = pd.read_csv(f"{path_preproc}/{arquivo}", index_col=0)
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

# # var_tfidf("Bolsonaro", min_df=0.001, max_features=1000) # # Exemplo