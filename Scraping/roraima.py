import requests
import pandas as pd
from bs4 import BeautifulSoup
from goose3 import Goose

# Header para o scraper
header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

# Links dos jornais
link_roraima1 = "https://www.roraima1.com.br"
page_roraima1 = "/page/"
tema_roraima_1 = "/?s="

# Inicializando Goose
g = Goose()

# Definindo Colunas dos Dataframes
colunas = ["sigla", "nome_jornal", "termo_de_busca", "data", "manchete", "artigo"]

# Sigla do estado
SIGLA = "RR"


def scrap_rr_roraima1(tema, data_path, values_path):

    # Puxando infos com requests
    url_data = requests.get(link_roraima1 + page_roraima1 + str(1) + tema_roraima_1 + tema, headers=header).text
    soup = BeautifulSoup(url_data, "lxml")  # inicializando Soup

    # Descobrindo número de páginas
    n_page = int(soup.findAll("a", {"class": "last"})[0]["title"])

    # Lista para armazenar links das páginas
    links_paginas = []

    # Coletando links das paginas e datas das noticias
    for pagina in range(1, n_page + 1):
        link_pag = link_roraima1 + page_roraima1 + str(pagina) + tema_roraima_1 + tema
        links_paginas.append(link_pag)

    # Lista para armazenar links das notícias
    links_noticias = []

    # Loop para o scraping dos links das noticias
    for i in range(len(links_paginas)):
        link = links_paginas[i]
        _ = requests.get(link, headers=header).text
        _ = BeautifulSoup(_, "lxml")
        links_noticias.extend([i.contents[0]["href"] for i in soup.findAll("h3", {"class": "entry-title td-module-title"})])
        print(f"Já foram coletados os links da página {i}/{len(links_paginas)}")

    # Lista para armazenar linhas do df
    rows_list = []

    # Loop para o scraping das noticias
    for i in range(len(links_noticias)):
        link = links_noticias[i]
        goose = g.extract(url=link)

        # Coleta da data
        data = "-".join(goose.publish_date[0:10].split("-")[::-1])

        # Definindo id
        ident = f"{i}_{SIGLA}_Roraima1_{tema}"

        # Salvando infos no dicionário
        dict_i = {"unique_identifier": ident, "sigla": SIGLA, "nome_jornal": "Roraima 1", "termo_de_busca": tema,
                  "data": data, "manchete": goose.title}

        rows_list.append(dict_i)

        # Writing .txt
        with open(f"{data_path}/{ident}.txt", 'w') as file:
            file.write(goose.cleaned_text)
        print("Artigo {} de {} finalizado".format(i, len(links_noticias) - 1))

    df = pd.DataFrame(rows_list)

    try:
        df_values = pd.read_csv(f"{values_path}/{SIGLA}.csv", index_col=[0])
        df = df.append(df_values)
        df.drop_duplicates(inplace=True)
        df.to_csv(f"{values_path}/{SIGLA}.csv")

    except FileNotFoundError:
        df.to_csv(f"{values_path}/{SIGLA}.csv")

    return df

# scrap_rr_roraima1("Neymar", data_path="/Users/maxmitteldorf/Desktop/neymar/data", values_path="/Users/maxmitteldorf/Desktop/neymar/values")