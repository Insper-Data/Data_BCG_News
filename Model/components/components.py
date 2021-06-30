import dash_html_components as html
import dash_core_components as dcc
from datetime import date

class Dashboard:
    def __init__(self) -> None:
        pass

    def cria_header(self):
        return html.H1(className='titulo',
                       children='Clusterização Nacional de Notícias'
                       )

    def cria_dropdown_termo_de_busca(self):
        return dcc.Dropdown(id="termo-filtro",
                            options=[
                                {'label': 'Bolsonaro', 'value': 'Bolsonaro'},
                                {'label': 'Lula', 'value': 'Lula'},
                                {'label': 'Neymar', 'value': 'Neymar'},

                            ],

                            value='TUDO',
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            )

    def cria_dropdown_estado(self):
        lista_estados = ['Acre',
                         'Alagoas',
                         'Amapa',
                         'Amazonas',
                         'Bahia',
                         'Ceara',
                         'Distrito Federal',
                         'Espirito Santo',
                         'Goias',
                         'Maranhao',
                         'Mato Grosso',
                         'Mato Grosso do Sul',
                         'Minas Gerais',
                         'Para',
                         'Paraiba',
                         'Parana',
                         'Pernambuco',
                         'Piaui',
                         'Rio de Janeiro',
                         'Rio Grande do Norte',
                         'Rio Grande do Sul',
                         'Rondonia',
                         'Roraima',
                         'Santa Catarina',
                         'Sao Paulo',
                         'Sergipe',
                         'Tocantins',
                         'Todos']
        lista_de_siglas = ['AC',
                           'AL',
                           'AP',
                           'AM',
                           'BA',
                           'CE',
                           'DF',
                           'ES',
                           'GO',
                           'MA',
                           'MT',
                           'MS',
                           'MG',
                           'PA',
                           'PB',
                           'PR',
                           'PE',
                           'PI',
                           'RJ',
                           'RN',
                           'RS',
                           'RO',
                           'RR',
                           'SC',
                           'SP',
                           'SE',
                           'TO',
                           'TUDO']
        lista_de_label = ['label' for i in range(len(lista_estados))]
        dropdown_list = []
        for index, _ in enumerate(lista_de_label):
            keys = ['label', 'value']
            values = [lista_estados[index], lista_de_siglas[index]]

            dropdown_list.append(dict(zip(keys, values)))
        return dcc.Dropdown(id="local-filtro",
                            options=dropdown_list,

                            value='TUDO',
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                            )

    def input_data(self):
        return dcc.DatePickerRange(id="date-range",
                                   start_date_placeholder_text="Data Inicial",
                                   end_date_placeholder_text="Data Final",
                                   calendar_orientation='vertical',
                                   start_date=date(2020,1,1),
                                   end_date=date(2021,1,1)

                                   )

    def cria_botao(self):
        return html.Button('Rodar Modelo', className='button', id='button_run',n_clicks=0
                           )

