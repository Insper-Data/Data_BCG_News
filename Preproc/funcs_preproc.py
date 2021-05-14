import string
import re
import unicodedata
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
import ssl
import nltk

# # Desabilitando verificação de ssh  #### Usar isso se o download do nltk data falhar
# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context
#

# variaveis para limpeza
lista_stopwords_pt = stopwords.words('portuguese')
pt_stemmer = SnowballStemmer('portuguese')
pt_lematizer = WordNetLemmatizer()

# # Download de dados do nltk
# nltk.download("wordnet")


# Função que remove os \n e toda pontuação
def remove_punctuation(texto):
    texto_ = texto.replace('\\n', '')
    texto_limpo = ''.join(
        [letter for letter in texto_.lower() if letter not in string.punctuation])
    return texto_limpo

  
# Função que remove os acentos de cada palavra sem tirar a letra
# link da função: https://www.edureka.co/community/68910/what-is-the-best-way-remove-accents-in-python-unicode-string
def remove_accents(string, accents=('COMBINING ACUTE ACCENT', 'COMBINING GRAVE ACCENT', 'COMBINING TILDE')):
    accents = set(map(unicodedata.lookup, accents))
    chars = [c for c in unicodedata.normalize(
        'NFD', string) if c not in accents]
    return unicodedata.normalize('NFC', ''.join(chars))


def remove_stopwords(text):
    lista_text = text.split()
    sem_stop_words = [
        text for text in lista_text if text not in lista_stopwords_pt]
    texto_sem_stop_words = ' '.join(sem_stop_words)

    return texto_sem_stop_words


def stem_and_lemmatize(text):
    stem_text = [pt_stemmer.stem(word) for word in word_tokenize(text)]
    lematizze_text = [pt_lematizer.lemmatize(word) for word in stem_text]

    return "".join(lematizze_text)


def clean_text_func(text):
    texto_sem_pontuacao = remove_punctuation(text)
    texto_sem_acento = remove_accents(texto_sem_pontuacao)
    texto_pos_regex = re.sub(
        r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)|^rt|http.+?|[0-9.*]", "", texto_sem_acento).strip()
    texto_sem_stopword = remove_stopwords(texto_pos_regex)
    texto_stematizado_e_lematizado = stem_and_lemmatize(texto_sem_stopword)

    return texto_stematizado_e_lematizado

