from urllib.request import urlopen, urlretrieve, Request
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup, SoupStrainer
from multiprocessing import Pool
import requests
import pandas as pd
from tqdm import tqdm
import lxml
import os

def extrai_html(url):
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"}
    req = Request(url, headers = header)
    response = urlopen(req)
    html = response.read().decode("utf-8")
    return html

def scraping_SP_FolhaSP(termo_de_busca):

    ## Definições iniciais
    jornal = "FolhaSP"
    estado = "SP"
    linhas_df = []
    total_noticias = 0
    root_dir = "./Scraping_" + estado + "_" + jornal + "_" + termo_de_busca
    txt_dir = root_dir + "/arquivos_txt"
    if not os.path.isdir(root_dir):
        os.mkdir(root_dir)
        os.mkdir(txt_dir)
    erros = 0

    ## Lista de links das páginas
    links_noticias = []
    for i in tqdm(range(1, 9977, 25), desc="Coletando HTMLs das notícias"):
        url = f"https://search.folha.uol.com.br/search?q={termo_de_busca}&site=todos&periodo=todos&sr={str(i)}&results_count=10000&search_time=0%2C066&url=https%3A%2F%2Fsearch.folha.uol.com.br%2Fsearch%3Fq%3Dbolsonaro%26site%3Dtodos%26periodo%3Dtodos%26sr%3D25984"
        
        noticias = BeautifulSoup(extrai_html(url), "lxml", parse_only = SoupStrainer("div", class_="col col--md-10-15 col--lg-12-18"))
        for noticia in noticias.findAll("div", class_="c-headline__content"):
            link = noticia.a.get("href")
            links_noticias.append(link)

    for url in tqdm(links_noticias, desc="Notícias coletadas"):
        try:
            soup = BeautifulSoup(extrai_html(url), "lxml", parse_only = SoupStrainer("main", id="conteudo"))
            manchete = soup.find("h1", class_="c-content-head__title").getText()
            data = soup.find("time", class_="c-more-options__published-date")['datetime'][:10]

            paragrafos = soup.find("div", class_="c-news__body").findAll("p")
            artigo = ""
            for paragrafo in paragrafos:
                artigo += paragrafo.getText()

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
            erros += 1
            print("PROBLEMA NO URL: " + str(url))
    
    df = pd.DataFrame(linhas_df)
    df.to_csv(root_dir + "/CSV_" + estado + "_" + jornal + ".csv")
    print(f"{erros} erros de scraping")
    return (f"Scraping finalizado. {total_noticias} notícias coletadas.")

termo_de_busca = input("Qual o termo de busca? \n")
scraping_SP_FolhaSP(termo_de_busca)