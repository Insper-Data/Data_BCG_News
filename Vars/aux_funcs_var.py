import os
from datetime import date

def arquivo_mais_recente(lista_arquivos):
    data_mais_recente = date(2021 ,1 ,1)
    maior_id = 0
    nome_arquivo_mais_recente = str()

    for i in lista_arquivos:
        if i == ".DS_Store":
            lista_arquivos.remove(".DS_Store")

    for arquivo in lista_arquivos:
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
