import json
import os
from urllib.request import urlopen

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
import sys
from plotly.tools import mpl_to_plotly
from configs import *
from model_v2 import *

import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt



class Graficos:
    def __init__(self):
        self.Brazil = ''
        self.state_id_map = {}
        self.dicionario_filtro = {'Acre': 'AC',
                                  'Alagoas': 'AL',
                                  'Amapá': 'AP',
                                  'Amazonas': 'AM',
                                  'Bahia': 'BA',
                                  'Ceará': 'CE',
                                  'Distrito Federal': 'DF',
                                  'Espírito Santo': 'ES',
                                  'Goiás': 'GO',
                                  'Maranhão': 'MA',
                                  'Mato Grosso': 'MT',
                                  'Mato Grosso do Sul': 'MS',
                                  'Minas Gerais': 'MG',
                                  'Pará': 'PA',
                                  'Paraíba': 'PB',
                                  'Paraná': 'PR',
                                  'Pernambuco': 'PE',
                                  'Piauí': 'PI',
                                  'Rio de Janeiro': 'RJ',
                                  'Rio Grande do Norte': 'RN',
                                  'Rio Grande do Sul': 'RS',
                                  'Rondônia': 'RO',
                                  'Roraima': 'RR',
                                  'Santa Catarina': 'SC',
                                  'São Paulo': 'SP',
                                  'Sergipe': 'SE',
                                  'Tocantins': 'TO'}
        self.df_aux = ''
        self.df = ''
        self.df2 = ''
        self.colors = ['Blues', 'BuGn', 'BuPu', 'Purples', 'PuRd', 'GnBu', 'Blues', 'BuGn', 'BuPu', 'Purples', 'PuRd',
                       'GnBu']
        self.zeus = ''

    def pega_conteudo_auxilar(self):
        with urlopen(
                'https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson') as response:
            self.Brazil = json.load(response)  # Javascrip object notation
        self.df_aux = pd.read_csv('https://raw.githubusercontent.com/nayanemaia/Dataset_Soja/main/soja%20sidra.csv')

    def executa_zeus(self, termo):

        termo = termo
        user = USERS['Wilgner']
        path_files = constroi_id(termo)
        treino_id = path_files[0]
        teste_id = path_files[1]

        print(treino_id, teste_id)

        self.zeus = Zeus(
            termo=termo,
            user=user,
            treino_id=treino_id,
            test_id=teste_id
        )

    def roda_modelo(self, local, data_start, data_end):

        if local == 'TUDO':
            local = False

        self.zeus.filtrar_treino(local=local,
                                 data_start=data_start,
                                 data_end=data_end)

        self.zeus.criar_base_sintetica(numero_de_amostras=NUMERO_DE_AMOSTRAS,
                                       porcentagem_para_criacao=PORCENTAGEM_PARA_CRIACAO)
        self.zeus.treina_lightGBM()

        self.zeus.rodando_louvain(porcentagem_do_sample=PORCENTAGEM_PARA_SAMPLE)

        self.zeus.pega_variaveis(teste=True)

        self.zeus.filtrar_teste(local=local,
                                data_start=data_start,
                                data_end=data_end)

        self.zeus.classifica_agrupamento()

        self.df = self.zeus.faz_agregacao()

    def coleta_dados_do_json(self):
        for feature in self.Brazil['features']:
            feature['id'] = feature['properties']['name']
            self.state_id_map[feature['properties']['sigla']] = feature['id']

    def prepara_df_aux(self):
        self.df_aux.Estado = self.df_aux.Estado.map(self.dicionario_filtro)
        self.df_aux.drop_duplicates(subset=['Estado'], inplace=True)
        self.df_aux.drop(['Unnamed: 5', 'Produção', 'ano'], axis=1, inplace=True)
        self.df_aux.set_index('Estado', inplace=True)

    def cria_df_pronto(self):
        self.df2 = pd.concat([self.df_aux, self.df], axis=1)
        self.df2.fillna(value=0, inplace=True)
        self.df2['Estado'] = self.df2.index
        self.df2['Estado'] = self.df2.Estado.map(self.state_id_map)
        colunas = self.df2.columns.tolist()
        numero_de_clusters = []
        map_clusters = {}
        for index, coluna in enumerate(colunas):
            if isinstance(coluna, int):
                map_clusters[coluna] = f'cluster {coluna}'
                numero_de_clusters.append(index)

        self.df2.rename(columns=map_clusters, inplace=True)

        return numero_de_clusters

    def constroi_grafico_1(self, n_cluster):

        lista_fig = []
        for numero in range(n_cluster):
            try:
                fig = px.choropleth(
                    data_frame=self.df2,
                    locations='Estado',
                    geojson=self.Brazil,
                    color=f'cluster {numero}',
                    hover_name='Estado',
                    hover_data=[f'cluster {numero}', "Longitude", "Latitude"],
                    color_continuous_scale=self.colors[numero]
                )
                fig.update_geos(fitbounds="locations", visible=False)
                fig.update_layout(title_text=f"Estados com mais noticias no cluster {numero}", title_x=0.5,
                                  coloraxis_colorbar_x=-0.15)
                lista_fig.append(fig)
            except:
                lista_fig.append('')
        return lista_fig

    def constroi_grafico_2(self, numero2, n_cluster):
        lista_fig = []
        for numero in range(n_cluster):
            try:
                df_data = pd.DataFrame({'word': self.zeus.var_teste[self.zeus.var_teste.label == numero].drop(
                    columns=['label']).sum(axis=0).nlargest(numero2).index.tolist(),
                                        'value': self.zeus.var_teste[self.zeus.var_teste.label == numero].drop(
                                            columns=['label']).sum(axis=0).nlargest(numero2).values.tolist()})

                fig = px.bar(df_data, x='word', y='value', color='value', color_continuous_scale=self.colors[numero])
                fig.update_layout(title_text=f"As palavras que mais aparecem no cluster {numero}", title_x=0.5, template='ggplot2')
                fig.update_xaxes(showgrid=False)
                fig.update_yaxes(showgrid=False)
                lista_fig.append(fig)

            except:
                lista_fig.append('')

        return lista_fig

    def plot_wordcloud(data):
        d = {a: x for a, x in data.values}
        wc = WordCloud()
        wc.generate_from_frequencies(frequencies=d)
        return wc

    def constroi_grafico_3(self, numero2, n_cluster):
        lista_fig = []
        for numero in range(n_cluster):
            try:
                df_data = pd.DataFrame({'word': self.zeus.var_teste[self.zeus.var_teste.label == numero].drop(
                    columns=['label']).sum(axis=0).nlargest(numero2).index.tolist(),
                                        'value': self.zeus.var_teste[self.zeus.var_teste.label == numero].drop(
                                            columns=['label']).sum(axis=0).nlargest(numero2).values.tolist()})

                nuvem = self.plot_wordcloud(df_data)
                fig = plt.figure(figsize=(10,10))
                ax = fig.add_axes([0,0,1,1])
                ax.imshow(nuvem,  interpolation="bilinear")
                plotly_fig = mpl_to_plotly(fig)
                lista_fig.append(plotly_fig)
            except:
                lista_fig.append('')

        return lista_fig
