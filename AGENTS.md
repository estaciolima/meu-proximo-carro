# AGENTS.md - Meu Proximo Carro

Este arquivo orienta agentes e engenheiros que forem evoluir o projeto. O objetivo e manter as decisoes de produto e engenharia alinhadas enquanto o repositorio sai de um experimento local de dados para um dashboard publico.

## Visao do Produto

O Meu Proximo Carro deve ajudar pessoas comuns a analisar precos de veiculos seminovos para fazer a melhor compra possivel.

O produto nao e um marketplace e nao deve tentar substituir a decisao do comprador. O papel do dashboard e organizar evidencias: preco FIPE, precos reais anunciados, quilometragem, ano/modelo, versao e features relevantes do veiculo.

O primeiro produto publico sera um MVP analitico em que o usuario seleciona um veiculo e entende rapidamente se os anuncios encontrados parecem caros, baratos ou coerentes em relacao a FIPE e ao mercado observado.

## Contexto de Dominio

A Tabela FIPE e a principal referencia de preco de automoveis no Brasil e costuma ser usada por compradores e vendedores como base de negociacao. Ela e muito util para historico e preco medio, mas nao descreve as features dos veiculos anunciados.

A Mobiauto e uma fonte interessante porque, quando o projeto foi criado, era acessivel a crawlers e continha anuncios reais com dados praticos para o consumidor, como opcionais, quilometragem, cambio, combustivel, cidade, cor e outros atributos.

Uma parte central do projeto e ligar as informacoes da FIPE aos modelos obtidos na Mobiauto. Esse matching deve comecar com normalizacao de nomes e fuzzy matching leve; embeddings/modelos pesados so devem entrar se houver um ganho medido que justifique o custo.

## Arquitetura Alvo

- Dashboard publico: Dash/Plotly.
- Banco de dados: Supabase/Postgres.
- Deploy inicial: Render, Fly, Railway ou outro servico equivalente para apps Python.
- Atualizacao de dados: job manual primeiro, com snapshots revisados antes de alimentar o dashboard.
- Crawler: processo separado do dashboard. O app publico deve ler dados tratados do banco, nao executar scraping durante a navegacao do usuario.

Fluxo esperado:

1. Executar crawler manual para Mobiauto e FIPE.
2. Salvar dados brutos em `data/raw/`, preservando snapshots.
3. Limpar, normalizar e enriquecer dados em uma etapa de processamento.
4. Fazer matching entre anuncios Mobiauto e registros FIPE.
5. Carregar tabelas tratadas no Supabase/Postgres.
6. Servir o dashboard Dash/Plotly consultando apenas dados tratados.

## MVP do Dashboard

O MVP deve focar em comparar FIPE x anuncios reais. Ele deve permitir:

- selecionar marca, modelo e ano/modelo;
- ver preco FIPE atual e historico recente;
- ver preco medio, minimo, maximo e distribuicao dos anuncios encontrados;
- comparar diferenca percentual entre anuncios e FIPE;
- explorar quilometragem dos anuncios;
- visualizar features relevantes para decisao de compra, como cambio, combustivel, opcionais e cidade;
- identificar casos em que ha poucos dados ou matching incerto.

A interface deve ser simples para consumidores nao tecnicos. Evite transformar o MVP em uma ferramenta de analise exploratoria complexa demais antes de entregar a comparacao principal.

## Regras Para Agentes

- Preserve dados brutos. Nunca sobrescreva snapshots em `data/raw/`; gere novos arquivos ou use uma estrategia explicita de versionamento.
- Nao inclua segredos, chaves de API, senhas ou strings de conexao reais no repositorio.
- Padronize caminhos em torno de `data/`, com subpastas como `raw`, `processed` e `lookup`.
- Evite efeitos colaterais no import. Modulos Python nao devem executar crawlers, gerar artefatos de matching, mudar diretorio de trabalho ou fazer chamadas externas apenas por serem importados.
- Nao faça crawling agressivo. Use pausas, retries com backoff, limites de paginas e logs claros.
- Trate scraping como fragil. Mudancas no HTML/CSS da Mobiauto devem ser documentadas junto com a correcao.
- Separe coleta, transformacao, carga e visualizacao. O dashboard nao deve depender de arquivos locais soltos nem executar pipeline pesado em callback.
- Prefira funcoes pequenas, testaveis e com entradas/saidas explicitas.
- Ao alterar matching FIPE x Mobiauto, registre o criterio usado e preserve dados suficientes para auditoria.
- Antes de remover ou reprocessar dados, verifique se eles sao insumo para notebooks, dashboards ou comparacoes historicas.

## Estado Atual do Repositorio

O repositorio esta em transicao de experimento local para aplicacao. Antes de implementar funcionalidades maiores, considere estes pontos:

- A implementacao atual deve ficar em `src/meu_proximo_carro/`.
- `scripts/` deve conter apenas entrypoints pequenos ou wrappers de compatibilidade.
- O dashboard atual e `dashboard/app.py`; arquivos antigos de Streamlit/Dash experimental foram removidos.
- O scraping da Mobiauto prioriza o payload `__NEXT_DATA__`, mas continua dependente de um site externo.
- `requirements.txt` existe; mantenha dependencias pesadas fora do projeto salvo necessidade medida.
- Ha notebooks e datasets historicos; preserve mudancas existentes e evite reverter trabalho nao relacionado.

## Proximos Passos Tecnicos

1. Evoluir o SQLite local para Supabase/Postgres.
2. Definir schema final para marcas, modelos FIPE, anuncios, snapshots de coleta e resultados de matching.
3. Criar rotina de carga de snapshot tratado para Supabase/Postgres.
4. Preparar o dashboard Dash/Plotly para deploy publico.
5. Ampliar testes para limpeza de dados, conversao de valores, parsing FIPE e matching.
6. Documentar processo manual de atualizacao de dados.

## Referencias

- Supabase Python client: https://supabase.com/docs/reference/python/installing
- Supabase/Postgres connection options: https://supabase.com/docs/guides/database/connecting-to-postgres/serverless-drivers
- Plotly/Dash deployment troubleshooting: https://dash.plotly.com/dash-deployment-server/troubleshooting
