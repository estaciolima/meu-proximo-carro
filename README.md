# Meu Proximo Carro

Projeto de coleta, preparacao e visualizacao de dados de carros usados no Brasil. O repositorio combina web scraping de anuncios, consultas a Tabela FIPE, tratamento de dados, embeddings para aproximar nomes de modelos e dashboards para apoiar a analise de preco de veiculos.

## Objetivo

A ideia central e ajudar na comparacao entre precos anunciados e referencias FIPE, especialmente para identificar oportunidades de compra de carros usados. O projeto hoje cobre:

- coleta de anuncios de carros usados na Mobiauto;
- extracao de atributos do veiculo, como fabricante, modelo, versao, preco, quilometragem, cambio, combustivel e opcionais;
- limpeza e enriquecimento dos dados coletados;
- consulta historica de precos pela API da Tabela FIPE;
- matching semantico entre nomes de modelos usando `sentence-transformers`;
- dashboards em Dash e Streamlit para exploracao visual.

## Estrutura do projeto

```text
.
├── dashboard/
│   ├── dashboard_dash.py          # Dashboard experimental em Plotly Dash
│   ├── dashboard_streamlit.py     # Dashboard Streamlit para serie historica FIPE
│   └── mockups/                   # Imagens de referencia para layout
├── data/
│   ├── lookup/                    # Tabelas auxiliares da FIPE e modelos
│   ├── processed/                 # Bases tratadas e embeddings
│   └── raw/                       # Bases brutas coletadas
├── notebooks/
│   ├── dashboard_preparation.ipynb
│   ├── exploratory_data_analysis.ipynb
│   └── serie_temporal_carro.ipynb
├── scripts/
│   ├── car_crawler.py             # Extrai dados de uma pagina de anuncio
│   ├── links_crawler.py           # Coleta links de anuncios e gera CSV bruto
│   ├── helpers.py                 # Funcoes de limpeza, coleta de links e embeddings
│   ├── fipe_api.py                # Funcoes para consultar a API da FIPE
│   ├── create_db.py               # Carga experimental em MySQL
│   ├── create_car_database.py     # Script legado para montar base a partir de links
│   └── config.py                  # Headers HTTP usados no scraping
└── database-*.csv                 # Saidas pontuais de coleta
```

## Pipeline de dados

1. `scripts/links_crawler.py` acessa uma pagina de busca da Mobiauto, coleta links de anuncios e chama `car_crawler`.
2. `scripts/car_crawler.py` extrai os campos principais da pagina do veiculo e retorna um dicionario pronto para virar `DataFrame`.
3. `scripts/helpers.py` prepara a base com limpeza de duplicados, conversao de preco para numero, criacao de ano de fabricacao/modelo e tratamento de valores ausentes.
4. `scripts/fipe_api.py` consulta marcas, modelos, anos e historico mensal de precos na FIPE.
5. Os notebooks em `notebooks/` fazem analise exploratoria, preparacao para dashboard e estudos de serie temporal.
6. Os dashboards em `dashboard/` apresentam seletores de marca/modelo/ano e graficos de evolucao de preco.

## Principais bases

- `data/raw/database-*.csv`: dados brutos coletados de anuncios.
- `data/processed/database_cleaned.csv`: base limpa para analise.
- `data/processed/database-dashboard.csv`: base preparada para visualizacao.
- `data/lookup/lista_completa_fiat.csv`: combinacoes de marca, modelo e ano da FIPE para Fiat.
- `data/lookup/lista_completa.csv`: tabela auxiliar mais ampla de modelos FIPE.
- `data/lookup/nomes_fipe.csv`: nomes de modelos usados no matching semantico.
- `data/processed/embeddings/embeddings.parquet`: embeddings dos nomes de modelos.

## Requisitos

O repositorio nao possui um arquivo `requirements.txt` no momento. Pelos imports atuais, as principais dependencias sao:

```bash
pip install pandas beautifulsoup4 requests unidecode sqlalchemy mysql-connector-python
pip install streamlit dash dash-bootstrap-components plotly
pip install torch sentence-transformers pyarrow openpyxl
```

Opcionalmente, crie um ambiente virtual antes de instalar:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

## Como usar

### Coletar anuncios

```bash
python scripts/links_crawler.py
```

O script gera um CSV `database-<timestamp>.csv` com os anuncios encontrados. A URL inicial esta definida dentro de `scripts/links_crawler.py`.

### Consultar FIPE via Python

```python
from scripts.fipe_api import consultar_historico_modelo

df = consultar_historico_modelo(
    codigo_marca="21",
    codigo_modelo="5273",
    codigo_ano="2011-1",
    tabela_ref="320",
)
```

### Rodar o dashboard Streamlit

```bash
streamlit run dashboard/dashboard_streamlit.py
```

### Rodar o dashboard Dash

```bash
python dashboard/dashboard_dash.py
```

## Observacoes de desenvolvimento

- Alguns scripts ainda referenciam caminhos antigos como `datasets/` e `embeddings/`, enquanto a estrutura atual usa `data/lookup`, `data/raw` e `data/processed`. Antes de executar esses scripts de ponta a ponta, pode ser necessario ajustar os caminhos.
- `scripts/car_crawler.py` altera o diretorio de trabalho para a propria pasta `scripts/`, o que influencia caminhos relativos.
- O scraping depende da estrutura HTML da Mobiauto; mudancas nas classes CSS do site podem quebrar a extracao.
- As consultas a FIPE podem receber limitacao de taxa. Algumas funcoes ja usam espera exponencial ou pausas entre requisicoes.
- Ha um ambiente virtual versionado em `myenv/`; em novos clones, prefira criar um ambiente local novo.

## Proximos passos sugeridos

- Criar `requirements.txt` ou `pyproject.toml`.
- Padronizar todos os caminhos para a estrutura `data/`.
- Remover codigo legado/comentado ou mover experimentos para notebooks.
- Adicionar testes para conversao de valores, limpeza de dados e consultas FIPE.
- Parametrizar URLs, cidade e marca/modelo por argumentos de linha de comando ou arquivo de configuracao.
