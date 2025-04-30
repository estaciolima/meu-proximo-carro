from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
from fipe_api import consultar_historico_modelo
import dash_bootstrap_components as dbc

df_fipe = pd.read_csv('datasets/lista_completa_fiat.csv')
df_seminovos = pd.read_csv('datasets/database_cleaned-1716945632.246805.csv')
df_seminovos['ModeloVersao'] = df_seminovos.apply(lambda row: row['Modelo']+''+row['Versao'], axis=1)

external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H2("Selecione o carro"),
    
    html.Div([
        html.Div([
            html.Label("Marca"),
            dcc.Dropdown(
                id='dropdown-marca',
                options=[{'label': marca, 'value': marca} for marca in df_fipe['Marca'].unique().tolist()],
                placeholder='Selecione uma marca'
            ),
        ], style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Modelo"),
            dcc.Dropdown(id='dropdown-modelo', placeholder='Selecione um modelo')
        ], style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Ano Modelo"),
            dcc.Dropdown(id='dropdown-ano', placeholder='Selecione o ano')
        ], style={'width': '30%', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justify-content': 'space-between', 'margin-bottom': '20px'}),

    html.Div([
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Preço Médio FIPE", className="card-title"),
                    html.P("$$$$", className="card-text")
                ])
            ]), width=3),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Preço Médio Anúncios", className="card-title"),
                    html.P("$$$$", className="card-text")
                ])
            ]), width=3),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("Diferença", className="card-title"),
                    html.P("-%", className="card-text")
                ])
            ]), width=3),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.H4("!", className="card-title"),
                    html.P("Mais barato que a fipe!", className="card-text")
                ])
            ]), width=3),
        ], justify="between", style={'margin-bottom': '20px'})
    ]),

    dcc.Loading(
        id="loading-grafico",
        type="circle",  # ou "default", "dot"
        children=[
            dcc.Graph(id="grafico-linha", figure={})
        ]
    )
    
], style={'margin-left': '20%', 'margin-right': '20%', 'padding': '20px', 'border': '1px solid #ccc', 'border-radius': '10px', 'background-color': '#f9f9f9'})

# Callback para atualizar os modelos com base na marca
@app.callback(
    Output('dropdown-modelo', 'options'),
    Output('dropdown-modelo', 'value'),
    # Output('dropdown-ano', 'options'),
    # Output('dropdown-ano', 'value'),
    Input('dropdown-marca', 'value')
)
def atualizar_modelos(marca):
    if marca is None:
        return [], None#, [], None
    modelos = df_fipe[df_fipe['Marca']==marca]['Modelo'].unique().tolist()
    return [{'label': modelo, 'value': modelo} for modelo in modelos], None #, [], None


# Callback para atualizar os anos com base no modelo
@app.callback(
    Output('dropdown-ano', 'options'),
    Output('dropdown-ano', 'value'),
    Input('dropdown-marca', 'value'),
    Input('dropdown-modelo', 'value')
)
def atualizar_anos(marca, modelo):
    if marca is None or modelo is None:
        return [], None
    
    anos = df_fipe[
                (df_fipe['Marca'] == marca) &
                (df_fipe['Modelo'] == modelo)
            ]['Ano'].unique().tolist()
    
    return [{'label': str(ano), 'value': ano} for ano in anos], None

# Callback para executar a rotina e gerar gráfico
@app.callback(
    Output("grafico-linha", "figure"),
    #Input("botao-coletar", "n_clicks"),
    Input('dropdown-ano', 'value'),
    Input('dropdown-marca', 'value'),
    Input('dropdown-modelo', 'value')
)
def atualizar_grafico(ano, marca, modelo):
    if ano is None or marca is None or modelo is None:
        return {}

    dff = df_fipe[
                    (df_fipe['Marca'] == marca) &
                    (df_fipe['Modelo'] == modelo) &
                    (df_fipe['Ano'] == ano)
                ]

    df_historico = consultar_historico_modelo(
                        str(dff['Código Marca'].values[0]),
                        str(dff['Código Modelo'].values[0]),
                        dff['Código Ano'].values[0],
                        tabela_ref='320'
                    )
    
    df_historico['Valor'] = df_historico['Valor'].apply(
                        lambda x: float(x.split()[1].replace('.', '').replace(',', '.'))
                    )

    fig = px.line(df_historico, x='MesReferencia', y='Valor',
                    title='Variação de valor ao longo do tempo', markers=True)
    
    return fig


if __name__ == '__main__':
    app.run(debug=True)
