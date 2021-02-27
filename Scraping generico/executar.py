from coleta import *
from extracao import *
from urls import *
from multiprocessing import Pool
import pandas as pd


if __name__ == '__main__':

    with Pool(24) as p:
        links = urls(10, 'lula')
        resultado = p.map(coleta_principais, links)

    lista_com_manchete = []
    for lista_manchete in resultado:
        for manchete in lista_manchete[1]:
            lista_com_manchete.append(manchete)

    lista_com_links = []
    for lista_link in resultado:
        for link in lista_link[0]:
            lista_com_links.append(link)

    lista_com_data = []
    for lista_data in resultado:
        for data in lista_data[2]:
            lista_com_data.append(data)

    with Pool(24) as p:
        textos = p.map(coleta_texto, lista_com_links)

    sigla = ['AL' for i in range(len(lista_com_manchete))]
    jornal = ['Jornal Extra' for i in range(len(lista_com_manchete))]
    tema = ['Lula' for i in range(len(lista_com_manchete))]

    df_final = pd.DataFrame({'sigla': sigla,
                             'nome_do_jornal': jornal,
                             'termo_de_busca': tema,
                             'data': lista_com_data,
                             'manchete': lista_com_manchete,
                             'artigo': textos})

    df_final.to_csv(f'{sigla[0]}_{tema[0]}.csv')
