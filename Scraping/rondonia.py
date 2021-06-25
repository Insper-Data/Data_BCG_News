import requests
import pandas as pd
from bs4 import BeautifulSoup
from goose3 import Goose
import re
import time

# Header para o scraper
header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

# Inicializando Goose
g = Goose()

# Definindo Colunas dos Dataframes
colunas = ["sigla", "nome_jornal", "termo_de_busca", "data", "manchete", "artigo"]

# Dicionário para datas
meses = {"Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04", "Maio": "05", "Junho": "06", "Julho": "07",
         "Agosto": "08", "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"}

# Sigla do estado
SIGLA = "RO"

# Links dos jornais
# # Rondonia Agora
link_rondonia_agora = "https://www.rondoniagora.com"
query_page = "/busca/pagina-"
query_tema = "?q="


# Função de scraping para o ND Mais
def scrap_ro_rondonia_agora(tema, data_path, values_path):

    # Puxando infos com requests
    url_data = requests.get(link_rondonia_agora + query_page + str(1) + query_tema + tema, headers=header).text
    soup = BeautifulSoup(url_data, "lxml")  # inicializando Soup

    # Descobrindo número de páginas
    page_str = str(soup.findAll("ul", {"class": "pagination"})[0].contents[-1].contents[0])
    n_page = int(re.findall(r'\d+', page_str)[0])

    # Lista para armazenar links das páginas
    links_paginas = []

    # Coletando links das paginas e datas das noticias
    for pagina in range(1, n_page + 1):
        link_pag = link_rondonia_agora + query_page + str(pagina) + query_tema + tema
        links_paginas.append(link_pag)

    # Lista para armazenar links das notícias
    links_noticias = []

    # Loop para o scraping dos links das noticias
    for i in range(len(links_paginas)):
        link = links_paginas[i]
        _ = requests.get(link, headers=header).text
        _ = BeautifulSoup(_, "lxml")
        links_noticias.extend([i["href"] for i in soup.findAll("a", {"class": "titulo"})])

    # Lista para armazenar linhas do df
    rows_list = []

    # Loop para o scraping das noticias
    for i in range(len(links_noticias)):
        link = links_noticias[i]
        goose = g.extract(url=link)
        url_data_i = requests.get(link, headers=header).text
        soup_i = BeautifulSoup(url_data_i, "lxml")

        # Coletando data do artigo
        print(links_noticias[i])
        raw_date = str(soup_i.findAll("div", {"class": "data_publicacao"})[0].contents[0])
        day = re.split(" ", raw_date)[3]
        month = meses[re.split(" ", raw_date)[5]]
        year = re.split(" ", raw_date)[7]
        data = "-".join([day, month, year])

        # Definindo id
        ident = f"{i}_{SIGLA}_RondoniaAgora_{tema}"

        # Salvando infos no dicionário
        dict_i = {"unique_identifier": ident, "sigla": SIGLA, "nome_jornal": "Rondônia Agora", "termo_de_busca": tema,
                  "data": data,
                  "manchete": goose.title}

        rows_list.append(dict_i)

        # Writing .txt
        with open(f"{data_path}/{ident}.txt", 'w') as file:
            file.write(goose.cleaned_text)
        print("Artigo {} de {} finalizado".format(i, len(links_noticias) - 1))
        time.sleep(0.2)

    df = pd.DataFrame(rows_list)

    try:
        df_values = pd.read_csv(f"{values_path}/{SIGLA}.csv", index_col=[0])
        df = df.append(df_values)
        df.drop_duplicates(inplace=True)
        df.to_csv(f"{values_path}/{SIGLA}.csv")

    except FileNotFoundError:
        df.to_csv(f"{values_path}/{SIGLA}.csv")

    return df

# scrap_ro_rondonia_agora("Neymar", data_path="/Users/maxmitteldorf/Desktop/neymar/data", values_path="/Users/maxmitteldorf/Desktop/neymar/values")