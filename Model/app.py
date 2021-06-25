import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
from dash_callback_conglomerate import Router
from components.components import Dashboard
import os
from graph import Graficos

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = external_stylesheets = [
    {
        "href": "href=https://fonts.googleapis.com/css2?"
                "family=Barlow+Semi+Condensed:wght@100&display=swap",
        "rel": "stylesheet",
    },
]

app = dash.Dash(__name__, prevent_initial_callbacks=False)

# router = Router(app, True)

# default values -> Roda offline
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.config.suppress_callback_exceptions = True

# Variavel usuario
user = 'Wilgner'

componentes = Dashboard()
graficos = Graficos()
graficos.pega_conteudo_auxilar()
graficos.coleta_dados_do_json()
graficos.prepara_df_aux()

app.layout = html.Div(id='main',
                      children=[
                          html.Div(className='header', children=[
                              html.Img(className='logo', src='./assets/logo.png'),
                              componentes.cria_header()

                          ]),
                          html.Div(className='menu',
                                   children=[
                                       html.Div(children=[
                                           html.Div(className='menu-title',
                                                    children='Termo de busca'),
                                           componentes.cria_dropdown_termo_de_busca()]),
                                       html.Div(children=[
                                           html.Div(className='menu-title',
                                                    children='Local'),
                                           componentes.cria_dropdown_estado(),
                                       ]),
                                       html.Div(children=[
                                           html.Div(className='menu-title',
                                                    children='Data'),
                                           componentes.input_data()
                                       ]),

                                   ]),
                          html.Div(className='run-button', children=[
                              componentes.cria_botao()
                          ]),
                          html.Div(id='container-main2', children=[]),
                      ])


def cria_graficos_dinamicos(numero_de_clusters):
    lista_fig = graficos.constroi_grafico_1(len(numero_de_clusters))
    lista_fig2 = graficos.constroi_grafico_2(10, len(numero_de_clusters))
    lista_fig3 = graficos.constroi_grafico_3(25, len(numero_de_clusters))
    lista_fig4 = graficos.constroi_grafico_4(len(numero_de_clusters))
    fig5 = graficos.constroi_grafico_5()
    fig6 = graficos.constroi_grafico_6()
    lista_html = []

    grafico5e6 = html.Div(className='menu3', children=[
        html.Div(id=f'graficos0', children=[
            html.Div(className='menu2', children=[
                dcc.Graph(figure=fig5)
            ]),
            html.Div(className='menu2', children=[
                dcc.Graph(figure=fig6)
            ]),
        ]),

    ])
    lista_html.append(grafico5e6)



    for index in range(len(lista_fig2)):
        '''try:'''
        fig = lista_fig[index]
        fig2 = lista_fig2[index]
        fig3 = lista_fig3[index]
        fig4 = lista_fig4[index]
        lista_html += [
            html.Div(className='menu3', children=[
                html.Div(className='titulo-cluster',
                         children=[html.H2(children=f'Cluster {index}')]),
                html.Div(id=f'graficos{index}', children=[

                    html.Div(className='menu2', children=[
                        dcc.Graph(id=f'graph_{index}', figure=fig),
                    ]),
                    html.Div(className='menu2', children=[
                        dcc.Graph(id=f'graph_{index}', figure=fig2),

                    ]),
                    html.Div(className='menu2', children=[
                        html.Img(id=f'graph_{index}', src=fig3),
                    ]),
                    html.Div(className='menu2', children=[
                        dcc.Graph(id=f'graph_{index}', figure=fig4),
                    ]),
                ]),
            ]),
        ]

    # print(len(lista_html))
    return lista_html


## Callback
@app.callback([Output(component_id='container-main2', component_property='children')],
              [Input(component_id='button_run', component_property='n_clicks'), ],
              [State(component_id='termo-filtro', component_property='value'),
               State(component_id='local-filtro', component_property='value'),
               State(component_id='date-range', component_property='start_date'),
               State(component_id='date-range', component_property='end_date'),
               State(component_id='container-main2', component_property='children')],
              )
def printa_info(n_clicks, input_termo, input_local, data_inicial, data_final, lista_html):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'No clicks yet'
        raise dash.exceptions.PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'button_run':
        print(input_termo, input_local, data_inicial, data_final)

        string_file_name = f'{input_termo}_{input_local}_{data_inicial.replace("-", "")}_{data_final.replace("-", "")}'

        graficos.executa_zeus(input_termo, user)
        graficos.zeus.valida_acesso_path_user()
        path_name = f'{graficos.zeus.path_user}Model//'
        os.chdir(os.path.dirname(path_name))
        file_dir = os.listdir()
        result = f'{string_file_name}.parquet'

        if result in file_dir:
            graficos.zeus.pega_variaveis(load_df=True, file_name_load=result)
            graficos.faz_agregacao(graficos.zeus.load_df, is_load=True)
            numero_de_clusters = graficos.cria_df_pronto()
            lista_html = cria_graficos_dinamicos(numero_de_clusters)

        else:
            graficos.executa_zeus(input_termo, user)
            graficos.roda_modelo(local=input_local,
                                 data_start=data_inicial,
                                 data_end=data_final)

            numero_de_clusters = graficos.cria_df_pronto()
            lista_html = cria_graficos_dinamicos(numero_de_clusters)
            path_name = f'{graficos.zeus.path_user}Model//'
            os.chdir(os.path.dirname(path_name))
            print(graficos.df_final)
            graficos.df_final.to_parquet(f'{string_file_name}.parquet')

        return [lista_html]


'''            except:
                lista_html.append(html.Div())'''

# router.register_callbacks()

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload_interval=10000, dev_tools_hot_reload_watch_interval=10)
    # app.run_server()
