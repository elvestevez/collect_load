import os
import pandas as pd
from modules.db import to_db as db
from modules.db import db_integrity as db_int


CITY_PATH = './data/dimensions/cities.csv'
CITY_TABLE = 'CITY'
PROVINCE_PATH = './data/dimensions/provinces.csv'
PROVINCE_TABLE = 'PROVINCE'
REGION_PATH = './data/dimensions/regions.csv'
REGION_TABLE = 'REGION'
INDICATOR_INCOME_PATH = './data/dimensions/indicator_income.csv'
INDICATOR_INCOME_TABLE = 'INDICATOR_IN'


# read dimension file
def read_dimension(file):
    df_in = pd.read_csv(file, sep=';', converters={'Total': lambda x: x.replace('.', '')})
    
    return df_in

# save dimension in db
def save_dimension(df, name_table):
    db.to_sqlite(df, name_table)

# clean city df
def data_clean_city(df_in):
    # copy df
    df_out = df_in.copy()
    
    # join and fill columns
    df_out['Id_city'] = df_out['CPRO'].astype(str).str.zfill(2) + df_out['CMUN'].astype(str).str.zfill(3)
    df_out['Id_province'] = df_out['CPRO'].astype(str).str.zfill(2)

    # rename and reorder cols
    df_out.rename(columns={'NOMBRE': 'City'}, inplace=True)
    df_out.rename(columns={'NOMBRE_GOV': 'City_gov'}, inplace=True)
    cols = ['Id_province', 'Id_city', 'City', 'City_gov']
    df_out = df_out[cols]
    
    return df_out

# read and save in db cities
def load_cities():
    # read file cities
    df_c = read_dimension(CITY_PATH)
    df_cities = data_clean_city(df_c)
    
    # save cities in db
    save_dimension(df_cities, CITY_TABLE)

# clean province df
def data_clean_province(df_in):
    # copy df
    df_out = df_in.copy()
    
    # fill columns
    df_out['Id_province'] = df_out['Id_province'].astype(str).str.zfill(2)
    df_out['Id_region'] = df_out['Id_region'].astype(str).str.zfill(2)
    
    return df_out

# read and save in db provinces
def load_provinces():
    # read file provinces
    df_p = read_dimension(PROVINCE_PATH)
    df_provinces = data_clean_province(df_p)
    
    # save provinces in db
    save_dimension(df_provinces, PROVINCE_TABLE)

# clean region df
def data_clean_region(df_in):
    # copy df
    df_out = df_in.copy()
    
    # fill columns
    df_out['Id_region'] = df_out['Id_region'].astype(str).str.zfill(2)
    
    return df_out

# read and save in db regions
def load_regions():
    # read file regions
    df_r = read_dimension(REGION_PATH)
    df_regions = data_clean_region(df_r)
    
    # save regions in db
    save_dimension(df_regions, REGION_TABLE)

# read and save in db indicators incomes
def load_indicators_incomes():
    # read file indicators incomes
    df_ii = read_dimension(INDICATOR_INCOME_PATH)
    
    # save indicators incomes in db
    save_dimension(df_ii, INDICATOR_INCOME_TABLE)

# load dimensions
def load_dimensions():
    # regions
    load_regions()
    # provinces
    load_provinces()
    # cities
    load_cities()
    # indicators incomes
    load_indicators_incomes()

# check integrity dimensions
def check_integrity_dimensions():
    msg = 'Integrity dimensions: '
    prov_ok = db_int.integrity_province()
    regi_ok = db_int.integrity_region(PROVINCE_TABLE)
    if prov_ok and regi_ok:
        msg = msg + '\n   Ok'
    if not prov_ok:
        msg = msg + '\n   Error provinces'
    if not regi_ok:
        msg = msg + '\n   Error regions'
    return msg
