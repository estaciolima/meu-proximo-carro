from __future__ import annotations

import sys
from pathlib import Path

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])


PAGE_STYLE = {
    "minHeight": "100vh",
    "background": "#f4f7fb",
    "color": "#243447",
    "fontFamily": "Inter, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
}

SURFACE_STYLE = {
    "background": "#ffffff",
    "border": "1px solid #dfe7f1",
    "borderRadius": "8px",
    "boxShadow": "0 8px 28px rgba(36, 52, 71, 0.08)",
}

CONTROL_STYLE = {
    **SURFACE_STYLE,
    "padding": "18px",
    "marginBottom": "20px",
}


def build_layout():
    return html.Main(
        dbc.Container(
            [
                html.Section(
                    [
                        html.Div(
                            [
                                html.P(
                                    "Dashboard de compra inteligente",
                                    style={
                                        "textTransform": "uppercase",
                                        "fontSize": "12px",
                                        "fontWeight": 700,
                                        "letterSpacing": "0.08em",
                                        "color": "#2f80ed",
                                        "marginBottom": "6px",
                                    },
                                ),
                                html.H1(
                                    "Meu Proximo Carro",
                                    style={"fontWeight": 800, "marginBottom": "8px", "color": "#1d2b3a"},
                                ),
                                html.P(
                                    "Compare anuncios reais com referencia FIPE declarada no anuncio e veja rapidamente se o preco faz sentido.",
                                    style={"fontSize": "17px", "maxWidth": "780px", "color": "#526173", "margin": 0},
                                ),
                            ]
                        ),
                        html.Div(
                            [
                                metric_pill(f"{len(df_listings)} anuncios", "amostra local"),
                                metric_pill(f"{df_listings['fabricante'].nunique()} marcas", "disponiveis"),
                                *(
                                    [metric_pill("rode o crawler", "sem dados locais")]
                                    if df_listings.empty
                                    else []
                                ),
                            ],
                            style={"display": "flex", "gap": "10px", "flexWrap": "wrap"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "space-between",
                        "gap": "20px",
                        "alignItems": "flex-start",
                        "padding": "28px 0 22px",
                    },
                ),
                html.Section(
                    [
                        html.Div(
                            [
                                html.Label("Marca", className="filter-label"),
                                dcc.Dropdown(
                                    id="dropdown-marca",
                                    options=[
                                        {"label": marca, "value": marca}
                                        for marca in sorted(df_listings["fabricante"].dropna().unique())
                                    ],
                                    placeholder="Selecione uma marca",
                                ),
                            ],
                            className="filter-control",
                        ),
                        html.Div(
                            [
                                html.Label("Modelo", className="filter-label"),
                                dcc.Dropdown(id="dropdown-modelo", placeholder="Selecione um modelo"),
                            ],
                            className="filter-control",
                        ),
                        html.Div(
                            [
                                html.Label("Ano modelo", className="filter-label"),
                                dcc.Dropdown(id="dropdown-ano", placeholder="Selecione o ano"),
                            ],
                            className="filter-control",
                        ),
                    ],
                    style={
                        **CONTROL_STYLE,
                        "display": "grid",
                        "gridTemplateColumns": "repeat(auto-fit, minmax(220px, 1fr))",
                        "gap": "16px",
                    },
                ),
                dbc.Row(id="cards-resumo", className="g-3 mb-3"),
                dbc.Row(
                    [
                        dbc.Col(surface(dcc.Graph(id="grafico-precos", config={"displayModeBar": False})), lg=7),
                        dbc.Col(surface(dcc.Graph(id="grafico-km", config={"displayModeBar": False})), lg=5),
                    ],
                    className="g-3 mb-3",
                ),
                surface(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3("Anuncios filtrados", style={"fontSize": "20px", "fontWeight": 800}),
                                        html.P(
                                            "Use a tabela para auditar os veiculos que alimentam os indicadores.",
                                            style={"color": "#687789", "margin": 0},
                                        ),
                                    ]
                                ),
                                html.Div(id="status-amostra", style={"color": "#526173", "fontWeight": 700}),
                            ],
                            style={
                                "display": "flex",
                                "justifyContent": "space-between",
                                "gap": "16px",
                                "alignItems": "center",
                                "marginBottom": "14px",
                            },
                        ),
                        dash_table.DataTable(
                            id="tabela-anuncios",
                            page_size=8,
                            style_table={"overflowX": "auto"},
                            style_cell={
                                "textAlign": "left",
                                "fontFamily": "Inter, system-ui, sans-serif",
                                "fontSize": 13,
                                "padding": "10px",
                                "border": "0",
                            },
                            style_header={
                                "fontWeight": "700",
                                "backgroundColor": "#f1f5fa",
                                "border": "0",
                                "color": "#344256",
                            },
                            style_data_conditional=[
                                {"if": {"row_index": "odd"}, "backgroundColor": "#fbfdff"},
                            ],
                        ),
                    ],
                    padding="18px",
                ),
            ],
            fluid=True,
            style={"padding": "0 24px 32px", "maxWidth": "1440px"},
        ),
        style=PAGE_STYLE,
    )


def summary_card(title: str, value: str, subtitle: str, tone: str = "default"):
    colors = {
        "default": ("#2f80ed", "#edf5ff"),
        "good": ("#1f9d55", "#ecfdf3"),
        "warning": ("#c27803", "#fff7e6"),
        "muted": ("#687789", "#f3f6fa"),
    }
    color, background = colors.get(tone, colors["default"])
    return dbc.Col(
        dbc.Card(
            dbc.CardBody(
                [
                    html.Div(style={"width": "36px", "height": "4px", "background": color, "borderRadius": "8px"}),
                    html.H5(title, style={"fontSize": "15px", "fontWeight": 800, "color": "#526173", "marginTop": "14px"}),
                    html.P(value, style={"fontSize": "28px", "fontWeight": 800, "color": "#1d2b3a", "margin": "0 0 4px"}),
                    html.P(subtitle, style={"fontSize": "13px", "color": "#687789", "margin": 0}),
                ]
            ),
            style={**SURFACE_STYLE, "background": f"linear-gradient(180deg, {background}, #ffffff 58%)"},
        ),
        md=3,
    )


def metric_pill(value: str, label: str):
    return html.Div(
        [html.Strong(value, style={"display": "block"}), html.Span(label, style={"fontSize": "12px", "color": "#687789"})],
        style={**SURFACE_STYLE, "padding": "10px 14px", "minWidth": "130px"},
    )


def surface(children, padding: str = "0"):
    return html.Div(children, style={**SURFACE_STYLE, "padding": padding, "height": "100%"})


def build_price_figure(dff: pd.DataFrame, fipe_atual):
    if dff.empty:
        return empty_figure("Distribuicao de precos")

    fig = px.histogram(
        dff,
        x="valor",
        nbins=max(4, min(12, len(dff))),
        title="Distribuicao de precos",
        labels={"valor": "Preco anunciado"},
        color_discrete_sequence=["#2f80ed"],
    )
    if fipe_atual and not pd.isna(fipe_atual):
        fig.add_vline(
            x=fipe_atual,
            line_width=2,
            line_dash="dash",
            line_color="#1f9d55",
            annotation_text="FIPE",
            annotation_position="top right",
        )
    return polish_figure(fig)


def build_km_figure(dff: pd.DataFrame):
    if dff.empty:
        return empty_figure("Preco por quilometragem")

    fig = px.scatter(
        dff,
        x="km",
        y="valor",
        color="fabricante",
        hover_data=["modelo", "versao", "ano", "cidade"],
        title="Preco por quilometragem",
        labels={"km": "Quilometragem", "valor": "Preco anunciado", "fabricante": "Marca"},
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    fig.update_traces(marker={"size": 11, "line": {"width": 1, "color": "#ffffff"}})
    return polish_figure(fig)


def empty_figure(title: str):
    fig = go.Figure()
    fig.update_layout(title=title, annotations=[{"text": "Sem dados para este filtro", "showarrow": False}])
    return polish_figure(fig)


def polish_figure(fig):
    fig.update_layout(
        template="plotly_white",
        title={"font": {"size": 18, "color": "#1d2b3a"}},
        margin={"l": 38, "r": 18, "t": 58, "b": 42},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font={"family": "Inter, system-ui, sans-serif", "color": "#344256"},
        legend={"orientation": "h", "y": -0.22},
    )
    fig.update_xaxes(showgrid=True, gridcolor="#edf2f7", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#edf2f7", zeroline=False)
    return fig


def format_table_data(dff: pd.DataFrame) -> pd.DataFrame:
    table_df = dff.copy()
    table_df["preco_formatado"] = table_df["valor"].apply(_format_brl)
    table_df["fipe_formatado"] = table_df["valor_fipe"].apply(_format_brl)
    table_df["diferenca_formatada"] = table_df.apply(_row_difference, axis=1)
    table_df["km_formatado"] = table_df["km"].apply(_format_km)
    return table_df


def _row_difference(row):
    if pd.isna(row.get("valor")) or pd.isna(row.get("valor_fipe")) or not row.get("valor_fipe"):
        return "N/D"
    return _format_percent((row["valor"] - row["valor_fipe"]) / row["valor_fipe"] * 100)


def _format_brl(value):
    if value is None or pd.isna(value):
        return "N/D"
    return f"R$ {value:,.0f}".replace(",", ".")


def _format_percent(value):
    if value is None or pd.isna(value):
        return "N/D"
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f}%"


def _format_km(value):
    if value is None or pd.isna(value):
        return "N/D"
    return f"{value:,.0f} km".replace(",", ".")


def _difference_tone(value):
    if value is None or pd.isna(value):
        return "muted"
    if value <= 0:
        return "good"
    if value <= 5:
        return "default"
    return "warning"


def _difference_hint(value):
    if value is None or pd.isna(value):
        return "FIPE indisponivel neste filtro"
    if value <= 0:
        return "abaixo ou igual a FIPE"
    if value <= 5:
        return "proximo da referencia"
    return "acima da referencia"


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
    Output("status-amostra", "children"),
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

    preco_mediano = dff["valor"].median() if not dff.empty else None
    preco_minimo = dff["valor"].min() if not dff.empty else None
    km_mediano = dff["km"].median() if not dff.empty else None
    fipe_atual = dff["valor_fipe"].dropna().mean() if "valor_fipe" in dff.columns and not dff.empty else None
    diferenca = ((preco_mediano - fipe_atual) / fipe_atual * 100) if fipe_atual and preco_mediano else None

    cards = [
        summary_card("Preco mediano", _format_brl(preco_mediano), f"{len(dff)} anuncio(s) no filtro"),
        summary_card("FIPE Mobiauto", _format_brl(fipe_atual), "media dos anuncios com FIPE"),
        summary_card("Acima da FIPE", _format_percent(diferenca), _difference_hint(diferenca), tone=_difference_tone(diferenca)),
        summary_card("Menor preco", _format_brl(preco_minimo), f"KM mediano {_format_km(km_mediano)}"),
    ]

    fig_precos = build_price_figure(dff, fipe_atual)
    fig_km = build_km_figure(dff)

    table_df = format_table_data(dff)
    columns = [
        {"name": label, "id": column}
        for column, label in {
            "fabricante": "Marca",
            "modelo": "Modelo",
            "versao": "Versao",
            "ano": "Ano",
            "preco_formatado": "Preco",
            "fipe_formatado": "FIPE",
            "diferenca_formatada": "Dif.",
            "km_formatado": "KM",
            "cidade": "Cidade",
            "cambio": "Cambio",
            "combustivel": "Combustivel",
        }.items()
    ]
    status = f"{len(dff)} anuncio(s) exibido(s)"
    return cards, fig_precos, fig_km, table_df[[column["id"] for column in columns]].to_dict("records"), columns, status


if __name__ == "__main__":
    app.run(debug=True)
