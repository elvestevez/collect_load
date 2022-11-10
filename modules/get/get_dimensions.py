import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import inspect
import pandas as pd


DB_SQLITE = './db/db_collect.db'


# connect DB
def connect_DB():
    # DB sqlite
    connectionDB = f'sqlite:///{DB_SQLITE}'
    engineDB = create_engine(connectionDB)
    return engineDB

# get data DB
def get_data(engineDB):
    # query 
    query = f'''
    SELECT c.Id_city , c.City , c.City_gov , c.Id_province , p.Province , p.Province_gov , p.Id_region, r.Region  
    FROM CITY c
	    INNER JOIN PROVINCE p ON p.Id_province = c.Id_province 
	    INNER JOIN REGION r ON r.Id_region = p.Id_region 
    '''
    
    #print(query)

    dict_data = pd.read_sql_query(query, engineDB).to_dict(orient='records')
    
    ###print(json_data)
    
    return dict_data

# get cities
def get_city_province():
    # connect
    engineDB = connect_DB()

    # select data
    result_data = get_data(engineDB)
    
    return result_data
