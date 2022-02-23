import city_data
import fbi_data

def get_dataset(rows=None):
    try: # sometimes website asks to login other times it doesn't
        city_data.login()
        city_data.get_city_data(rows) # get all data
        pass
    except:
        city_data.get_city_data(rows)
        pass
    
    fbi_data.get_crime_data()
    # clean up some duplicate data
    
get_dataset()

    