import os
from datetime import date
from Vars.aux_funcs_var import *
import ast

path_atual = os.getcwd()
path_aux = path_atual.replace("Vars", r"aux_funcs/")
arquivo_path = open(f'{path_aux}/set_path.py', 'r')
ler_arquivo = arquivo_path.read()
dicionario = ast.literal_eval(ler_arquivo)

def arquivo_mais_recente(termo_de_busca, USUARIO):

    path = f"{dicionario[USUARIO]}/Preproc/"
    lista_arquivos = os.listdir(path)
    data_mais_recente = date(2021 ,1 ,1)
    maior_id = 0
    nome_arquivo_mais_recente = str()
    arquivos_de_interesse = []

    for arquivo in lista_arquivos:
        try:
            componentes = arquivo.split("_")
            if componentes[0] == termo_de_busca:
                arquivos_de_interesse.append(arquivo)
        except:
            None

    for arquivo in arquivos_de_interesse:
        arquivo_limpo = arquivo.split(".")[0]
        tema, data_raw, id_ = arquivo_limpo.split("_")
        data = data_raw.split("-")
        data_datetime = date(int(data[0]), int(data[1]), int(data[2]))
        try:
            if data_datetime >= data_mais_recente:

                if data_datetime == data_mais_recente:
                    if id_ > nome_arquivo_mais_recente.split(".")[0].split("_")[1]:
                        nome_arquivo_mais_recente = arquivo
                else:
                    nome_arquivo_mais_recente = arquivo

                data_mais_recente = data_datetime
        except:
            None

    return nome_arquivo_mais_recente
