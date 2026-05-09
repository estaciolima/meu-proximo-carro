from __future__ import annotations

import sys
from pathlib import Path

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dash_table, dcc, html


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from meu_proximo_carro.database import connect_sqlite, init_sqlite_db


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    connection = connect_sqlite()
    init_sqlite_db(connection)
    listings = pd.read_sql_query("SELECT * FROM mobiauto_listings", connection)
    fipe_prices = pd.read_sql_query("SELECT * FROM fipe_prices", connection)
    return listings, fipe_prices


df_listings, df_fipe_prices = load_data()
app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])


def build_layout():
    if df_listings.empty:
        return dbc.Container(
            [
                html.H2("Meu Proximo Carro"),
                html.P("Banco local sem anuncios."),
                html.Code("python3 scripts/populate_sample_db.py --limit 3"),
            ],
            fluid=True,
            style={"padding": "24px"},
        )

    return dbc.Container(
        [
            html.H2("Meu Proximo Carro"),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Marca"),
                            dcc.Dropdown(
                                id="dropdown-marca",
                                options=[
                                    {"label": marca, "value": marca}
                                    for marca in sorted(df_listings["fabricante"].dropna().unique())
                                ],
                                placeholder="Selecione uma marca",
                            ),
                        ],
                        style={"width": "32%"},
                    ),
                    html.Div(
                        [
                            html.Label("Modelo"),
                            dcc.Dropdown(id="dropdown-modelo", placeholder="Selecione um modelo"),
                        ],
                        style={"width": "32%"},
                    ),
                    html.Div(
                        [
                            html.Label("Ano modelo"),
                            dcc.Dropdown(id="dropdown-ano", placeholder="Selecione o ano"),
                        ],
                        style={"width": "32%"},
                    ),
                ],
                style={"display": "flex", "gap": "16px", "marginBottom": "24px"},
            ),
            dbc.Row(id="cards-resumo", className="mb-4"),
            dbc.Row(
                [
                    dbc.Col(dcc.Graph(id="grafico-precos"), md=6),
                    dbc.Col(dcc.Graph(id="grafico-km"), md=6),
                ]
            ),
            html.H4("Anuncios"),
            dash_table.DataTable(
                id="tabela-anuncios",
                page_size=8,
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left", "fontFamily": "Arial", "fontSize": 13},
            ),
        ],
        fluid=True,
        style={"padding": "24px"},
    )


app.layout = build_layout


@app.callback(
    Output("dropdown-modelo", "options"),
    Output("dropdown-modelo", "value"),
    Input("dropdown-marca", "value"),
)
def atualizar_modelos(marca):
    if not marca:
        return [], None
    modelos = sorted(df_listings[df_listings["fabricante"] == marca]["modelo"].dropna().unique())
    return [{"label": modelo, "value": modelo} for modelo in modelos], None


@app.callback(
    Output("dropdown-ano", "options"),
    Output("dropdown-ano", "value"),
    Input("dropdown-marca", "value"),
    Input("dropdown-modelo", "value"),
)
def atualizar_anos(marca, modelo):
    if not marca or not modelo:
        return [], None
    dff = df_listings[(df_listings["fabricante"] == marca) & (df_listings["modelo"] == modelo)]
    anos = sorted(dff["ano_modelo"].dropna().astype(int).unique())
    return [{"label": str(ano), "value": int(ano)} for ano in anos], None


@app.callback(
    Output("cards-resumo", "children"),
    Output("grafico-precos", "figure"),
    Output("grafico-km", "figure"),
    Output("tabela-anuncios", "data"),
    Output("tabela-anuncios", "columns"),
    Input("dropdown-marca", "value"),
    Input("dropdown-modelo", "value"),
    Input("dropdown-ano", "value"),
)
def atualizar_dashboard(marca, modelo, ano):
    dff = df_listings.copy()
    if marca:
        dff = dff[dff["fabricante"] == marca]
    if modelo:
        dff = dff[dff["modelo"] == modelo]
    if ano:
        dff = dff[dff["ano_modelo"] == ano]

    preco_medio = dff["valor"].mean() if not dff.empty else 0
    km_medio = dff["km"].mean() if not dff.empty else 0
    fipe_atual = df_fipe_prices["valor"].dropna().iloc[-1] if not df_fipe_prices.empty else None
    diferenca = ((preco_medio - fipe_atual) / fipe_atual * 100) if fipe_atual else None

    cards = [
        summary_card("Preco medio anuncios", _format_brl(preco_medio)),
        summary_card("Preco FIPE sample", _format_brl(fipe_atual)),
        summary_card("Diferenca", f"{diferenca:.1f}%" if diferenca is not None else "N/D"),
        summary_card("KM medio", f"{km_medio:,.0f}".replace(",", ".")),
    ]

    fig_precos = px.histogram(dff, x="valor", title="Distribuicao de precos dos anuncios")
    fig_km = px.scatter(dff, x="km", y="valor", color="cidade", title="Preco por quilometragem")

    columns = [
        {"name": label, "id": column}
        for column, label in {
            "fabricante": "Marca",
            "modelo": "Modelo",
            "versao": "Versao",
            "ano": "Ano",
            "valor": "Preco",
            "km": "KM",
            "cidade": "Cidade",
            "cambio": "Cambio",
            "combustivel": "Combustivel",
        }.items()
    ]
    return cards, fig_precos, fig_km, dff[[column["id"] for column in columns]].to_dict("records"), columns


def summary_card(title: str, value: str):
    return dbc.Col(
        dbc.Card(dbc.CardBody([html.H5(title, className="card-title"), html.P(value)])),
        md=3,
    )


def _format_brl(value):
    if value is None or pd.isna(value):
        return "N/D"
    return f"R$ {value:,.0f}".replace(",", ".")


if __name__ == "__main__":
    app.run(debug=True)
