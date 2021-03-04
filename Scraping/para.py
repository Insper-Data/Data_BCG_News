from urllib.request import urlopen, urlretrieve, Request
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup, SoupStrainer
from multiprocessing import Pool
import requests
import pandas as pd
from tqdm import tqdm
import lxml
import os

# Funções auxiliares
def extrai_html(url):
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"}
    req = Request(url, headers = header)
    response = urlopen(req)
    html = response.read().decode("utf-8")
    return html

# Função principal

def scraping_PA_OLiberal(termo_de_busca):
    
    ## Definições iniciais
    jornal = "OLiberal"
    estado = "PA"
    linhas_df = []
    total_noticias = 0
    root_dir = "./Scraping_" + estado + "_" + jornal + "_" + termo_de_busca
    txt_dir = root_dir + "/arquivos_txt"
    if not os.path.isdir(root_dir):
        os.mkdir(root_dir)
        os.mkdir(txt_dir)
    
    # Ultima página da pesquisa
    url = "https://www.oliberal.com/?q=" + termo_de_busca + "&page=1000"
    soup = BeautifulSoup(extrai_html(url), "lxml", parse_only = SoupStrainer("ul", class_="pagination")).findAll("li")[-1]
    ultima_pagina = int(soup.a.getText())
    
    ## Lista de links das páginas
    links_noticias = []
    for i in tqdm(range(1, ultima_pagina + 1), desc="Coletando HTMLs das notícias"):
        url = "https://www.oliberal.com/?q=" + termo_de_busca + "&page=" + str(i)
        noticias = BeautifulSoup(extrai_html(url), "lxml", parse_only = SoupStrainer("ul", class_="list-group"))
        for noticia in noticias.findAll("li"):
            link = noticia.h3.a.get("href")
            links_noticias.append("https://www.oliberal.com" + str(link))
            
    for url in tqdm(links_noticias, desc="Notícias coletadas"):
        try:
            soup = BeautifulSoup(extrai_html(url), "lxml", parse_only = SoupStrainer("div", class_="ol-article-content article-content "))
            manchete = soup.find("h1", class_="title article__headline").getText()
            data = soup.find("time", class_="publishing-date").get("datetime")

            paragrafos = soup.find("div", class_="textbody article__body").findAll("p")
            artigo = str()
            for paragrafo in paragrafos:
                artigo += paragrafo.getText() + " "

            unique_identifier = str(total_noticias) + "_" + estado + "_" + jornal + "_" + termo_de_busca.capitalize()
            dic_noticia = {"unique_identifier":unique_identifier,
                               "sigla": estado,
                               "nome_jornal": jornal,
                               "termo_de_busca": termo_de_busca.capitalize(),
                               "data": data,
                               "manchete": manchete}
            linhas_df.append(dic_noticia)
            with open (os.path.join("./" + txt_dir, dic_noticia["unique_identifier"] + ".txt"), "w") as arquivo_txt_noticia:
                arquivo_txt_noticia.write(artigo)

            total_noticias += 1
        except:
            print("PROBLEMA NO URL: " + str(url))
    
    df = pd.DataFrame(linhas_df)
    df.to_csv(root_dir + "/CSV_" + estado + "_" + jornal + ".csv")
    return (f"Scraping finalizado. {total_noticias} notícias coletadas.")

termo_de_busca = input("Qual o termo de busca? \n")
scraping_PA_OLiberal(termo_de_busca)
