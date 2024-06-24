from datetime import datetime
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, XSD, RDFS
import gzip
import io
import requests
import pandas as pd
import unicodedata
import re
import calendar

smunicipio_options = {
    "16": "ARARENDA",
    "44": "CATUNDA",
    "51": "CRATEUS",
    "71": "HIDROLANDIA",
    "79": "INDEPENDENCIA",
    "80": "IPAPORANGA",
    "83": "IPUEIRAS",
    "117": "MONSENHOR TABOSA",
    "124": "NOVA RUSSAS",
    "125": "NOVO ORIENTE",
    "161": "SANTA QUITERIA",
    "171": "TAMBORIL",
}

anos_options = {
    2020: "https://github.com/wcota/covid19br/raw/master/cases-brazil-cities-time_2020.csv.gz",
    2021: "https://github.com/wcota/covid19br/raw/master/cases-brazil-cities-time_2021.csv.gz",
    2022: "https://github.com/wcota/covid19br/raw/master/cases-brazil-cities-time_2022.csv.gz",
}


def read_csv(url):
    response = requests.get(url)

    df_covid = pd.DataFrame()

    if response.status_code == 200:
        with gzip.GzipFile(fileobj=io.BytesIO(response.content)) as f:
            df_covid = pd.read_csv(f, encoding="utf-8")
    else:
        print("Falha ao fazer o download do arquivo")

    return df_covid


def normaliza_str(str):
    texto_norm = unicodedata.normalize('NFD', str)
    texto_sem_acentos = texto_norm.encode('ascii', 'ignore').decode('utf-8')
    texto_limpo = re.sub(r'[^A-Za-z0-9 ]', '', texto_sem_acentos)
    return texto_limpo.replace(' ', '_').replace('-', '_').lower()


maped_cities = map(normaliza_str, smunicipio_options.values())
maped_cities = list(maped_cities)


def create_graph(year):
    g = Graph()

    ICD10MO = Namespace("https://www.ufc.br/ontologies/ICD10CM-MO/")
    ICD10 = Namespace("http://purl.bioontology.org/ontology/ICD10CM/")
    GEO = Namespace("http://www.geonames.org/ontology#")

    g.bind("icd10MO", ICD10MO)
    g.bind("icd10", ICD10)
    g.bind("geo", GEO)

    df_covid = read_csv(anos_options[year])
    previous_month_deaths={}

    # COVID-19
    disease = ICD10['U07.1']
    count = 0

    # Adicionar registros de COVID-19
    for index, row in df_covid.iterrows():
        if (row["city"].lower() == 'total'):
            continue

        city, state = row['city'].split('/')

        if state.lower() != 'ce':
            continue

        city_key = normaliza_str(city)
        if city_key not in maped_cities:
            continue

        date = row['date']

        data = datetime.strptime(date, "%Y-%m-%d")
        ultimo_dia_do_mes = calendar.monthrange(data.year, data.month)[1]

        if (data.day != ultimo_dia_do_mes):
            continue

        current_month_deaths = row['deaths']
        previous_deaths = previous_month_deaths.get(city_key, 0)
        monthly_deaths = current_month_deaths - previous_deaths
        previous_month_deaths[city_key] = current_month_deaths

        event_covid = URIRef(ICD10MO + f"{city_key}/U07.1/{date}")

        city_uri = GEO[city_key]
        g.add((city_uri, RDF.type, GEO.City))
        g.add((city_uri, RDFS.label, Literal(city)))

        g.add((event_covid, RDF.type, ICD10MO.MortalityEvent))
        g.add((event_covid, ICD10MO.occurredIn, city_uri))
        g.add((event_covid, ICD10MO.hasCause, disease))
        g.add((event_covid, ICD10MO.numberOfDeaths,
               Literal(monthly_deaths, datatype=XSD.integer)))
        g.add((event_covid, ICD10MO.date, Literal(date, datatype=XSD.date)))
        g.add((event_covid, RDFS.label, Literal(
            f"{city} - COVID-19 - {date}")))
        g.add((event_covid, RDFS.comment, Literal(
            f"COVID-19 in {city} on {date}")))
        print(event_covid)
        count += 1

    rdf_output = g.serialize(format="turtle")

    with open(
        f"graph/covid-{year}.ttl", "w", encoding="utf-8"
    ) as rdf_file:  # Use "w" to write as a string
        rdf_file.write(rdf_output)

    print(f"Arquivo gerado com sucesso: covid-{year}.ttl")
    print(f"Total de eventos em {year}: {count}")


for year in anos_options.keys():
    create_graph(year)

    