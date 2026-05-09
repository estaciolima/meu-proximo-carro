# Meu Proximo Carro

Projeto de coleta, preparacao e visualizacao de dados de carros usados no Brasil. O repositorio combina web scraping de anuncios, consultas a Tabela FIPE, tratamento de dados, matching textual para aproximar nomes de modelos e dashboards para apoiar a analise de preco de veiculos.

## Objetivo

A ideia central e ajudar na comparacao entre precos anunciados e referencias FIPE, especialmente para identificar oportunidades de compra de carros usados. O projeto hoje cobre:

- coleta de anuncios de carros usados na Mobiauto;
- extracao de atributos do veiculo, como fabricante, modelo, versao, preco, quilometragem, cambio, combustivel e opcionais;
- limpeza e enriquecimento dos dados coletados;
- consulta historica de precos pela API da Tabela FIPE;
- matching textual entre nomes de modelos usando `RapidFuzz`;
- dashboard em Dash/Plotly para exploracao visual.

## Estrutura do projeto

```text
.
├── dashboard/
│   ├── app.py                     # Dashboard Dash/Plotly atual
│   └── mockups/                   # Imagens de referencia para layout
├── data/
│   ├── lookup/                    # Tabelas auxiliares da FIPE e modelos
│   ├── processed/                 # Bases tratadas
│   └── raw/                       # Bases brutas coletadas
├── notebooks/
│   ├── dashboard_preparation.ipynb
│   ├── exploratory_data_analysis.ipynb
│   └── serie_temporal_carro.ipynb
├── scripts/
│   ├── car_crawler.py             # Extrai dados de uma pagina de anuncio
│   ├── links_crawler.py           # Coleta links de anuncios e gera CSV bruto
│   ├── helpers.py                 # Funcoes de limpeza, coleta de links e matching
│   ├── fipe_api.py                # Funcoes para consultar a API da FIPE
│   └── populate_sample_db.py      # Popula banco local com amostra pequena
├── src/meu_proximo_carro/         # Modulos atuais de crawler, FIPE, matching e banco
├── tests/                         # Testes unitarios e smoke tests opcionais
└── database-*.csv                 # Saidas pontuais de coleta
```

## Pipeline de dados

1. `scripts/links_crawler.py` acessa uma pagina de busca da Mobiauto, coleta links de anuncios e chama `car_crawler`.
2. `scripts/car_crawler.py` extrai os campos principais da pagina do veiculo e retorna um dicionario pronto para virar `DataFrame`.
3. `scripts/helpers.py` prepara a base com limpeza de duplicados, conversao de preco para numero, criacao de ano de fabricacao/modelo e tratamento de valores ausentes.
4. `scripts/fipe_api.py` consulta marcas, modelos, anos e historico mensal de precos na FIPE.
5. Os notebooks em `notebooks/` fazem analise exploratoria, preparacao para dashboard e estudos de serie temporal.
6. O dashboard em `dashboard/app.py` apresenta seletores de marca/modelo/ano e graficos de comparacao.

## Principais bases

- `data/raw/database-*.csv`: dados brutos coletados de anuncios.
- `data/processed/database_cleaned.csv`: base limpa para analise.
- `data/processed/database-dashboard.csv`: base preparada para visualizacao.
- `data/lookup/lista_completa_fiat.csv`: combinacoes de marca, modelo e ano da FIPE para Fiat.
- `data/lookup/lista_completa.csv`: tabela auxiliar mais ampla de modelos FIPE.
- `data/lookup/nomes_fipe.csv`: nomes de modelos usados no matching textual.
- `data/processed/meu_proximo_carro.db`: banco SQLite local usado para testar o dashboard.

## Requisitos

As principais dependencias estao em `requirements.txt`. Para instalar manualmente:

```bash
pip install pandas beautifulsoup4 requests unidecode
pip install dash dash-bootstrap-components plotly
pip install rapidfuzz pyarrow openpyxl
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

### Popular banco local de exemplo

```bash
python3 scripts/populate_sample_db.py --limit 6 --fipe-months 1
```

### Rodar o dashboard

```bash
python3 dashboard/app.py
```

## Observacoes de desenvolvimento

- A implementacao atual vive em `src/meu_proximo_carro/`; `scripts/` contem entrypoints e wrappers de compatibilidade.
- O scraping da Mobiauto prioriza o payload `__NEXT_DATA__`, mas ainda depende de uma pagina externa e pode quebrar.
- As consultas a FIPE usam headers de navegador e a tabela de referencia mais recente retornada pela API.
- Ha um ambiente virtual versionado em `myenv/`; em novos clones, prefira criar um ambiente local novo.

## Proximos passos sugeridos

- Evoluir de SQLite local para Supabase/Postgres.
- Padronizar notebooks antigos para usar `src/meu_proximo_carro/`.
- Adicionar testes para conversao de valores, limpeza de dados e consultas FIPE.
- Parametrizar URLs, cidade e marca/modelo por argumentos de linha de comando ou arquivo de configuracao.
