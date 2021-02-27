from bs4 import BeautifulSoup, SoupStrainer
import requests
import time


def extrai_html(url_pronta):
    # PASSAR TAG PRINCIPAL
    custom = SoupStrainer('div', {'class': 'item'})
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    req = ''
    while req == '':
        try:
            req = requests.get(url_pronta, headers=header)
            break
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue

    response = req.text
    html = BeautifulSoup(response, 'lxml', parse_only=custom)

    return html


def extrai_html_artigo(url_pronta):
    # PASSAR TAG PRINCIPAL
    custom = SoupStrainer('article', {'id': 'materia_texto'})
    header = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    req = ''
    while req == '':
        try:
            req = requests.get(url_pronta, headers=header)
            break
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            time.sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue

    response = req.text

    html = BeautifulSoup(response, 'lxml', parse_only=custom)

    return html
