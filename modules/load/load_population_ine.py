import os
import pandas as pd
from modules.db import to_db as db
from modules.db import db_integrity as db_int


POPULATION_PATH = './data/population_ine/'
POPULATION_TABLE = 'POPULATION_INE'


# save population in db
def save_population(df, name_table):
    db.to_sqlite(df, name_table)

# clean population df
def data_clean_population(df_in, year):
    # filter only city, period
    df_pop = df_in.loc[(df_in['Municipios'].notnull()) &
                       (df_in['Periodo'] == f'1 de enero de {year}')].copy()
    
    # filter sex, age
    df_pop = df_pop.loc[(df_pop['Sexo'] != 'Total') &
                        (df_pop['Edad (año a año)'] != 'Todas las edades')]

    # get year
    df_pop['Year'] = df_pop['Periodo'].str.split(' ').str[-1]
    
    # set date
    df_pop['Date'] = '01/01/' + df_pop['Year'] 
    
    # convert Year to int
    df_pop['Year'] = df_pop['Year'].astype('int')
    
    # divide city in cod and description
    df_pop[['Id_city', 'City']] = df_pop['Municipios'].str.split(' ', n=1, expand=True)
    
    # get only years old
    df_pop['Id_age'] = df_pop['Edad (año a año)'].str.split(' ', n=1).str[0]
    
    # encoding
    df_pop['Id_gender'] = df_pop['Sexo'].str.replace('Hombres', 'M').str.replace('Mujeres', 'F').str.strip()

    # convert total to number 
    df_pop['Total'] = pd.to_numeric(df_pop['Total'], errors='coerce')

    # drop columns
    df_pop.drop(['Provincias', 'Municipios'], axis=1, inplace=True)

    # drop rows with null value
    df_pop.dropna(inplace=True)

    # rename and reorder cols
    df_pop['Total'] = df_pop['Total'].astype('int')
    cols = ['Id_city', 'Id_gender', 'Id_age', 'Date', 'Year', 'Total']
    df_pop = df_pop[cols]

    # pivot by gender
    df_pop_g = df_pop.pivot_table('Total', 
                                  ['Id_city', 'Id_age', 'Date', 'Year'], 
                                  'Id_gender').reset_index().rename(columns={'F': 'Female', 'M': 'Male'})
    
    # pivot by age
    df_pop_a = df_pop_g.pivot_table(['Female', 'Male'], ['Id_city', 'Date', 'Year'], 'Id_age').reset_index()

    # rename cols
    df_pop_a.columns = ["_".join(pair) for pair in df_pop_a.columns]

    df_pop_a.rename(columns={'Id_city_': 'Id_city', 'Year_': 'Year', 'Date_': 'Date'}, inplace=True)

    # total and total gender
    list_name_f = []
    list_name_m = []
    for c in df_pop.columns:
        if c.startswith('Female'):
            list_name_f.append(c)
        if c.startswith('Male'):
            list_name_m.append(c)

    # total gender
    df_pop_a['Total_F'] = df_pop_a.loc[:, list_name_f].sum(axis=1)
    df_pop_a['Total_M'] = df_pop_a.loc[:, list_name_m].sum(axis=1)
    # total
    df_pop_a['Total'] = df_pop_a['Total_F'] + df_pop_a['Total_M']
    
    return df_pop_a

# clean population (national) df
def data_clean_national_population(df_in, year):
    # filter sex, age, period
    df_pop = df_in.loc[(df_in['Sexo'] != 'Total') &
                       (df_in['Edad (año a año)'] != 'Todas las edades') &
                       (df_in['Municipios'] != 'Total Nacional') &
                       (df_in['Periodo'] == f'1 de enero de {year}')].copy()
    
    # get year
    df_pop['Year'] = df_pop['Periodo'].str.split(' ').str[-1]
    
    # set date
    df_pop['Date'] = '01/01/' + df_pop['Year'] 
    
    # convert Year to int
    df_pop['Year'] = df_pop['Year'].astype('int')
    
    # divide city in cod and description
    df_pop[['Id_city', 'City']] = df_pop['Municipios'].str.split(' ', n=1, expand=True)
    
    # get only years old
    df_pop['Id_age'] = df_pop['Edad (año a año)'].str.split(' ', n=1).str[0]

    # encoding
    df_pop['Id_gender'] = df_pop['Sexo'].str.replace('Hombres', 'M').str.replace('Mujeres', 'F').str.strip()
    
    # convert total to number 
    df_pop['Total'] = pd.to_numeric(df_pop['Total'], errors='coerce')

    # drop columns
    df_pop.drop(['Municipios'], axis=1, inplace=True)

    # drop rows with null value
    df_pop.dropna(inplace=True)

    # rename and reorder cols
    df_pop['Total'] = df_pop['Total'].astype('int')
    cols = ['Id_city', 'Id_gender', 'Id_age', 'Date', 'Year', 'Total']
    df_pop = df_pop[cols]

    # pivot by gender
    df_pop_g = df_pop.pivot_table('Total', 
                                  ['Id_city', 'Id_age', 'Date', 'Year'], 
                                  'Id_gender').reset_index().rename(columns={'F': 'Female', 'M': 'Male'})
    
    # pivot by age
    df_pop_a = df_pop_g.pivot_table(['Female', 'Male'], ['Id_city', 'Date', 'Year'], 'Id_age').reset_index()

    # rename cols
    df_pop_a.columns = ["_".join(pair) for pair in df_pop_a.columns]

    df_pop_a.rename(columns={'Id_city_': 'Id_city', 'Year_': 'Year', 'Date_': 'Date'}, inplace=True)

    # total and total gender
    list_name_f = []
    list_name_m = []
    for c in df_pop_a.columns:
        if c.startswith('Female'):
            list_name_f.append(c)
        if c.startswith('Male'):
            list_name_m.append(c)

    # total gender
    df_pop_a['Total_F'] = df_pop_a.loc[:, list_name_f].sum(axis=1)
    df_pop_a['Total_M'] = df_pop_a.loc[:, list_name_m].sum(axis=1)
    # total
    df_pop_a['Total'] = df_pop_a['Total_F'] + df_pop_a['Total_M']
    
    return df_pop_a

# read population file
def read_population(file, year):
    df_pop = pd.read_csv(file, sep=';', converters={'Total': lambda x: x.replace('.', '')})
    #df_population = data_clean_population(df_pop, year)
    df_population = data_clean_national_population(df_pop, year)

    return df_population

# read and save in db population
def load_population(year):
    # population files
    files = os.listdir(POPULATION_PATH)
    
    # df final
    df_population = pd.DataFrame([])
    for f in files:
        # read file population
        df_pop = read_population(POPULATION_PATH + f, year)
        # join population
        df_population = pd.concat([df_population, df_pop])
    
    # save population in db
    print(len(df_population))
    save_population(df_population, POPULATION_TABLE)

# check integrity incomes
def check_integrity_population(year):
    msg = f'Integrity population {POPULATION_TABLE} year {year}: '
    city_ok = db_int.integrity_city(POPULATION_TABLE, year)
    if city_ok:
        msg = msg + '\n   Ok'
    if not city_ok:
        msg = msg + '\n   Error cities'
    return msg
