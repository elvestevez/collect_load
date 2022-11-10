import time
from datetime import datetime
import os
import xlrd
from random import randrange
import pandas as pd
import requests
import bs4
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.select import Select
from modules.db import to_db as db
from modules.db import db_integrity as db_int
from modules.get import get_dimensions as dim


DOWNLOAD_PATH = '../../Downloads/'
GOVERNMENT_PATH = './data/government/'
GOVERNMENT_TABLE = 'GOVERNMENT'
DRIVER_CHROME = '../../drivers/chromedriver'


# save government in db
def save_government(df, name_table):
    db.to_sqlite(df, name_table)

# clean government df
def data_clean_government(df_in, province):
    # copy df
    df_gov = df_in.copy()
    
    # add end date and province
    df_gov['Id_province'] = province
    
    # rename and reorder cols
    df_gov.rename(columns={'Municipio': 'Name_city', 
                           'Lista': 'Government', 
                           'Fecha de Posesión': 'Ini_date'}, inplace=True)
    
    # replace
    df_gov['Government'] = df_gov['Government'].str.replace('P.S.O.E.',
                                                            'PSOE', regex=False) \
                                               .str.replace('P.S.O.E',
                                                            'PSOE', regex=False) \
                                               .str.replace('P.S.O.E-A',
                                                            'PSOE-A', regex=False) \
                                               .str.replace('P.S.O.E. - A',
                                                            'PSOE-A', regex=False) \
                                               .str.replace('P.S.O.E. ANDALUCIA',
                                                            'PSOE-A', regex=False) \
                                               .str.replace('P.S.O.E.- A',
                                                            'PSOE-A', regex=False) \
                                               .str.replace('P.S.O.E.-A',
                                                            'PSOE-A', regex=False) \
                                               .str.replace('P.S.O.E.-A.',
                                                            'PSOE-A', regex=False) \
                                               .str.replace('PSOE- A',
                                                            'PSOE-A', regex=False) \
                                               .str.replace('PSOE.-A',
                                                            'PSOE-A', regex=False) \
                                               .str.replace('P.P.',
                                                            'PP', regex=False) \
                                               .str.replace('P.P',
                                                            'PP', regex=False)

    # format ini date
    df_gov['Ini_date'] = df_gov['Ini_date'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y'))

    # president name
    df_gov['Name_president'] = df_gov['Nombre'].str.upper() + ' ' + df_gov['Apellido'].str.upper() + ' ' + df_gov['Apellido.1'].str.upper()

    # merge with cities dimensions
    df_cities = pd.DataFrame(dim.get_city_province())
    df_cities['City_gov'] = df_cities['City_gov'].str.upper()
    df_cities['City'] = df_cities['City'].str.upper()
    df_gov['Name_city'] = df_gov['Name_city'].str.upper()
    df_gov1 = df_gov.merge(df_cities, left_on=['Id_province', 'Name_city'], right_on=['Id_province', 'City_gov'])
    df_gov2 = df_gov.merge(df_cities, left_on=['Id_province', 'Name_city'], right_on=['Id_province', 'City'])
    df_government = pd.concat([df_gov1, df_gov2])
    df_government.drop_duplicates(inplace=True)
    
    # add end time and region
    df_government['End_date'] = None
    df_government['Id_region'] = None

    # reorder cols
    cols = ['Ini_date', 'End_date', 'Government', 'Name_president', 'Id_city', 'Id_region']
    df_government = df_government[cols]

    return df_government

# read government file
def read_government(path, file):
    workbook = xlrd.open_workbook(path + file, ignore_workbook_corruption=True)
    df_gov = pd.read_excel(workbook, header=5, usecols='A:F')
    province = file.split('_')[0]
    df_government = data_clean_government(df_gov, province)

    return df_government

# read and save in db government
def load_government():
    # gov files
    files = os.listdir(GOVERNMENT_PATH)
    
    # df final
    df_government = pd.DataFrame([])
    for f in files:
        if "ficha_alcaldes" in f:
            # read file government
            df_gov = read_government(GOVERNMENT_PATH, f)
            # join government
            df_government = pd.concat([df_government, df_gov])
    
    # save government in db
    print(len(df_government))
    save_government(df_government, GOVERNMENT_TABLE)

# clean government df
def data_clean_old_government(df_in):
    # copy df
    df_gov = df_in.copy()
    
    # rename and reorder cols
    df_gov.rename(columns={'GRUPO': 'Government',
                           'FECHA-POSESION': 'Ini_date'}, inplace=True)
    
    # president name
    df_gov['Name_president'] = df_gov['NOMBRE'].str.upper() + ' ' + df_gov['APELLIDO1'].str.upper() + ' ' + df_gov['APELLIDO2'].str.upper()

    # merge with cities dimensions
    df_cities = pd.DataFrame(dim.get_city_province())
    df_cities['City_gov'] = df_cities['City_gov'].str.upper()
    df_cities['City'] = df_cities['City'].str.upper()
    df_cities['Province_gov'] = df_cities['Province_gov'].str.upper()
    df_gov['MUNICIPIO'] = df_gov['MUNICIPIO'].str.upper()
    df_gov['PROVINCIA'] = df_gov['PROVINCIA'].str.upper()
    df_gov1 = df_gov.merge(df_cities, left_on=['PROVINCIA', 'MUNICIPIO'], right_on=['Province_gov', 'City_gov'])
    df_gov2 = df_gov.merge(df_cities, left_on=['PROVINCIA', 'MUNICIPIO'], right_on=['Province_gov', 'City'])
    df_government = pd.concat([df_gov1, df_gov2])
    df_government.drop_duplicates(inplace=True)

    # add end time and region
    df_government['End_date'] = None
    df_government['Id_region'] = None

    # reorder cols
    cols = ['Ini_date', 'End_date', 'Government', 'Name_president', 'Id_city', 'Id_region']
    df_government = df_government[cols]

    return df_government

# read government file
def read_old_government(path, file):
    df_gov = pd.read_excel(path + file, usecols='A:H')
    df_government = data_clean_old_government(df_gov)

    return df_government

def load_old_government():
    # gov files
    files = os.listdir(GOVERNMENT_PATH)
    
    # df final
    df_government = pd.DataFrame([])
    for f in files:
        if "Mandato" in f:
            # read file government
            df_gov = read_old_government(GOVERNMENT_PATH, f)
            # join government
            df_government = pd.concat([df_government, df_gov])
    
    # save government in db
    print(len(df_government))
    save_government(df_government, GOVERNMENT_TABLE)
    
# check integrity government
def check_integrity_government():
    msg = f'Integrity government {GOVERNMENT_TABLE}: '
    city_ok = db_int.integrity_city(GOVERNMENT_TABLE, year=None)
    if city_ok:
        msg = msg + '\n   Ok'
    if not city_ok:
        msg = msg + '\n   Error cities'
    return msg

# get file from download directory
def move_gov_file(province, pattern):
    files = os.listdir(DOWNLOAD_PATH)
    for f in files:
        if f.startswith(pattern):
            os.rename(DOWNLOAD_PATH + f, 
                      GOVERNMENT_PATH + province + '_' + f)

# web scraping
def get_government_files():
    service = Service(executable_path=DRIVER_CHROME)
    driver = webdriver.Chrome(service=service)

    url_gov ='https://concejales.redsara.es/consulta/'
    driver.get(url_gov)
    
    # get list province
    options = driver.find_element(By.ID, 'concejales_consulta_provincia').find_elements(By.TAG_NAME, 'option')
    provinces = Select(driver.find_element(By.ID, 'concejales_consulta_provincia'))
    for op in range(1, len(options)):
        # sleep proccess
        t = randrange(15)
        # get id province
        id_prov = options[op].get_attribute('value').zfill(2)
        
        # check province
        provinces.select_by_value(options[op].get_attribute('value'))
        download = driver.find_element(By.ID, 'descarga_alcaldes').find_element(By.ID, 'alcaldes_link')
        # download file
        download.click()
        # rename and move file
        time.sleep(8)
        move_gov_file(id_prov, 'ficha_alcaldes')
        
    # exit
    driver.quit()

# get file from download directory
def move_old_gov_file(pattern):
    files = os.listdir(DOWNLOAD_PATH)
    for f in files:
        if f.startswith(pattern):
            os.rename(DOWNLOAD_PATH + f, 
                      GOVERNMENT_PATH + f)

# web scraping
def get_old_government_files():
    service = Service(executable_path=DRIVER_CHROME)
    driver = webdriver.Chrome(service=service)

    url ='http://www.mptfp.es/portal/politica-territorial/local/sistema_de_informacion_local_-SIL-/alcaldes_y_concejales.html'

    driver.get(url)

    # download file
    download = driver.find_element(By.CLASS_NAME, 'com-listado__vertical').find_element(By.TAG_NAME, 'li').find_element(By.TAG_NAME, 'a')
    download.click()
    # rename and move file
    time.sleep(10)
    move_old_gov_file('Mandato')

    # exit
    driver.quit()

# check integrity government
def check_integrity_government_region():
    msg = f'Integrity government {GOVERNMENT_TABLE}: '
    city_ok = db_int.integrity_region(GOVERNMENT_TABLE)
    if city_ok:
        msg = msg + '\n   Ok'
    if not city_ok:
        msg = msg + '\n   Error cities'
    return msg

# read and save in db government regions
def load_government_region():

    url ='https://es.wikipedia.org/wiki/Anexo:Presidencias_de_las_comunidades_aut%C3%B3nomas_espa%C3%B1olas'

    # html
    response = requests.get(url)
    html = response.content
    parsed_html = bs4.BeautifulSoup(html, 'html.parser') 
    # element tbody
    list_tbody = parsed_html.find_all('tbody')
    mytbody = list_tbody[-1]
    myrows = mytbody.find_all('tr')
    # get presidents
    list_presidents = []
    for row in range(len(myrows)):
        content = myrows[row].find_all('td')
        ini_dates = 0
        end_dates = 0
        for td in range(len(content)):
            # name president
            if td == 0:
                name_president = ''
                if content[td].find('a') is not None:
                    name_president = content[td].find('a').string.upper()
            # ini date
            if td == 1:
                ini_dates = content[td].find_all('span')
            # end date
            if td == 2:
                end_dates=[]
                if content[td].find('span') is not None:
                    end_dates = content[td].find_all('span')
            # government
            if td == 4:
                list_gov = [g['title'].replace('Partido Socialista Obrero Español', 
                                               'PSOE') \
                                      .replace('Partido Popular',
                                               'PP') \
                                      .replace('Ciudadanos (España)',
                                               'Ciudadanos') for g in content[td].find_all('a')]
            # name region
            if td == 5:
                # list dates
                for dates in range(len(ini_dates)):
                    # new government
                    dict_presidents = {}
                    
                    dict_presidents['Ini_date'] = datetime.strptime(ini_dates[dates].string.strip()[1:], '%Y-%m-%d')
                    if dates <= len(end_dates)-1:
                        dict_presidents['End_date'] = datetime.strptime(end_dates[dates].string.strip()[1:], '%Y-%m-%d')
                    else:
                        dict_presidents['End_date'] = None
                    dict_presidents['Government'] =  ', '.join(list_gov)
                    dict_presidents['Name_president'] = name_president
                    dict_presidents['Id_city'] = None                
                    if content[td].find('a').string == 'Andalucía':
                        dict_presidents['Id_region'] = '01'
                    if content[td].find('a').string == 'Aragón':
                        dict_presidents['Id_region'] = '02'
                    if content[td].find('a').string == 'Principado de Asturias':
                        dict_presidents['Id_region'] = '03'
                    if content[td].find('a').string == 'Islas Baleares':
                        dict_presidents['Id_region'] = '04'                
                    if content[td].find('a').string == 'Canarias':
                        dict_presidents['Id_region'] = '05'
                    if content[td].find('a').string == 'Cantabria':
                        dict_presidents['Id_region'] = '06'
                    if content[td].find('a').string == 'Castilla y León':
                        dict_presidents['Id_region'] = '07'
                    if content[td].find('a').string == 'Castilla-La Mancha':
                        dict_presidents['Id_region'] = '08'
                    if content[td].find('a').string == 'Cataluña':
                        dict_presidents['Id_region'] = '09'
                    if content[td].find('a').string == 'Comunidad Valenciana':
                        dict_presidents['Id_region'] = '10'
                    if content[td].find('a').string == 'Extremadura':
                        dict_presidents['Id_region'] = '11'
                    if content[td].find('a').string == 'Galicia':
                        dict_presidents['Id_region'] = '12'
                    if content[td].find('a').string == 'Comunidad de Madrid':
                        dict_presidents['Id_region'] = '13'
                    if content[td].find('a').string == 'Región de Murcia':
                        dict_presidents['Id_region'] = '14'
                    if content[td].find('a').string == 'Comunidad Foral de Navarra':
                        dict_presidents['Id_region'] = '15'    
                    if content[td].find('a').string == 'País Vasco':
                        dict_presidents['Id_region'] = '16'
                    if content[td].find('a').string == 'La Rioja':
                        dict_presidents['Id_region'] = '17'
                    if content[td].find('a').string == 'Ceuta':
                        dict_presidents['Id_region'] = '18'
                    if content[td].find('a').string == 'Melilla':
                        dict_presidents['Id_region'] = '19'
                    # add government
                    if dict_presidents:
                        list_presidents.append(dict_presidents)

    df_gov_reg = pd.DataFrame(list_presidents)
    
    # save government in db
    print(len(df_gov_reg))
    save_government(df_gov_reg, GOVERNMENT_TABLE)
