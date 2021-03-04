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

def scraping_PI_CidadeVerde(termo_de_busca):
    
    ## Definições iniciais
    jornal = "CidadeVerde"
    estado = "PI"
    linhas_df = []
    total_noticias = 0
    root_dir = "./Scraping_" + estado + "_" + jornal + "_" + termo_de_busca
    txt_dir = root_dir + "/arquivos_txt"
    if not os.path.isdir(root_dir):
        os.mkdir(root_dir)
        os.mkdir(txt_dir)
    
    # Ultima página da pesquisa
    url = "https://cidadeverde.com/buscar/noticias/" + termo_de_busca + "/p/1"
    soup = BeautifulSoup(extrai_html(url), "lxml", parse_only = SoupStrainer("ul", class_="pagination")).findAll("li")[-1]
    ultima_pagina = int(soup.a.get("href").split("/")[-1])
    
    ## Lista de links das páginas
    links_noticias = []
    for i in tqdm(range(1, ultima_pagina + 1), desc="Coletando HTMLs das notícias"):
        url = "https://cidadeverde.com/buscar/noticias/" + termo_de_busca + "/p/" + str(i)
        noticias = BeautifulSoup(extrai_html(url), "lxml", parse_only = SoupStrainer("div", class_="ultimas clearfix")).find("ul")
        for noticia in noticias.findAll("li"):
            link = noticia.a.get("href")
            links_noticias.append(link)

    for url in tqdm(links_noticias, desc="Notícias coletadas"):
        try:
            soup = BeautifulSoup(extrai_html(url), "lxml", parse_only = SoupStrainer("div", id="main"))
            manchete = soup.find("h1", class_="post-title").a.getText()
            data_raw = soup.find("p", class_="post-date").getText()[:8].split("/")
            data = "-".join(("20" + data_raw[2], data_raw[1], data_raw[0]))
            paragrafos = soup.find("div", class_="post-body").findAll("p")
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
scraping_PI_CidadeVerde(termo_de_busca)
