import requests
import bs4
import pandas as pd
from modules.db import to_db as db
from modules.db import db_integrity as db_int


URL_2020 = 'https://www.agenciatributaria.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfmunicipios/2020/jrubikf7024f7e68a6d19091b823f761818f14de77d7950.html'
URL_2019 = 'https://www.agenciatributaria.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfmunicipios/2019/jrubikf74b3dca9af01b51cabd6d5603e0e16daecd1a97c.html'
URL_2018 = 'https://www.agenciatributaria.es/AEAT/Contenidos_Comunes/La_Agencia_Tributaria/Estadisticas/Publicaciones/sites/irpfmunicipios/2018/jrubik7fe28e5d4daeab97eaf47efe29f0716914ab405e.html'
INCOME_TABLE = 'INCOME_AEAT'


# save income in db
def save_incomes(df, name_table):
    db.to_sqlite(df, name_table)

# read income file
def read_incomes(year):
    if year == '2018':
        url = URL_2018
    if year == '2019':
        url = URL_2019
    if year == '2020':
        url = URL_2020
    
    # html
    response = requests.get(url)
    html = response.content
    parsed_html = bs4.BeautifulSoup(html, "html.parser") 

    list_cities = []
    # get tag cities
    cities = parsed_html.find_all("tr", {"class": "depth_3"})
    for i in cities:
        # city name
        city_name = i.find("div", {"class": "depth_div_4"}).string
        # get tag data of every city
        city_data = i.find_all("td")
        dict_city = {}
        #dict_city['City'] = city_name
        city_name_split = city_name.split('-')
        if len(city_name_split) == 1:
            dict_city['Id_city'] = city_name_split[0]
        else:
            dict_city['Id_city'] = city_name_split[-1].ljust(5, '0')
        dict_city['Year'] = year
        for j in range(len(city_data)):
            # owners
            if j == 0:
                dict_city['Owners'] = city_data[j].string.replace('.', '')
            # number of declarations
            if j == 1:
                dict_city['Declarations'] = city_data[j].string.replace('.', '')
            # population
            if j == 2:
                dict_city['Population'] = city_data[j].string.replace('.', '')
            # national position
            if j == 3:
                dict_city['National_position'] = city_data[j].string.replace('.', '')
            # region position
            if j == 4:
                dict_city['Region_position'] = city_data[j].string.replace('.', '')
            # average gross income
            if j == 5:
                dict_city['Avg_gross_income'] = city_data[j].string.replace('.', '')
            # average net income
            if j == 6:
                dict_city['Avg_net_income'] = city_data[j].string.replace('.', '')
        # append list of cities
        list_cities.append(dict_city)
    # convert df
    df_incomes = pd.DataFrame(list_cities)
    # convert to int
    df_incomes['Year'] = pd.to_numeric(df_incomes['Year'], errors='coerce')
    df_incomes['Owners'] = pd.to_numeric(df_incomes['Owners'], errors='coerce')
    df_incomes['Declarations'] = pd.to_numeric(df_incomes['Declarations'], errors='coerce')
    df_incomes['Population'] = pd.to_numeric(df_incomes['Population'], errors='coerce')
    df_incomes['National_position'] = pd.to_numeric(df_incomes['National_position'], errors='coerce')
    df_incomes['Region_position'] = pd.to_numeric(df_incomes['Region_position'], errors='coerce')
    df_incomes['Avg_gross_income'] = pd.to_numeric(df_incomes['Avg_gross_income'], errors='coerce')
    df_incomes['Avg_net_income'] = pd.to_numeric(df_incomes['Avg_net_income'], errors='coerce')

    # fill NA (indicators no info)
    df_incomes.fillna(0, inplace=True)
    df_incomes['Owners'] = df_incomes['Owners'].astype('int')
    df_incomes['Declarations'] = df_incomes['Declarations'].astype('int')
    df_incomes['Population'] = df_incomes['Population'].astype('int')
    df_incomes['National_position'] = df_incomes['National_position'].astype('int')
    df_incomes['Region_position'] = df_incomes['Region_position'].astype('int')
    df_incomes['Avg_gross_income'] = df_incomes['Avg_gross_income'].astype('int')
    df_incomes['Avg_net_income'] = df_incomes['Avg_net_income'].astype('int')
    
    return df_incomes

# read and save in db incomes
def load_incomes(year):
    # read incomes from url
    df_incomes = read_incomes(year)
    
    # save incomes in db
    print(len(df_incomes))
    save_incomes(df_incomes, INCOME_TABLE)

# check integrity incomes
def check_integrity_incomes(year):
    msg = f'Integrity income {INCOME_TABLE} year {year}: '
    city_ok = db_int.integrity_city(INCOME_TABLE, year)
    if city_ok:
        msg = msg + '\n   Ok'
    if not city_ok:
        msg = msg + '\n   Error cities'
    return msg
