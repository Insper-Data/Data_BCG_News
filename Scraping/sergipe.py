import requests
import pandas as pd
from bs4 import BeautifulSoup
from goose3 import Goose
import re

# Header para o scraper
header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

# Inicializando Goose
g = Goose()

# Definindo Colunas dos Dataframes
colunas = ["sigla", "nome_jornal", "termo_de_busca", "data", "manchete", "artigo"]

# Sigla do estado
SIGLA = "SE"

# Links dos jornais
# # A8SE
link_a8se = "https://a8se.com"  # type_id == 19 -> só textos (elimina videos)
query_type = "/busca/?type_id=19"
query_page = "&page="
query_tema = "&query="


def scrap_se_a8se(tema, data_path, values_path):

    # Puxando infos com requests
    url_data = requests.get(link_a8se + query_type + query_page + str(1) + query_tema + tema, headers=header).text
    soup_id = BeautifulSoup(url_data, "lxml")  # inicializando Soup

    # Descobrindo número de páginas
    link_resultados = soup_id.findAll("span")
    n_resultados = None

    for i in link_resultados:
        for string in i.contents:
            if "Encontrado" in string:
                n_resultados = string.split()[1]

    n_paginas = int(int(n_resultados)/10)

    # Lista para armazenar links das páginas
    links_paginas = []

    # Coletando links das paginas e datas das noticias
    for pagina in range(1, n_paginas + 1):
        link_pag = link_a8se + query_type + query_page + str(pagina) + query_tema + tema
        links_paginas.append(link_pag)

    # Lista para armazenar links e datas das notícias
    lista_links_noticias = []
    lista_datas_noticias = []

    # Loop para coleta de links e datas das notícias
    for link in links_paginas:
        url_data = requests.get(link, headers=header).text
        soup_id = BeautifulSoup(url_data, "lxml")  # Inicializando Soup

        links_noticias = soup_id.findAll("a", href=True)
        for i in links_noticias:
            if tema.lower() in i["href"] and "/noticias/" in i["href"]:
                lista_links_noticias.append(link_a8se + i["href"])

        links_datas = soup_id.findAll("h1")
        for i in links_datas:
            if "\n" in i:
                lista_datas_noticias.append(str(i.contents[1])[6:16].replace("/", "-"))

    # Lista para dicionários
    rows_list = []

    # Loop pelas notícias
    for i in range(len(lista_links_noticias)):

        # Definindo id
        ident = f"{i}_{SIGLA}_A8se_{tema}"

        # Extração do artigo com Goose
        article = g.extract(url=lista_links_noticias[i])
        dict_i = {"unique_identifier": ident, "sigla": SIGLA, "nome_jornal": "A8se", "termo_de_busca": tema,
                  "data": lista_datas_noticias[i], "manchete": article.title}
        rows_list.append(dict_i)

        # Separando Texto
        url_data = requests.get(lista_links_noticias[i], headers=header).text
        soup_id = BeautifulSoup(url_data, "lxml")  # inicializando Soup
        try:
            artigo = "\n".join([str(texto.contents[0]) for texto in soup_id.findAll("p")[1:]])
        except IndexError:
            artigo = "\n".join([str(texto.contents) for texto in soup_id.findAll("p")[1:]])


        # Writing .txt
        with open(f"{data_path}/{ident}.txt", 'w') as file:
            file.write(artigo)

        print("Artigo {} de {} finalizado".format(i, len(lista_links_noticias) - 1))

    df = pd.DataFrame(rows_list)

    try:
        df_values = pd.read_csv(f"{values_path}/{SIGLA}.csv", index_col=[0])
        df = df.append(df_values)
        df.drop_duplicates(inplace=True)
        df.to_csv(f"{values_path}/{SIGLA}.csv")

    except FileNotFoundError:
        df.to_csv(f"{values_path}/{SIGLA}.csv")

    return df
