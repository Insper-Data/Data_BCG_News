"""Local onde esta o model"""
PATH_ZEUS = r'C:\Users\wilgn\Desktop\Faculdade\3° Semestre\Insper Data\Projeto\Git projeto\Data_BCG_News\Model\\model_v2.py'
PATH_DASH = r'C:\Users\wilgn\Desktop\Faculdade\3° Semestre\Insper Data\Projeto\Git projeto\Data_BCG_News\Dash\\'

"""Variaveis"""
USERS = {'Wilgner': 'Wilgner',
         'Rodrigo': 'Rodrigo',
         'Max': 'Max'}

NUMERO_DE_AMOSTRAS = 5
PORCENTAGEM_PARA_CRIACAO = 0.3
PORCENTAGEM_PARA_SAMPLE = 0.2


def constroi_id(termo):

    treino_id = f'var_tfidf_{termo}_10_2021-06-24_0'
    teste_id = f'var_tfidf_{termo}_90_2021-06-24_0'

    return [treino_id, teste_id]
