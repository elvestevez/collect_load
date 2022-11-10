import os
import pandas as pd
from modules.db import to_db as db
from modules.db import db_integrity as db_int


INCOME_PATH = './data/income_ine/'
INCOME_TABLE = 'INCOME_INE'


# save income in db
def save_incomes(df, name_table):
    db.to_sqlite(df, name_table)

# clean income df
def data_clean_income(df_in, year):
    # filter only city
    df_income = df_in.loc[(df_in['Distritos'].isnull()) &
                          (df_in['Secciones'].isnull())].copy()

    # filter period
    df_income = df_income.loc[(df_income['Periodo'] == int(year))]
    
    # divide city in cod and description
    df_income[['Id_city', 'City']] = df_income['Municipios'].str.split(' ', n=1, expand=True)

    # drop columns
    df_income.drop(['Municipios', 'Distritos', 'Secciones'], axis=1, inplace=True)

    # encoding
    df_income['Id_indicator'] = df_income['Indicadores de renta media y mediana']. \
                                                                                  str.replace('Renta neta media por persona', 'RNMP'). \
                                                                                  str.replace('Renta neta media por hogar', 'RNMH'). \
                                                                                  str.replace('Media de la renta por unidad de consumo', 'RMUC'). \
                                                                                  str.replace('Mediana de la renta por unidad de consumo', 'RDUC'). \
                                                                                  str.replace('Renta bruta media por persona', 'RBMP'). \
                                                                                  str.replace('Renta bruta media por hogar', 'RBMH').str.strip()

    # convert total to number 
    df_income['Total'] = pd.to_numeric(df_income['Total'], errors='coerce')

    # drop rows with null value (Total=NA)
    df_income.dropna(inplace=True)
    
    # convert Total to int
    df_income['Total'] = df_income['Total'].astype('int')

    # rename and reorder cols
    df_income.rename(columns={'Periodo': 'Year'}, inplace=True)
    cols = ['Id_city', 'Id_indicator', 'Year', 'Total']
    df_income = df_income[cols]

    return df_income

# read income file
def read_incomes(file, year):
    df_in = pd.read_csv(file, sep=';', converters={'Total': lambda x: x.replace('.', '')})
    df_incomes = data_clean_income(df_in, year)

    return df_incomes

# read and save in db incomes
def load_incomes(year):
    # income files
    files = os.listdir(INCOME_PATH)
    
    # df final
    df_incomes = pd.DataFrame([])
    for f in files:
        # read file income
        df_income = read_incomes(INCOME_PATH + f, year)
        # join incomes
        df_incomes = pd.concat([df_incomes, df_income])
    
    # save incomes in db
    print(len(df_incomes))
    save_incomes(df_incomes, INCOME_TABLE)

# check integrity incomes
def check_integrity_incomes(year):
    msg = f'Integrity income {INCOME_TABLE} year {year}: '
    city_ok = db_int.integrity_city(INCOME_TABLE, year)
    indi_ok = db_int.integrity_indicator_incomes(INCOME_TABLE, year)
    if city_ok and indi_ok:
        msg = msg + '\n   Ok'
    if not city_ok:
        msg = msg + '\n   Error cities'
    if not indi_ok:
        msg = msg + '\n   Error indicators income'
    return msg
