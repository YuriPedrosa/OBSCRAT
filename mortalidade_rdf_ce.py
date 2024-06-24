from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, XSD, RDFS
from bs4 import BeautifulSoup
import requests
import pandas as pd
import calendar
import unicodedata
import re

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
    2020: "obtce20.dbf",
    2021: "obtce21.dbf",
    2022: "obtce22.dbf",
}

headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
}


base_url = "http://tabnet.datasus.gov.br/cgi/tabcgi.exe?sim/cnv/obt10ce.def"
post_data = "Linha=Categoria_CID-10&Coluna=M%EAs_do_%D3bito&Incremento=%D3bitos_p%2FOcorr%EAnc&Arquivos={file}&pesqmes1=Digite+o+texto+e+ache+f%E1cil&SMunic%EDpio={city}&pesqmes2=Digite+o+texto+e+ache+f%E1cil&SRegi%E3o_de_Sa%FAde_%28CIR%29=TODAS_AS_CATEGORIAS__&SMacrorregi%E3o_de_Sa%FAde=TODAS_AS_CATEGORIAS__&pesqmes4=Digite+o+texto+e+ache+f%E1cil&SDivis%E3o_administ_estadual=TODAS_AS_CATEGORIAS__&pesqmes5=Digite+o+texto+e+ache+f%E1cil&SMicrorregi%E3o_IBGE=TODAS_AS_CATEGORIAS__&SRegi%E3o_Metropolitana_-_RIDE=TODAS_AS_CATEGORIAS__&pesqmes7=Digite+o+texto+e+ache+f%E1cil&SCap%EDtulo_CID-10=TODAS_AS_CATEGORIAS__&pesqmes8=Digite+o+texto+e+ache+f%E1cil&SGrupo_CID-10=TODAS_AS_CATEGORIAS__&pesqmes9=Digite+o+texto+e+ache+f%E1cil&SCategoria_CID-10=TODAS_AS_CATEGORIAS__&pesqmes10=Digite+o+texto+e+ache+f%E1cil&SCausa_-_CID-BR-10=TODAS_AS_CATEGORIAS__&SCausa_mal_definidas=TODAS_AS_CATEGORIAS__&pesqmes12=Digite+o+texto+e+ache+f%E1cil&SFaixa_Et%E1ria=TODAS_AS_CATEGORIAS__&pesqmes13=Digite+o+texto+e+ache+f%E1cil&SFaixa_Et%E1ria_OPS=TODAS_AS_CATEGORIAS__&pesqmes14=Digite+o+texto+e+ache+f%E1cil&SFaixa_Et%E1ria_det=TODAS_AS_CATEGORIAS__&SFx.Et%E1ria_Menor_1A=TODAS_AS_CATEGORIAS__&SSexo=TODAS_AS_CATEGORIAS__&SCor%2Fra%E7a=TODAS_AS_CATEGORIAS__&SEscolaridade=TODAS_AS_CATEGORIAS__&SEstado_civil=TODAS_AS_CATEGORIAS__&SLocal_ocorr%EAncia=TODAS_AS_CATEGORIAS__&zeradas=exibirlz&formato=prn&mostre=Mostra"


def get_df_mortalidade(year):
    df_mortalidade = pd.DataFrame()

    for option_value, option_name in smunicipio_options.items():
        response = requests.post(base_url, headers=headers,
                                 data=post_data.format(file = anos_options[year], city = option_value))
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        pre_tag = soup.find('pre')
        pre_text = pre_tag.get_text()
        linhas = pre_text.split('\n')

        data = []
        for linha in linhas:
            if linha.strip():
                valores = linha.replace('"', '').split(';')
                data.append(valores)

        option_df = pd.DataFrame(data[1:], columns=data[0])
        option_df = option_df.apply(
            lambda x: x.str.replace('\r', '', regex=True))
        option_df = option_df[~option_df.apply(
            lambda row: row.astype(str).str.contains('&').any(), axis=1)]
        option_df = option_df[~option_df.apply(
            lambda row: row.astype(str).str.contains('Total').any(), axis=1)]
        option_df = option_df.loc[:, ~option_df.columns.str.contains('Total')]
        option_df['Município'] = option_name
        df_mortalidade = pd.concat(
            [df_mortalidade, option_df], ignore_index=True)
        print(option_name)

    return df_mortalidade


meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
         'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']


def normaliza_str(str):
    texto_norm = unicodedata.normalize('NFD', str)
    texto_sem_acentos = texto_norm.encode('ascii', 'ignore').decode('utf-8')
    texto_limpo = re.sub(r'[^A-Za-z0-9 ]', '', texto_sem_acentos)
    return texto_limpo.replace(' ', '_').replace('-', '_').lower()


def converter_data(data_str):
    mes, ano = map(int, data_str.split('-'))
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    return f"{ano}-{mes:02d}-{ultimo_dia:02d}"


def create_graph(year):
    g = Graph()
    count = 0

    ICD10MO = Namespace("https://www.ufc.br/ontologies/ICD10CM-MO/")
    ICD10 = Namespace("http://purl.bioontology.org/ontology/ICD10CM/")
    GEO = Namespace("http://www.geonames.org/ontology#")

    g.bind("icd10MO", ICD10MO)
    g.bind("icd10", ICD10)
    g.bind("geo", GEO)

    df_mortalidade = get_df_mortalidade(year)

    for index, row in df_mortalidade.iterrows():
        [cid, name] = row['Categoria CID-10'].split(' ', 1)
        disease = ICD10[cid]

        city = row['Município'].lower()
        city_uri = GEO[normaliza_str(city)]

        for i, mes in enumerate(meses):
            date = converter_data(f"{i+1}-{year}")
            deaths = row[mes]

            if (pd.isna(deaths) or deaths == "-"):
                deaths = 0

            g.add((city_uri, RDF.type, GEO.City))

            event = URIRef(ICD10MO + f"{normaliza_str(city)}/{cid}/{date}")

            g.add((event, RDF.type, ICD10MO.MortalityEvent))
            g.add((event, ICD10MO.occurredIn, city_uri))
            g.add((event, ICD10MO.hasCause, disease))
            g.add((event, ICD10MO.numberOfDeaths,
                   Literal(deaths, datatype=XSD.integer)))
            g.add((event, ICD10MO.date, Literal(date, datatype=XSD.date)))
            g.add((event, RDFS.label, Literal(
                f"{city} - {name.strip()} - {date}")))
            g.add((event, RDFS.comment, Literal(
                f"{name.strip()} in {city} on {date}")))
            print(event)
            count += 1

    rdf_output = g.serialize(format="turtle")

    with open(
        f"graph/mortalidade-{year}.ttl", "w", encoding="utf-8"
    ) as rdf_file:  # Use "w" to write as a string
        rdf_file.write(rdf_output)
    print(f"Arquivo gerado com sucesso: mortalidade-{year}.ttl")
    print(f"Total de eventos em {year}: {count}")

for year in anos_options.keys():
    create_graph(year)