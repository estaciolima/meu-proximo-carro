import streamlit as st
import pandas as pd
import plotly.express as px
from fipe_api import 

# Carregar dados
df = pd.read_csv('Lista de marcas e modelos.csv')

# Interface do usuário
st.title("Análise de Série Temporal por Veículo")

# Dropdown 1: Marca
marca_selecionada = st.selectbox("Selecione a marca", df['Marca'].unique())

# Filtra os modelos disponíveis com base na marca
modelos_disponiveis = df[df['marca'] == marca_selecionada]['Modelo'].unique()
modelo_selecionado = st.selectbox("Selecione o modelo", modelos_disponiveis)

# Filtra os anos disponíveis com base no modelo
anos_disponiveis = df[
    (df['marca'] == marca_selecionada) &
    (df['modelo'] == modelo_selecionado)
]['ano_modelo'].unique()

ano_selecionado = st.selectbox("Selecione o ano modelo", anos_disponiveis)

# Filtra os dados finais para o gráfico
df_filtrado = df[
    (df['marca'] == marca_selecionada) &
    (df['modelo'] == modelo_selecionado) &
    (df['ano_modelo'] == ano_selecionado)
]

# Gera o gráfico de série temporal
if not df_filtrado.empty:
    fig = px.line(df_filtrado, x='mes', y='valor', title='Variação de Valor ao Longo dos Meses')
    st.plotly_chart(fig)
else:
    st.warning("Nenhum dado disponível para essa seleção.")