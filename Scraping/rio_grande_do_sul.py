import requests
import pandas as pd
from bs4 import BeautifulSoup
from goose3 import Goose

# Header para o scraper
header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

# Links dos jornais
link_correio_do_povo = "https://www.correiodopovo.com.br"
tema_correio_do_povo = "/busca?q="
page_correio_do_povo = "&page="

# Inicializando Goose
g = Goose()

# Definindo Colunas dos Dataframes
colunas = ["sigla", "nome_jornal", "termo_de_busca", "data", "manchete", "artigo"]

# Sigla do estado
SIGLA = "RS"

def scrap_rs_correio_do_povo(tema, data_path, values_path):

    # Puxando infos com requests
    url_data = requests.get(link_correio_do_povo + tema_correio_do_povo + tema
                            + page_correio_do_povo + "1", headers=header).text

    soup = BeautifulSoup(url_data, "lxml")  # inicializando Soup

    # Descobrindo número de páginas
    n_art = int(soup.findAll("a", {"onclick": "Atex.plugin.search.filterSearch('inputTemplate:standard.Article')"})[0].contents[1].contents[0])
    n_page = round(n_art/25)  # There are 25 results per page
    if n_page == 0:
        n_page+=1

    # Lista para armazenar links das páginas
    links_paginas = []

    # Coletando links das paginas e datas das noticias
    for pagina in range(1, n_page + 1):
        link_pag = link_correio_do_povo + tema_correio_do_povo + tema + page_correio_do_povo + str(pagina)
        links_paginas.append(link_pag)

    # Lista para armazenar links das notícias
    links_noticias = []
    print(links_noticias)

    # Loop para o scraping dos links das noticias
    cont_link = 1
    for pagina in range(len(links_paginas)):
        link = links_paginas[pagina]
        _ = requests.get(link, headers=header).text
        _ = BeautifulSoup(_, "lxml")

        for i in soup.findAll("section", {"class": "main-slot"})[1].contents[1::2]:
            try:
                links_noticias.append(i.contents[1].contents[1]["href"])
                print(f"{cont_link} links coletados")
                cont_link +=1
            except IndexError or KeyError:
                pass
            except KeyError:
                pass

    # Lista para armazenar linhas do df
    rows_list = []

    # Loop para coleta de notícias
    index = 0
    for i in range(len(links_noticias)):
        try:
            # Goose do Artigo
            goose = g.extract(url=link_correio_do_povo+links_noticias[i])

            # Unique ID
            ident = f"{index}_{SIGLA}_CorreioDoPovo_{tema}"

            # Adicionando variáveis ao dicionário
            dict_i = {"unique_identifier": ident, "sigla": SIGLA, "nome_jornal": "CorreioDoPovo", "termo_de_busca": tema,
                      "data": goose.publish_date[0:10], "manchete": goose.title}
            rows_list.append(dict_i)

            # Writing .txt
            with open(f"{data_path}/{ident}.txt", 'w') as file:
                file.write(goose.cleaned_text)

            print("Artigo {} de {} finalizado".format(i, len(links_noticias)-1))
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

# scrap_rs_correio_do_povo("Neymar", data_path="/Users/maxmitteldorf/Desktop/neymar/data", values_path="/Users/maxmitteldorf/Desktop/neymar/values")