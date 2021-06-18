import numpy as np
import pandas as pd
import datetime
import lightgbm as lgb
import networkx as nx
import community
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import roc_auc_score
from sklearn.feature_selection import SelectKBest, chi2
from tqdm import tqdm
import matplotlib.pyplot as plt
import plotly.express as px
import dask.dataframe as dd
from dask.diagnostics import ProgressBar
import os
from boruta import BorutaPy
from make_boruta import *


class Zeus():
    """
    CLASS CRIADA PARA CONSTRUÇÃO DO MODELO PREDITIVO
    """

    def __init__(self, user, path_treino, path_teste, run_id_train, run_id_teste, process_type, save_info=False, ):
        """
        Parametros:
        - user: Pessoa que esta criando o modelo
        - path: endereço dos dataset treino e teste
        - run_id: identificador do csv no Spine
        - save_info - teste ou oficial

        """

        """EXTRAIR PROCESS RUN_ID SPINE"""

        # trainFile = f'C:/Users/wilgn/OneDrive - Insper - Institudo de Ensino e Pesquisa/Data_BCG_News/Variables/{run_id_train}.parquet'
        # testeFile = f'C:/Users/wilgn/OneDrive - Insper - Institudo de Ensino e Pesquisa/Data_BCG_News/Variables/{run_id_teste}.parquet'
        trainFile = f'{path_treino}{run_id_train}.parquet'
        testeFile = f'{path_teste}{run_id_teste}.parquet'

        self.user = user
        self.run_id_train = run_id_train
        self.run_id_teste = run_id_teste
        self.date = datetime.date.today()
        self.process_type = process_type
        """Avaliar necessidade de input"""
        pwd = os.getcwd()
        os.chdir(os.path.dirname(trainFile))
        trainData = pd.read_parquet(os.path.basename(trainFile))
        testeData = pd.read_parquet(os.path.basename(testeFile))
        os.chdir(pwd)
        print('DATASET LIDO')
        self.df = trainData
        self.test = testeData

        # self.user = user
        # self.run_id = run_id
        # self.date = datetime.date.today()
        # self.process_type = process_type
        # self.df = pd.read_parquet(f'./{run_id}.gzip')
        # self.df.reset_index(drop=True, inplace=True)

        """
        TESTES DE ERRO
        """
        if save_info:
            users = ['Wilgner', 'Max', 'Rodrigo', 'David']

            if self.user not in users:
                raise ValueError('User não é valido')

            # if not isinstance(self.df, pd.DataFrame):
            #     raise ValueError('VOCÊ NÃO INSERIU UM DATAFRAME VALIDO')

            """
            DICIONARIO DE INFORMAÇÕES
            """
            info = {
                'User': self.user,
                'Date': self.date,
                'Run_id_train': self.run_id_train,
                'Run_id_teste': self.run_id_teste,
                'NLP_Process_type': self.process_type,
            }
            file = open(f"./Model/informações/{run_id_train}.txt", "wb")
            pickle.dump(info, file)

    def cria_data_sintetica(self, n_amostras_sinteticas=0, percent_df=.25, criar_base_randomica=False, random_state=False):

        # Criando amostras
        amostras_de_df = []
        if n_amostras_sinteticas > 0 and criar_base_randomica:
            for i in range(n_amostras_sinteticas):
                unique_identifier = self.df['unique_identifier']
                self.df_sem_unique = self.df.drop(columns='unique_identifier')
                df_outras_colunas = self.df_sem_unique.sample(
                    frac=percent_df, replace=True, axis=1).copy()
                df_amostra = pd.concat(
                    [unique_identifier, df_outras_colunas], axis=1)
                sintetico = pd.DataFrame()
                print(df_amostra.shape)
                df_amostra = df_amostra.loc[:, ~
                                            df_amostra.columns.duplicated()]
                # Criando parte sintetica
                for coluna in df_amostra.columns.tolist():

                    sintetico[coluna] = df_amostra[coluna].sample(
                        frac=1, replace=True, random_state=random_state).tolist()
                sintetico['label'] = 1
                df_amostra['label'] = 0

                df_amostral = pd.concat(
                    [df_amostra, sintetico])
                df_amostra.reset_index(inplace=True, drop=True)
                amostras_de_df.append(df_amostral)

        self.amostras_criadas = amostras_de_df

    def train_lightGBM(self, boruta_percs=[10], thr_bor_good=.5, thr_bor_ok=.9, take_out_cols=False):
        # Declarando parametros para o treino e para o feat_select
        quantidade_dfs = len(self.amostras_criadas)
        x_list = []
        y_list = []
        col_lists = []
        model_list = []
        trained_models = []

        dfs = self.amostras_criadas
        for i in range(quantidade_dfs):
            numero_de_colunas = dfs[i].shape[1]

            self.Y = dfs[i]['label']
            self.X = dfs[i].drop(columns=['unique_identifier', 'label'])
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

    def make_similarity_matrix_network(self, percent_sample=0.1):
        """
        Makes the similarity matrix, currently the biggest time sink should be parallelled or made much faster in the
        near future

        :return:
        """
        # Criando amostra para matrix de similaridade
        self.df_random = self.df.sample(
            frac=percent_sample, replace=True, axis=0).copy()
        print(self.df_random.shape)
        # frame_list = []
        model_c = 0
        mm = set()
        #full_leafs = np.array
        """SERA UNIQUE_ID AQUI NO OFICIAL"""
        ids = self.df_random['unique_identifier'].tolist()
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
        print('CRIANDO EDGES')
        edges = []
        # Criando matriz de similaridade
        for cc1, i in tqdm(enumerate(raw_leafs), 'FOLHAS:'):
            if cc1 % 100 == 0:
                print(cc1, datetime.datetime.now())
            for cc2_, j in enumerate(raw_leafs[cc1 + 1:]):
                cc2 = cc2_ + cc1 + 1
                if (cc1, cc2) not in mm and (cc2, cc1) not in mm:
                    leaf_count = sum(i == j)
                    # TODO: Fix similarity matrix with the square root
                    edges += [(ids[cc1], ids[cc2],
                               leaf_count / len(raw_leafs[0]))]
                    mm.add((cc1, cc2))
        print('done with list values')

        # YOU ARE HERE
        G = nx.Graph()

        G.add_weighted_edges_from(edges)
        self.G = G

    def run_louvain_community_detection(self):
        """
        Runs the community detection part of the code, this could also be parallel in the future, would require some
        work but should run on a n log n time scale

        :return: Saves Clusters
        """

        # Cria louvain
        self.clusters = (community.best_partition(
            self.G, weight='weight', randomize=True))

    # TODO:
    # Criar df aletorio para matriz OK
    # Criar supervisão por resultado do cluster OK
    def classifica_agrupamento(self,  boruta_percs=[10], thr_bor_good=.5, thr_bor_ok=.9, take_out_cols=False):

        self.df_cluster = pd.DataFrame({'Rotulo': self.clusters.keys(),
                                        'Label': self.clusters.values()})
        print(f'Tamanho dos dados de cluster {self.df_cluster.shape}')
        self.train = self.df[self.df['unique_identifier'].isin(
            self.df_cluster.Rotulo.values.tolist())]
        self.train['label'] = self.df_cluster.Label.values.tolist()
        self.predict = self.test.drop(columns=['unique_identifier'])

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

    def desenha_cluster_no_edges(self):
        plt.figure(figsize=(12, 8), dpi=150)
        plt.title('Louvain Tets', fontsize=20, loc='left', pad=15)
        self.pos = nx.spring_layout(self.G)
        nx.draw_networkx_nodes(self.G, self.pos, self.clusters.keys(), node_size=150,
                               node_color=list(self.clusters.values()))
        # nx.draw_networkx_edges(self.G, pos, alpha=0.5)
        plt.show()

    def desenha_cluster_with_edges(self):
        plt.figure(figsize=(12, 8), dpi=150)
        plt.title('Louvain Tets', fontsize=20,
                  loc='left', pad=15, fontweight='bold')
        self.pos = nx.spring_layout(self.G)
        nx.draw_networkx_nodes(self.G, self.pos, self.clusters.keys(), node_size=150,
                               node_color=list(self.clusters.values()))
        nx.draw_networkx_edges(self.G, self.pos, edge_color='gray', alpha=0.3)
        plt.show()

    def plota_palavras_maiores(self, numero):
        for i in range(len(self.df_resultante.label.unique())):

            df_data = pd.DataFrame({'word': self.df_resultante[self.df_resultante.label == i].drop(columns=['label', 'unique_identifier']).sum(axis=0).nlargest(numero).index.tolist(),
                                    'value': self.df_resultante[self.df_resultante.label == i].drop(columns=['label', 'unique_identifier']).sum(axis=0).nlargest(numero).values.tolist()})

            fig = px.bar(df_data, x='word', y='value', color='value')
            fig.show()
