import requests
import pandas as pd
from bs4 import BeautifulSoup
from goose3 import Goose

# Header para o scraper
header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

# Inicializando Goose
g = Goose()

# Definindo Colunas dos Dataframes
colunas = ["sigla", "nome_jornal", "termo_de_busca", "data", "manchete", "artigo"]

# Sigla do estado
SIGLA = "SC"


# Função de scraping para o ND Mais
def scrap_sc_ndmais(tema, data_path, values_path):

    # #  Descobrindo número de páginas de busca
    i = 10000  # Número máximo de páginas para pesquisar
    n_paginas = None
    lista_links = []  # Lista em branco para guardar links das notícias

    while i > 0:

        link = f"https://ndmais.com.br/wp-admin/admin-ajax.php?action=ajax_pagination&query_args=%7B%22s%22%3A%22{tema}%22%7D&page={i}"
        url_data = requests.get(link, headers=header).text
        soup = BeautifulSoup(url_data, "lxml")

        try:
            if str(soup.findAll("h1", {"class": "section-title title py-2"})[0].contents[0]) == "Conteúdo não encontrado":
                if i >= 5000:
                    i -= 100
                    print(f"determinando número de resultados, faltam {i} páginas")
                elif (i < 5000) and (i >= 2000):
                    i -= 50
                    print(f"determinando número de resultados, faltam {i} páginas")
                elif (i < 2000) and (i >= 500):
                    i -= 25
                    print(f"determinando número de resultados, faltam {i} páginas")
                elif (i < 500) and (i > 200):
                    i -= 5
                    print(f"determinando número de resultados, faltam {i} páginas")
                else:
                    i -= 1

        except IndexError:
            # Coleta dos links das notícias
            url_data = requests.get(link, headers=header).text
            soup = BeautifulSoup(url_data, "lxml")
            links_pag_i = [i["href"] for i in soup.findAll("a", {"class": "title"})]
            lista_links.extend(links_pag_i)
            print(f"Falta coletar o link de mais {i} páginas!")
            i -= 1

    print("Prosseguindo para coleta de notícias")

    # Lista para dicionários
    rows_list = []

    # Loop para coleta de notícias
    index = 0
    for i in range(len(lista_links)):
        try:
            # Goose do Artigo
            goose = g.extract(lista_links[i])

            # Unique ID
            ident = f"{index}_{SIGLA}_Ndmais_{tema}"

            # Adicionando variáveis ao dicionário
            dict_i = {"unique_identifier": ident, "sigla": SIGLA, "nome_jornal": "ND Mais", "termo_de_busca": tema,
                      "data": goose.publish_date[0:10], "manchete": goose.title}
            rows_list.append(dict_i)

            # Writing .txt
            with open(f"{data_path}/{ident}.txt", 'w') as file:
                file.write(goose.cleaned_text)

            print("Artigo {} de {} finalizado".format(i, len(lista_links)-1))
            index += 1

        except:
            print("Documento em branco")

    # Saving texts info:
    df = pd.DataFrame(rows_list)

    try:
        df_values = pd.read_csv(f"{values_path}/{SIGLA}.csv", index_col=[0])
        df = df.append(df_values)
        df.drop_duplicates(inplace=True)
        df.to_csv(f"{values_path}/{SIGLA}.csv")

    except FileNotFoundError:
        df.to_csv(f"{values_path}/{SIGLA}.csv")

    return df
