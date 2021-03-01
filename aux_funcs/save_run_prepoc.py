from datetime import date
from numpy import nan
from oficial import retorna_texto_limpo

def save_run_prepoc(df):
    coluna_run_id = list(df.unique_identifier)
    lista_artigo_limpo = []
    for run_id in coluna_run_id:
        with open(f'{run_id}.txt', 'r') as text:
            texto = text.read()
        if len(texto) < 4:
            lista_artigo_limpo.append(nan)
        else:
            try:
                lista_artigo_limpo.append(retorna_texto_limpo(texto))
            except:
                print('HOUVE UM ERRO DURANTE O PRÉ-PROCESSAMENTO')

    df['artigo'] = lista_artigo_limpo
    data_do_dia = date.today()
    df.to_csv(f'./{data_do_dia}.csv')
