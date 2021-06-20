import ast
import community
import datetime
import lightgbm as lgb
import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
import pickle
import plotly.express as px
import os
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score
from tqdm import tqdm
from make_boruta import *


class Zeus:
    """
    Class criada para construir modelo
    """

    def __init__(self, termo, user, treino_id, test_id):
        """
        Metodo construtor, aqui serão armazenadas as informações padrões do modelo:
        - User
        - run_id da base
        """
        self.term = termo
        self.data = datetime.date.today()
        self.user = str(user).upper()
        self.path_user = ''
        self.treino_id = treino_id
        self.test_id = test_id
        self.var_treino = ''
        self.var_teste = ''
        self.filtro_local = False
        self.filtro_data = False
        self.local = ''
        self.data_start = ''
        self.data_end = ''
        self.filtro = ''
        self.random_state = 101
        self.base_sintetica = ''
        self.data_active = False
        self.data_local = False
        self.mm = ''
        self.ids = ''
        self.train = ''
        self.numero_de_amostras_sinteticas_para_criar = ''
        self.porcentagem_para_criacao_de_amostras = ''
        self.df_cluster = ''
        self.clusters = ''
        self.var_teste_original = ''
        self.pega_variaveis()
        self.agregado = ''
        self.df_agregado = ''
        self.informacoes = ''
        self.sentimento = ''
        self.data_df = ''

    def pega_path_user(self):
        """
        Metodo que pega o path de acordo com o usuario que inicializou a class
        """
        os.chdir(os.path.dirname(
            r'C:\Users\wilgn\Desktop\Faculdade\3° Semestre\Insper Data\Projeto\Git projeto\Data_BCG_News\Model\\'))
        path_atual = os.getcwd()
        print(os.listdir())
        if self.user == 'WILGNER':
            path_aux_funcs = path_atual.replace('Model', r'aux_funcs\\')
        else:
            path_aux_funcs = path_atual.replace('Model', r'aux_funcs/')

        os.chdir(os.path.dirname(path_aux_funcs))
        print(os.listdir())
        with open('set_path.py', 'r') as arquivo_path:
            ler_arquivo = arquivo_path.read()
            dicionario = ast.literal_eval(ler_arquivo)

            lista_users = list(dicionario.keys())

            if self.user in lista_users:
                print('USUARIO VALIDO !')
                self.path_user = dicionario[self.user]
            else:
                raise TypeError(
                    'O USUARIO SELECIONADO NÃO TEM UM ENDEREÇO VALIDO CADASTRADO')

        os.chdir(os.path.dirname(
            r'C:\Users\wilgn\Desktop\Faculdade\3° Semestre\Insper Data\Projeto\Git projeto\Data_BCG_News\Model\\'))
        print(os.listdir())
        # arquivo_path.close()

    def valida_acesso_path_user(self):
        self.pega_path_user()
        try:
            os.path.exists(self.path_user)
            print('PATH VALIDO PARA ACESSO')

        except:
            raise TypeError('IMPOSSIVEL ACESSAR O PATH')

    def pega_variaveis(self, teste=False):

        if teste:
            path_name = f'{self.path_user}Variables/{self.term}/{self.test_id}.parquet'
            os.chdir(os.path.dirname(path_name))
            # print(os.listdir())
            # print(path_name)
            self.var_teste = pd.read_parquet(os.path.basename(path_name))

        else:
            self.valida_acesso_path_user()
            path_name = f'{self.path_user}Variables/{self.term}/{self.treino_id}.parquet'
            os.chdir(os.path.dirname(path_name))
            # print(os.listdir())
            # print(path_name)
            self.var_treino = pd.read_parquet(os.path.basename(path_name))

    def seleciona_filtros(self, local=False, data_start=False, data_end=False):
        """
        Isinstance verifica se houve uma solicitação de filtro em alguma das variaveis
        """
        estado_local = isinstance(local, bool)
        estado_data_start = isinstance(data_start, bool)

        if not estado_local:
            self.local = local
            self.filtro_local = True
        if not estado_data_start:
            self.data_start = data_start
            self.data_end = data_end
            self.filtro_data = True

    def construir_filtro(self, teste=False):
        self.filtro = ''
        if not teste:
            if self.filtro_local and self.filtro_data:
                self.filtro = (self.var_treino.sigla == self.local.upper())
                self.data_local = True
                self.data_active = True

            elif self.filtro_data and not self.filtro_local:
                self.data_active = True

            elif self.filtro_local and not self.filtro_data:
                self.filtro = (self.var_treino.sigla == self.local.upper())
        else:
            if self.filtro_local and self.filtro_data:
                self.filtro = (self.var_teste.sigla == self.local.upper())
                self.data_local = True
                self.data_active = True

            elif self.filtro_data and not self.filtro_local:
                self.data_active = True

            elif self.filtro_local and not self.filtro_data:
                self.filtro = (self.var_teste.sigla == self.local.upper())

    def filtrar_treino(self, local=False, data_start=False, data_end=False):
        self.seleciona_filtros(
            local=local, data_start=data_start, data_end=data_end)
        self.construir_filtro()
        self.var_treino.data = pd.to_datetime(self.var_treino.data)

        if self.data_active and self.data_local:
            self.var_treino = self.var_treino[self.filtro]
            self.var_treino = self.var_treino[(self.var_treino.data > self.data_start) & (
                    self.var_treino.data < self.data_end)]
        elif self.data_active and not self.data_local:
            self.var_treino = self.var_treino[
                (self.var_treino.data > self.data_start) & (self.var_treino.data < self.data_end)]
        else:
            self.var_treino = self.var_treino[self.filtro]

    def filtrar_teste(self, local=False, data_start=False, data_end=False):
        self.seleciona_filtros(
            local=local, data_start=data_start, data_end=data_end)
        self.construir_filtro(teste=True)
        self.var_teste.data = pd.to_datetime(self.var_teste.data)

        if self.data_active and self.data_local:
            self.var_teste = self.var_teste[self.filtro]
            self.var_teste = self.var_teste[
                (self.var_teste.data > self.data_start) & (self.var_teste.data < self.data_end)]
        elif self.data_active and not self.data_local:
            self.var_teste = self.var_teste[
                (self.var_teste.data > self.data_start) & (self.var_teste.data < self.data_end)]
        else:
            self.var_teste = self.var_teste[self.filtro]

    def criar_base_sintetica(self, numero_de_amostras=3, porcentagem_para_criacao=.25):
        bases_sinteticas = []
        self.numero_de_amostras_sinteticas_para_criar = numero_de_amostras
        self.porcentagem_para_criacao_de_amostras = porcentagem_para_criacao
        colunas_pro_drop = ['unique_identifier', 'sigla', 'data', 'sentimento']
        for i in range(numero_de_amostras):
            unique_identifier = self.var_treino['unique_identifier']
            df_com_drop = self.var_treino.drop(columns=colunas_pro_drop)
            df_com_colunas_sorteadas = df_com_drop.sample(
                frac=porcentagem_para_criacao, replace=True, random_state=self.random_state, axis=1)
            amostra = pd.concat(
                [unique_identifier, df_com_colunas_sorteadas], axis=1)
            amostra_sintetica = pd.DataFrame()
            amostra = amostra.loc[:, ~amostra.columns.duplicated()]

            for coluna in amostra.columns.tolist():
                amostra_sintetica[coluna] = amostra[coluna].sample(frac=1, replace=True,
                                                                   random_state=self.random_state).tolist()
            amostra_sintetica['label'] = 1
            amostra['label'] = 0

            amostra_concluida = pd.concat([amostra, amostra_sintetica])
            amostra_concluida.reset_index(inplace=True, drop=True)
            bases_sinteticas.append(amostra_concluida)

        self.base_sintetica = bases_sinteticas

    def treina_lightGBM(self, boruta_percs=[10], thr_bor_good=.5, thr_bor_ok=.9):
        numero_de_amostras = len(self.base_sintetica)
        x_list = []
        y_list = []
        col_lists = []
        model_list = []
        trained_models = []

        dfs = self.base_sintetica
        for i in range(numero_de_amostras):
            numero_de_colunas = dfs[i].shape[1]

            self.Y = dfs[i]['label']
            self.X = dfs[i].drop(columns=['unique_identifier', 'label'])
            self.take_out_cols_0 = []
            self.take_out_cols = []
            self.full_cols = self.X.columns.tolist()
            self.thr_bor_good = thr_bor_good
            self.thr_bor_ok = thr_bor_ok
            self.boruta_percs = boruta_percs
            self.boruta_res = boruta_select(
                X_df=self.X[[
                    col for col in self.full_cols if col not in self.take_out_cols]],
                Y=self.Y, perc_list=self.boruta_percs, allowed_perc_good=self.thr_bor_good,
                allowed_perc_med=self.thr_bor_ok)

            self.take_out_cols_irrelevant = self.boruta_res[0].loc[~self.boruta_res[0]['use']].index.tolist(
            )
            self.take_out_cols += self.take_out_cols_irrelevant

            self.use_cols = self.X[[col for col in self.X.columns.tolist(
            ) if col not in self.take_out_cols]].columns.tolist()

            y_list += [dfs[i]['label'].values]
            x_list += [dfs[i].drop(columns=['unique_identifier', 'label'])]
            col_lists += [self.use_cols]
            model_list += [{'type': 'LGBM',
                            'params': {'num_leaves': 25, 'n_estimators': 300, 'boosting_type': 'rf',
                                       'bagging_fraction': .8, 'bagging_freq': 1, 'random_state': self.random_state}}]

        # Treinando modelo
        for (model, x, y, cols) in zip(model_list, x_list, y_list, col_lists):
            X = x[cols]
            Y = y
            if model['type'] == 'LGBM':
                model_to_train = lgb.LGBMClassifier(**model['params'])

            trained_models += [model_to_train.fit(X=X.values, y=Y)]

        self.models = trained_models
        self.rf_models = self.models
        self.col_lists = col_lists

    def coleta_folhas(self, porcentagem_do_sample=0.1):

        self.df_random = self.var_treino.sample(
            frac=porcentagem_do_sample, replace=True, random_state=self.random_state, axis=0).copy()
        print(self.df_random.shape)
        # frame_list = []
        model_c = 0
        self.mm = set()
        self.ids = self.df_random['unique_identifier'].tolist()
        print('start with list values')

        # Pegando o resultado das folhas do model
        for (model, cols) in zip(self.rf_models, self.col_lists):
            if cols == 'label':
                continue
            else:
                raw_leafs = model.predict(
                    self.df_random[cols].values, pred_leaf=True)
                # return raw_leafs
                if model_c == 0:
                    full_leafs = raw_leafs
                else:
                    full_leafs = np.concatenate(
                        (full_leafs, raw_leafs), axis=1)

                model_c += 1
        self.raw = raw_leafs

    def criando_matriz_de_similaridade(self, porcentagem_do_sample=0.1):
        self.porcentagem_para_matriz = porcentagem_do_sample
        self.coleta_folhas(porcentagem_do_sample=porcentagem_do_sample)
        print('CRIANDO EDGES')
        edges = []
        # Criando matriz de similaridade
        for cc1, i in tqdm(enumerate(self.raw), 'FOLHAS:'):
            if cc1 % 100 == 0:
                print(cc1, datetime.datetime.now())
            for cc2_, j in enumerate(self.raw[cc1 + 1:]):
                cc2 = cc2_ + cc1 + 1
                if (cc1, cc2) not in self.mm and (cc2, cc1) not in self.mm:
                    leaf_count = sum(i == j)
                    # TODO: Fix similarity matrix with the square root
                    edges += [(self.ids[cc1], self.ids[cc2],
                               math.sqrt(leaf_count / len(self.raw[0])))]
                    self.mm.add((cc1, cc2))
        print('done with list values')

        # YOU ARE HERE
        G = nx.Graph()

        G.add_weighted_edges_from(edges)
        self.G = G

    def rodando_louvain(self, porcentagem_do_sample):
        self.criando_matriz_de_similaridade(
            porcentagem_do_sample=porcentagem_do_sample)
        self.clusters = (community.best_partition(
            self.G, weight='weight', randomize=True))

    def desenha_cluster_no_edges(self):
        plt.figure(figsize=(12, 8), dpi=150)
        plt.title('Louvain Tets', fontsize=20, loc='left', pad=15)
        self.pos = nx.spring_layout(self.G)
        nx.draw_networkx_nodes(self.G, self.pos, self.clusters.keys(), node_size=150,
                               node_color=list(self.clusters.values()))
        plt.show()

    def classifica_agrupamento(self, boruta_percs=[10], thr_bor_good=.5, thr_bor_ok=.9, take_out_cols=False):

        self.df_cluster = pd.DataFrame({'Rotulo': self.clusters.keys(),
                                        'Label': self.clusters.values()})
        print(f'Tamanho dos dados de cluster {self.df_cluster.shape}')
        self.train = self.var_treino[self.var_treino['unique_identifier'].isin(
            self.df_cluster.Rotulo.values.tolist())]
        self.train['label'] = self.df_cluster.Label.values.tolist()
        self.train.reset_index(drop=True)

        colunas_pro_drop = ['unique_identifier', 'sigla', 'data', 'sentimento', 'artigo_original']
        self.var_teste_original = self.var_teste
        self.sentimento = self.var_teste_original['sentimento']
        self.data_df = self.var_teste_original['data']
        self.var_teste = self.var_teste.drop(columns=colunas_pro_drop)
        self.train = self.train.drop(columns=['sigla', 'data', 'sentimento', 'artigo_original'])
        self.var_teste.reset_index(drop=True)
        self.train.reset_index(drop=True)

        print(f'Tamanho dos dados de treinamento {self.train.shape}')
        print(f'Tamanho dos dados de teste {self.var_teste.shape}')

        self.x_list = []
        self.y_list = []
        self.col_lists = []
        model_list = []
        trained_models = 0
        self.Y = self.train['label']
        self.X = self.train.drop(columns=['unique_identifier', 'label'])
        self.take_out_cols_0 = []
        self.take_out_cols = []
        self.full_cols = self.X.columns.tolist()
        self.thr_bor_good = thr_bor_good
        self.thr_bor_ok = thr_bor_ok
        self.boruta_percs = boruta_percs
        self.boruta_res = boruta_select(X_df=self.X[[col for col in self.full_cols if col not in self.take_out_cols]],
                                        Y=self.Y, perc_list=self.boruta_percs, allowed_perc_good=self.thr_bor_good,
                                        allowed_perc_med=self.thr_bor_ok)

        self.take_out_cols_irrelevant = self.boruta_res[0].loc[~self.boruta_res[0]['use']].index.tolist(
        )
        self.take_out_cols += self.take_out_cols_irrelevant

        self.use_cols = self.X[[col for col in self.X.columns.tolist(
        ) if col not in self.take_out_cols]].columns.tolist()

        if len(self.use_cols) < 1:
            self.use_cols = self.X.columns.tolist()

        self.y_list += [self.train['label'].values]
        self.x_list += [self.train.drop(columns=['unique_identifier', 'label'])]
        self.col_lists += [self.use_cols]
        model_list += [{'type': 'LGBM',
                        'params': {'num_leaves': 30, 'n_estimators': 500, 'boosting_type': 'rf',
                                   'bagging_fraction': .8, 'bagging_freq': 1, 'random_state': self.random_state}}]

        for (model, x, y, cols) in zip(model_list, self.x_list, self.y_list, self.col_lists):
            X = x[cols]
            print(X.shape)
            Y = y
            print(Y.shape)
            if model['type'] == 'LGBM':
                model_to_train = lgb.LGBMClassifier(**model['params'])

            trained_models = model_to_train.fit(X=X.values, y=Y)

        self.models = trained_models
        self.previsão = trained_models.predict(
            self.var_teste[self.col_lists[0]])
        self.resultado = self.previsão
        self.var_teste['label'] = self.resultado

        self.faz_agregacao()

        print('FREQUENCIA CLUSTER')
        print(self.df_cluster.Label.value_counts(sort=False))
        print('********************')
        print('FREQUENCIA CLASSIFICADO')
        print(self.var_teste.label.value_counts(sort=False))



    def plota_palavras_maiores(self, numero):
        for i in range(len(self.var_teste.label.unique())):
            df_data = pd.DataFrame({'word': self.var_teste[self.var_teste.label == i].drop(
                columns=['label']).sum(axis=0).nlargest(numero).index.tolist(),
                                    'value': self.var_teste[self.var_teste.label == i].drop(
                                        columns=['label']).sum(axis=0).nlargest(
                                        numero).values.tolist()})

            fig = px.bar(df_data, x='word', y='value', color='value', color_continuous_scale='Blues')
            fig.show()

    def salva_parametros(self):
        self.informacoes = {
            'user': self.user,
            'data': self.data,
            'run_id_treino': self.treino_id,
            'run_id_teste': self.test_id,
            'path_user': self.path_user,
            'filtro_nome': self.term,
            'filtro_data': self.data,
            'filtro_local': self.local,
            'numero_de_amostras_bases_sinteticas': self.numero_de_amostras_sinteticas_para_criar,
            'porcentagem_para_criacao_de_amostras': self.porcentagem_para_criacao_de_amostras,
            'porcentagem_para_matriz': self.porcentagem_para_matriz

        }

    def faz_agregacao(self):
        # Agrega os resultados
        self.var_teste_original['label'] = self.var_teste['label']
        self.agregado = self.var_teste_original[['unique_identifier', 'sigla', 'data', 'label']]
        self.df_agregado = pd.crosstab(self.agregado.sigla, self.agregado.label, normalize='index')

        return self.df_agregado
