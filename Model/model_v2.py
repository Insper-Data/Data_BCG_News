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
from aux_funcs.set_path import path_user
from make_boruta import *


class Zeus:
    """
    Class criada para construir modelo
    """

    def __init__(self, run_id, user, treino_id, test_id):
        """
        Metodo construtor, aqui serão armazenadas as informações padrões do modelo:
        - User
        - run_id da base
        """

        self.data = datetime.date.today()
        self.run_id = run_id
        self.user = str(user).upper()
        self.path_user = ''
        self.treino_id = treino_id
        self.test_id = test_id
        self.var_treino = ''
        self.var_teste = ''
        self.filtro_nome = False
        self.filtro_local = False
        self.filtro_data = False
        self.nome = ''
        self.local = ''
        self.data = ''
        self.filtro = ''
        self.random_state = 101
        self.base_sintetica = ''
        self.pega_variaveis()

    def pega_path_user(self):
        """
        Metodo que pega o path de acordo com o usuario que inicializou a class
        """
        lista_users = list(path_user.keys())

        if self.user in lista_users:
            print('USUARIO VALIDO !')
            self.path_user = path_user[self.user]
        else:
            raise TypeError('O USUARIO SELECIONADO NÃO TEM UM ENDEREÇO VALIDO CADASTRADO')

    def valida_acesso_path_user(self):
        self.pega_path_user()
        try:
            os.path.exists(self.path_user)
            print('PATH VALIDO PARA ACESSO')

        except:
            raise TypeError('IMPOSSIVEL ACESSAR O PATH')

    def pega_variaveis(self):
        self.valida_acesso_path_user()
        self.var_treino = pd.read_parquet(f'{self.path_user}\Variables\{self.treino_id}.parquet')

    def seleciona_filtros(self, nome=False, local=False, data=False):
        """
        Isinstance verifica se houve uma solicitação de filtro em alguma das variaveis
        """
        self.pega_variaveis()
        estado_nome = isinstance(nome, bool)
        estado_local = isinstance(local, bool)
        estado_data = isinstance(data, bool)

        if not estado_nome:
            self.nome = nome
            self.filtro_nome = True
        if not estado_local:
            self.local = local
            self.filtro_local = True
        if not estado_data:
            self.data = data
            self.filtro_data = True

    def construir_filtro(self):

        if self.filtro_nome and self.filtro_local and self.filtro_data:
            self.filtro = (self.var_treino.termo_de_busca == self.nome.capitalize()) & (
                    self.var_treino.sigla == self.local.upper()) & (self.var_treino.data == self.data)

        elif self.filtro_nome and self.filtro_data and not self.filtro_local:
            self.filtro = (self.var_treino.termo_de_busca == self.nome.capitalize()) & (
                    self.var_treino.data == self.data)

        elif self.filtro_nome and self.filtro_local and not self.filtro_data:
            self.filtro = (self.var_treino.termo_de_busca == self.nome.capitalize()) & (
                    self.var_treino.sigla == self.local.upper())

        elif self.filtro_data and self.filtro_local and not self.filtro_nome:
            self.filtro = (self.var_treino.sigla == self.local.upper()) & (self.var_treino.data == self.data)

        elif self.filtro_nome and not self.filtro_data and not self.filtro_local:
            self.filtro = self.var_treino.termo_de_busca == self.nome.capitalize()

        elif self.filtro_local and not self.filtro_data and not self.filtro_nome:
            self.filtro = self.var_treino.sigla == self.local.upper()

        elif self.filtro_data and not self.filtro_nome and not self.filtro_local:
            self.filtro = self.var_treino.data == self.data

    def filtrar(self, nome=False, local=False, data=False):
        self.seleciona_filtros(nome=nome, local=local, data=data)
        self.construir_filtro()

        self.var_treino = self.var_treino[self.filtro]

    def criar_base_sintetica(self, numero_de_amostras=3, porcentagem_para_criacao=.25):
        bases_sinteticas = []
        self.numero_de_amostras_sinteticas_para_criar = numero_de_amostras
        self.porcentagem_para_criacao_de_amostras = porcentagem_para_criacao
        colunas_pro_drop = ['unique_identifier', 'sigla', 'nome_jornal', 'termo_de_busca', 'data']
        for i in range(numero_de_amostras):
            unique_identifier = self.var_treino['unique_identifier']
            df_com_drop = self.var_treino.drop(columns=colunas_pro_drop)
            df_com_colunas_sorteadas = df_com_drop.sample(frac=porcentagem_para_criacao, replace=True, axis=1)
            amostra = pd.concat([unique_identifier, df_com_colunas_sorteadas], axis=1)
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
                X_df=self.X[[col for col in self.full_cols if col not in self.take_out_cols]],
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
                                       'bagging_fraction': .8, 'bagging_freq': 1}}]

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
            frac=porcentagem_do_sample, replace=True, axis=0).copy()
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
        for cc1, i in tqdm(enumerate(self.raw_leafs), 'FOLHAS:'):
            if cc1 % 100 == 0:
                print(cc1, datetime.datetime.now())
            for cc2_, j in enumerate(self.raw_leafs[cc1 + 1:]):
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
        self.criando_matriz_de_similaridade(porcentagem_do_sample=porcentagem_do_sample)
        self.clusters = (community.best_partition(self.G, weight='weight', randomize=True))

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
        self.var_teste = pd.read_parquet(f'{self.path_user}\Variables\{self.test_id}.parquet')
        self.var_teste = self.var_teste[self.filtro]
        self.predict = self.var_teste.drop(
            columns=['unique_identifier', 'sigla', 'nome_jornal', 'termo_de_busca', 'data'])

        print(f'Tamanho dos dados de treinamento {self.train.shape}')
        print(f'Tamanho dos dados de treinamento {self.predict.shape}')

        x_list = []
        y_list = []
        col_lists = []
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

        y_list += [self.train['label'].values]
        x_list += [self.train.drop(columns=['unique_identifier', 'label'])]
        col_lists += [self.use_cols]
        model_list += [{'type': 'LGBM',
                        'params': {'num_leaves': 30, 'n_estimators': 500, 'boosting_type': 'rf',
                                   'bagging_fraction': .8, 'bagging_freq': 1}}]

        for (model, x, y, cols) in zip(model_list, x_list, y_list, col_lists):
            X = x[cols]
            Y = y
            if model['type'] == 'LGBM':
                model_to_train = lgb.LGBMClassifier(**model['params'])

            trained_models = model_to_train.fit(X=X.values, y=Y)

        self.models = trained_models
        self.previsão = trained_models.predict(self.predict[col_lists[0]])
        self.resultado = self.predict['prev'] = self.previsão
        df_resultante = self.test.copy()
        df_resultante['label'] = self.resultado
        self.df_resultante = df_resultante

        print('FREQUENCIA CLUSTER')
        print(self.df_cluster.Label.value_counts(sort=False))
        print('********************')
        print('FREQUENCIA CLASSIFICADO')
        print(self.df_resultante.label.value_counts(sort=False))

    def plota_palavras_maiores(self, numero):
        for i in range(len(self.df_resultante.label.unique())):
            df_data = pd.DataFrame({'word': self.df_resultante[self.df_resultante.label == i].drop(
                columns=['label', 'unique_identifier']).sum(axis=0).nlargest(numero).index.tolist(),
                                    'value': self.df_resultante[self.df_resultante.label == i].drop(
                                        columns=['label', 'unique_identifier']).sum(axis=0).nlargest(
                                        numero).values.tolist()})

            fig = px.bar(df_data, x='word', y='value', color='value')
            fig.show()

    def salva_parametros(self):
        informações = {
            'user': self.user,
            'data': self.data,
            'run_id_treino': self.treino_id,
            'run_id_teste': self.test_id,
            'path_user': self.path_user,
            'filtro_nome': self.nome,
            'filtro_data': self.data,
            'filtro_local': self.local,
            'numero_de_amostras_bases_sinteticas': self.numero_de_amostras_sinteticas_para_criar,
            'porcentagem_para_criacao_de_amostras': self.porcentagem_para_criacao_de_amostras,
            'porcentagem_para_matriz': self.porcentagem_para_matriz

        }

        file = open(f"../Spine/{self.user}_model_documentation_{self.data}", "wb")
        pickle.dump(informações, file)


