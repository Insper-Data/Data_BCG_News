from extracao import *
from urls import *
from tqdm import tqdm


def coleta_principais(URL_PRONTA):
    LISTA_HREF, LISTA_MANCHETE, LISTA_DATA = [], [], []
    html = extrai_html(URL_PRONTA)

    # PASSART TAGS PARA TITULO, DATA, LINK
    try:
        for tag in html.findAll('a'):
            LISTA_HREF.append(tag.attrs['href'])
    except:
        print('NAO CONSEGUI ACESSAR ESSE HREF !!')
        LISTA_HREF.append('NaN')

    try:
        for tag in html.findAll('a'):
            LISTA_MANCHETE.append(tag.find('strong').get_text())
    except:
        print('NAO CONSEGUI ACESSAS ESSA MANCHETE !!')
        LISTA_MANCHETE.append('NaN')

    try:
        for a in html.findAll('a'):
            LISTA_DATA.append(a.find('small').get_text())

    except:
        print('NAO CONSEGUI ACESSAR ESSA DATA !!')
        LISTA_DATA.append('NaN')

    return LISTA_HREF, LISTA_MANCHETE, LISTA_DATA


def coleta_texto(href_pronto):
    # PASSAR TAGS DE TEXTO AQ
    html = extrai_html_artigo(href_pronto)

    lista_texto = []

    try:
        for tag in html.findAll('p'):

            lista_texto.append(tag.get_text())
    except:
        print('NAO CONSEGUI PEGAR ESSE TEXTO !!')
        lista_texto.append('NaN')

    return lista_texto
