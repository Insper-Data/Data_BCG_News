import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Output, Input, State
from dash_callback_conglomerate import Router
from components.components import Dashboard
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
router = Router(app, True)

# default values -> Roda offline
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.config.suppress_callback_exceptions = True

componentes = Dashboard()
graficos = Graficos()
graficos.pega_conteudo_auxilar()
graficos.coleta_dados_do_json()
graficos.prepara_df_aux()

app.layout = html.Div(id='main',
                      children=[
                          html.Div(className='header', children=[
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
                          html.Div(className='container-main', children=[

                              html.Div(id='graficos', children=[

                              ]),
                              html.Div(id='graficos1', children=[

                              ]),
                              html.Div(id='graficos2', children=[

                              ]),
                              html.Div(id='graficos3', children=[

                              ]),
                              html.Div(id='graficos4', children=[

                              ]),
                              html.Div(id='graficos5', children=[

                              ]),
                              html.Div(id='graficos6', children=[

                              ]),
                              html.Div(id='graficos7', children=[

                              ]),
                              html.Div(id='graficos8', children=[

                              ]),
                              html.Div(id='graficos9', children=[

                              ]),
                          ]),

                      ])


## Callback
@app.callback([Output(component_id='graficos', component_property='children'),
               Output(component_id='graficos1', component_property='children'),
               Output(component_id='graficos2', component_property='children'),
               Output(component_id='graficos3', component_property='children'),
               Output(component_id='graficos4', component_property='children'),
               Output(component_id='graficos5', component_property='children'),
               Output(component_id='graficos6', component_property='children'),
               Output(component_id='graficos7', component_property='children'),
               Output(component_id='graficos8', component_property='children'),
               Output(component_id='graficos9', component_property='children'),],
              [Input(component_id='button_run', component_property='n_clicks'),],
              [State(component_id='termo-filtro', component_property='value'),
               State(component_id='local-filtro', component_property='value'),
               State(component_id='date-range', component_property='start_date'),
               State(component_id='date-range', component_property='end_date')],
              )
def printa_info(n_clicks, input_termo, input_local, data_inicial, data_final):
    ctx = dash.callback_context

    if not ctx.triggered:
        button_id = 'No clicks yet'
        raise dash.exceptions.PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        print(input_termo, input_local, data_inicial, data_final)

        graficos.executa_zeus(input_termo)
        graficos.roda_modelo(local=input_local,
                             data_start=data_inicial,
                             data_end=data_final)
        numero_de_clusters = graficos.cria_df_pronto()

        lista_fig = graficos.constroi_grafico_1(len(numero_de_clusters))
        lista_fig2 = graficos.constroi_grafico_2(10, len(numero_de_clusters))

        lista_fig3 = graficos.constroi_grafico_3(10, len(numero_de_clusters))


        lista_html = []
        for index in range(10):
            try:
                fig = lista_fig[index]
                fig2 = lista_fig2[index]
                fig3 = lista_fig3[index]
                lista_html.append([
                    html.Div(className='menu2', children=[
                        dcc.Graph(id=f'graph_{index}', figure=fig),
                    ]),
                    html.Div(className='menu2', children=[
                        dcc.Graph(id=f'graph_{index}', figure=fig2),

                    ]),
                    html.Div(className='menu2', children=[
                        html.Img(id=f'graph_{index}', src=fig3),

                    ]),

                ])
            except:
                lista_html.append(html.Div())



    return lista_html[0], lista_html[1], lista_html[2], lista_html[3], lista_html[4], lista_html[5], lista_html[6], \
           lista_html[7], lista_html[8]


router.register_callbacks()

if __name__ == '__main__':
    app.run_server(debug=False, dev_tools_hot_reload_interval=10000, dev_tools_hot_reload_watch_interval=10)
    # app.run_server()
