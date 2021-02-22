import requests
import pandas as pd
from bs4 import BeautifulSoup
from goose3 import Goose
import re

# Header para o scraper
header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

# Dicionário com jornais do Tocantins, links de busca e domínios
links_jornais = {"jornal do tocantins": ["https://www.jornaldotocantins.com.br/busca?q=", "https://www.jornaldotocantins.com.br/"],
                 "Conexão Tocantins": ["https://conexaoto.com.br/busca?q=", "https://conexaoto.com.br/"],
                 "Agora Tocantins": ["https://www.agora-to.com.br/component/search/?searchword=", "https://www.agora-to.com.br/"],
                 "Folha do Tocantins": ["https://folhadotocantins.com.br/?s=", "https://folhadotocantins.com.br/"]}

# Inicializando Goose
g = Goose()

# Definindo Colunas dos Dataframes
colunas = ["sigla", "nome_jornal", "termo_de_busca", "data", "manchete", "artigo"]

# Sigla do estado
SIGLA = "TO"

# Dicionário para datas
meses = {"Janeiro": "01", "Fevereiro": "02", "Março": "03", "Abril": "04", "Maio": "05", "Junho": "06", "Julho": "07",
         "Agosto": "08", "Setembro": "09", "Outubro": "10", "Novembro": "11", "Dezembro": "12"}

# Função de scraping - Agora Tocantins
def scrap_to_agora_tocantins(tema, data_path, values_path):

    # Criando link de busca do tema
    link = links_jornais["Agora Tocantins"][0] + tema + "&limit=0"  # limit=0 -> remove limite de resultados

    # Separando domínio do site para depois
    dominio = links_jornais["Agora Tocantins"][1]

    # Puxando infos com requests
    url_data = requests.get(link, headers=header).text

    # Scraping com Soup
    soup_id = BeautifulSoup(url_data, "lxml")  # inicializando Soup
    noticias = soup_id.findAll("dt")
    links_noticias = [(dominio + i.contents[1]["href"]) for i in noticias]  # Separando links das matérias

    # Lista para dicionários
    rows_list = []

    # Loop pelas notícias
    for i in range(len(links_noticias)):

        # Extração da data
        url_data_noticia = requests.get(links_noticias[i]).text
        soup = BeautifulSoup(url_data_noticia, "lxml")
        data = soup.findAll("span", {"class": "itemDateCreated"})
        data = [i.contents for i in data][0][2]

        # Formatando data
        dia = re.split(" ", data)[1]
        mes = meses[re.split(" ", data)[2]]
        ano = re.split(" ", data)[3]

        data = "-".join([dia, mes, ano])

        # Definindo id
        ident = f"{i}_{SIGLA}_AgoraTocantins_{tema}"

        # Extração do artigo com goose
        article = g.extract(url=links_noticias[i])
        dict_i = {"unique_identifier": ident, "sigla": SIGLA, "nome_jornal": "Agora Tocantins", "termo_de_busca": tema, "data": data,
               "manchete": article.title}
        rows_list.append(dict_i)

        # Writing .txt
        with open(f"{data_path}/{ident}.txt", 'w') as file:
            file.write(article.cleaned_text)

        print("Artigo {} de {} finalizado".format(i, len(links_noticias)-1))

    df = pd.DataFrame(rows_list)

    try:
        df_values = pd.read_csv(f"{values_path}/{SIGLA}.csv", index_col=[0])
        df = df.append(df_values)
        df.drop_duplicates(inplace=True)
        df.to_csv(f"{values_path}/{SIGLA}.csv")

    except FileNotFoundError:
        df.to_csv(f"{values_path}/{SIGLA}.csv")

    return df


