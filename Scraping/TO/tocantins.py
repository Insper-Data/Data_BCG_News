import requests
import pandas as pd
from bs4 import BeautifulSoup
from goose3 import Goose

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

# Função de scraping - Agora Tocantins
def scrap_to_agora_tocantins(tema):

    # Criando link de busca do tema
    link = links_jornais["Agora Tocantins"][0] + tema + "&limit=0"  # limit=0 -> remove limite de resultados

    # Separando domínio do site para depois
    dominio = links_jornais["Agora Tocantins"][1]

    # Puxando infos com requests
    url_data = requests.get(link).text

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

        # Extração do artigo com goose
        article = g.extract(url=links_noticias[i])
        dict_i = {"sigla": SIGLA, "nome_jornal": "Agora Tocantins", "termo_de_busca": tema, "data": data,
               "manchete": article.title, "artigo": article.cleaned_text}
        rows_list.append(dict_i)
        dict_i.update()
        print("Artigo {} de {} finalizado".format(i, len(links_noticias)))

    df = pd.DataFrame(rows_list)

    return df


df_agora_to = scrap_to_agora_tocantins("Bolsonaro")

df_agora_to.to_csv("TO_AgoraTocantins_Bolsonaro.csv")