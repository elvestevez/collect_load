import time
from modules.load import load_dimensions as dim
from modules.load import load_income_aeat as in_aeat
from modules.load import load_income_ine as in_ine
from modules.load import load_population_ine as pop_ine
from modules.load import load_government as gov


# load dimensions
def load_dimensions():
    print('\nLoad dimensions...')
    start = time.time()
    
    dim.load_dimensions()
    print(dim.check_integrity_dimensions())
    
    end = time.time()
    print(f'time: {round(end-start, 2)} seg')

# load population INE
def load_population_INE(ini=2003, end=2021):
    print('\nLoad population INE...')
    start = time.time()
    
    for year in range(ini, end+1):
        pop_ine.load_population(str(year))
        print(pop_ine.check_integrity_population(str(year)))
    
    end = time.time()
    print(f'time: {round(end-start, 2)} seg')

# load income INE
def load_income_INE(ini=2016, end=2020):
    print('\nLoad income INE...')
    start = time.time()
    
    for year in range(ini, end+1):
        in_ine.load_incomes(str(year))
        print(in_ine.check_integrity_incomes(str(year)))
    
    end = time.time()
    print(f'time: {round(end-start, 2)} seg')

# load income AEAT
def load_income_AEAT(ini=2018, end=2020):
    print('\nLoad income AEAT...')
    start = time.time()
    
    for year in range(ini, end+1):
        in_aeat.load_incomes(str(year))
        print(in_aeat.check_integrity_incomes(str(year)))

    end = time.time()
    print(f'time: {round(end-start, 2)} seg')

# load government
def load_government():
    print('\nLoad government...')
    start = time.time()
    
    gov.get_government_files()
    gov.load_government()
    gov.get_old_government_files()
    gov.load_old_government()
    print(gov.check_integrity_government())

    gov.load_government_region()
    print(gov.check_integrity_government_region())
    
    end = time.time()
    print(f'time: {round(end-start, 2)} seg')


def main():

    # Dimensions
    load_dimensions()
    
    # Income AEAT
    load_income_AEAT(ini=2018, end=2020)

    # Income INE
    load_income_INE(ini=2016, end=2020)
    
    # Population INE
    load_population_INE(ini=2016, end=2021)
    
    # Government
    load_government()
    

if __name__ == '__main__':
    main()
