import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests

def constroi_url(url, query, url_pagina, tema):
    url = url
    query = query
    
    url_pagina = url_pagina
    tema_buscado = tema
    
    link = url+url_pagina+query+tema_buscado
    return link

def beatiful_soup_open(url, header):
    
    req = requests.get(url, headers=header)
    response = req.text
    r_html = BeautifulSoup(response, 'html.parser')
    return r_html

def scraping_acre(r_html, header, tema, tag_paragrafo, atributo_paragrafo, valor_atributo_paragrafo, sigla, nome_do_jornal):
#     NUMERO DE PAGINAS DO SITE
#     numero_de_paginas = int(r_html.findAll('a', {'class', "page-numbers"})[-2].get_text())
    
    #LINKS NOTICIAS DA PAGINA
    href_noticia = [str(href.find("a").attrs['href']) for href in r_html.findAll('h3', {'class', "evo-entry-title"})]
    
    # LISTA DE HTML DE CADA NOTICIA
    noticias = [beatiful_soup_open(link, header) for link in href_noticia]
    
    # DATA DE CADA NOTICIA
    data_noticia = [html.find('div', {'class', "evo-post-date"}).find('a').get_text() for html in noticias]
    
    # MANCHETE DE CADA NOTICIA
    manchete = [tag.get_text() for html in noticias for tag in html.findAll('h1', {'class', "evo-entry-title"})]
    
    # ENCAPSULANDO CADA ARTIGO DE SUA RESPECTIVA MANCHETE
    texto_noticia = {}
    contador = 0
    for html in noticias:
        texto = []
#       Exemplo = html.findAll('span', {'style': 'font-size: 14pt;'}):
        for paragrafo in html.findAll(f'{tag_paragrafo}', {f'{atributo_paragrafo}': f'{valor_atributo_paragrafo}'}):
        
            texto.append(paragrafo.get_text())
        
        texto_noticia[contador] = texto
        contador += 1
    
    tema = [tema.capitalize() for i in range(len(manchete))]
    sigla = [sigla.capitalize() for i in range(len(manchete))]
    nome_do_jornal = [nome_do_jornal.capitalize() for i in range(len(manchete))]
    
#   CRIANDO DATAFRAME

    df = pd.DataFrame({'sigla': sigla,
                       'nome_jornal':nome_do_jornal,
                       'termo_de_busca': tema,
                       'data': data_noticia,
                       'manchete': manchete,
                       'artigo':texto_noticia.values()})
    
    
    '''df = pd.DataFrame({'Manchete': manchete,
                  'Data': data_noticia,
                  'Tema': tema,
                  'Artigo': texto_noticia.values()})'''
                 
    return (df)