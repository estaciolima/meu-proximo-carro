import streamlit as st
import pandas as pd
import plotly.express as px
from fipe_api import consultar_historico_modelo


@st.cache_data # se função com os mesmos parâmetros, não chama de novo
def consultar_valores_fipe(cod_marca, cod_modelo, cod_ano, tabela_ref='320'):
    return consultar_historico_modelo(cod_marca, cod_modelo, cod_ano, tabela_ref)

# Carregar dados
df = pd.read_csv('lista_completa_fiat.csv')

# Interface do usuário
st.title("Análise de Série Temporal por Veículo")

# Menu de seleção com placeholder
marcas = ['Selecione uma marca'] + sorted(df['Marca'].unique().tolist())
marca_selecionada = st.selectbox("Marca", marcas)

if marca_selecionada != 'Selecione uma marca':
    modelos = ['Selecione um modelo'] + sorted(df[df['Marca'] == marca_selecionada]['Modelo'].unique().tolist())
    modelo_selecionado = st.selectbox("Modelo", modelos)

    if modelo_selecionado != 'Selecione um modelo':
        anos = ['Selecione um ano'] + sorted(
            df[
                (df['Marca'] == marca_selecionada) &
                (df['Modelo'] == modelo_selecionado)
            ]['Ano'].unique().tolist()
        )
        ano_selecionado = st.selectbox("Ano modelo", anos)

        if ano_selecionado != 'Selecione um ano':
            # Espera o clique no botão para gerar gráfico
            if st.button("Gerar gráfico"):
                df_filtrado = df[
                    (df['Marca'] == marca_selecionada) &
                    (df['Modelo'] == modelo_selecionado) &
                    (df['Ano'] == ano_selecionado)
                ]

                if not df_filtrado.empty:
                    df_historico = consultar_historico_modelo(
                        str(df_filtrado['Código Marca'].values[0]),
                        str(df_filtrado['Código Modelo'].values[0]),
                        df_filtrado['Código Ano'].values[0],
                        tabela_ref='320'
                    )

                    df_historico['Valor'] = df_historico['Valor'].apply(
                        lambda x: float(x.split()[1].replace('.', '').replace(',', '.'))
                    )

                    fig = px.line(df_historico, x='MesReferencia', y='Valor',
                                  title='Variação de valor ao longo do tempo', markers=True)
                    st.plotly_chart(fig)
                else:
                    st.warning("Nenhum dado encontrado para essa combinação.")