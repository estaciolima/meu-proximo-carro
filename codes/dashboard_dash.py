from dash import Dash, html, dcc, callback, Output, Input, dash_table
import plotly.express as px
import pandas as pd
from fipe_api import consultar_historico_modelo

df = pd.read_csv('datasets/lista_completa_fiat.csv')

app = Dash()

app.layout = html.Div([
    html.H2("Selecione o carro"),
    
    html.Label("Marca"),
    dcc.Dropdown(
        id='dropdown-marca',
        options=[{'label': marca, 'value': marca} for marca in df['Marca'].unique().tolist()],
        placeholder='Selecione uma marca'
    ),

    html.Label("Modelo"),
    dcc.Dropdown(id='dropdown-modelo', placeholder='Selecione um modelo'),

    html.Label("Ano Modelo"),
    dcc.Dropdown(id='dropdown-ano', placeholder='Selecione o ano'),

    html.Button("Coletar Dados e Gerar Gráfico", id="botao-coletar", n_clicks=0),

    dcc.Graph(id="grafico-linha", figure={})
])

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
    modelos = df[df['Marca']==marca]['Modelo'].unique().tolist()
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
    anos = df[
                (df['Marca'] == marca) &
                (df['Modelo'] == modelo)
            ]['Ano'].unique().tolist()
    
    return [{'label': str(ano), 'value': ano} for ano in anos], None

# Callback para executar a rotina e gerar gráfico
@app.callback(
    Output("grafico-linha", "figure"),
    Input("botao-coletar", "n_clicks"),
    Input('dropdown-ano', 'value'),
    Input('dropdown-marca', 'value'),
    Input('dropdown-modelo', 'value')
)
def atualizar_grafico(n_clicks, ano, marca, modelo):
    if n_clicks == 0 or ano is None:
        return {}  # Gráfico vazio inicialmente

    dff = df[
                    (df['Marca'] == marca) &
                    (df['Modelo'] == modelo) &
                    (df['Ano'] == ano)
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
