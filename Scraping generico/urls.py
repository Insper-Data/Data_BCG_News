import time
from extracao import extrai_html, extrai_html_artigo


def constroi_link(url, query, page):

    link = [url, query, page]
    link_formado = ''.join(link)

    return link_formado


def cria_todas_as_urls(ultima_pagina, tema):
    # PASSAR URL
    url = 'https://novoextra.com.br/'
    # PASSAR QUERY
    query = f'resultado-da-busca/{tema}/'
    # tema = tema
    lista_de_urls = []
    for pagina in range(1, ultima_pagina+1):
        if pagina == 1:
            lista_de_urls.append(
                'https://novoextra.com.br/resultado-da-busca/lula/pagina-1')
        else:
            # PASSAR FORMATO DA PAGINA
            page = f'pagina-{pagina}'
            lista_de_urls.append(constroi_link(url, query, page))

    return lista_de_urls

# Não altera


def urls(pagina, tema):
    lista_url = cria_todas_as_urls(pagina, tema)
    print(type(lista_url))
    print(lista_url[0])
    print(lista_url[1])
    return lista_url
