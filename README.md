# OBSCRAT - Framework Semântico para o Observatório de Dados Abertos dos Sertões de Crateús

Este repositório contém scripts e recursos para a integração semântica de dados de saúde relacionados à COVID-19 e mortalidade por outras doenças respiratórias no estado do Ceará, Brasil.

## Descrição

Os scripts Python neste repositório são usados para converter dados de saúde pública para o formato RDF (Resource Description Framework), que é um padrão da Web Semântica para integrar informações heterogêneas. Além disso, o arquivo `ontology.zip` contém uma ontologia expandida que é usada para estruturar e relacionar os dados semânticos.

## Arquivos no Repositório

- `covid_rdf_ce.py`: Script para converter dados de COVID-19 para RDF.
- `mortalidade_rdf_ce.py`: Script para converter dados de mortalidade para RDF.
- `ontology.zip`: Arquivo compactado contendo a ontologia utilizada para a integração semântica dos dados.

# Pré-requisitos para Execução dos Scripts de Análise de Mortalidade

Para executar os scripts de análise de mortalidade relacionados aos dados de COVID-19 e mortalidade geral no estado do Ceará, você precisará atender aos seguintes pré-requisitos:

## Ambiente de Desenvolvimento

- **Python**: Uma versão recente do Python (3.6 ou superior) deve estar instalada em seu sistema. Você pode baixar a última versão do Python do [site oficial](https://www.python.org/downloads/).

## Bibliotecas Python

Os scripts dependem de várias bibliotecas Python externas. Você pode instalá-las usando o gerenciador de pacotes `pip`. Abaixo estão as bibliotecas necessárias:

- **rdflib**: Uma biblioteca para trabalhar com RDF (Resource Description Framework), um padrão para troca de dados na Web.
  ```
  pip install rdflib
  ```
- **pandas**: Uma biblioteca que fornece estruturas de dados e ferramentas de análise de dados.
  ```
  pip install pandas
  ```
- **requests**: Uma biblioteca para fazer solicitações HTTP de maneira simples.
  ```
  pip install requests
  ```
- **BeautifulSoup**: Uma biblioteca para extrair dados de arquivos HTML e XML.
  ```
  pip install beautifulsoup4
  ```
## Conectividade de Rede

- Certifique-se de ter uma conexão de internet estável, pois os scripts fazem solicitações HTTP para baixar dados e extrair informações de páginas da web.

## Permissões de Acesso

- Você precisará de permissões de leitura e escrita no diretório onde os scripts estão localizados para que eles possam criar e salvar arquivos `.ttl`.

Após garantir que todos os pré-requisitos foram atendidos, você pode executar os scripts em seu ambiente de desenvolvimento Python. Se encontrar qualquer problema durante a instalação ou execução, verifique se todas as dependências foram corretamente instaladas e se sua versão do Python é compatível com as bibliotecas.