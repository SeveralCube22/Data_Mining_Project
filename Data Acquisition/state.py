from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup

import re
import pandas as pd

def get_ori_code(state, cities):
    driver = webdriver.Chrome(executable_path='C:/Users/manam/Desktop/chromedriver_win32/chromedriver.exe')
    base_url = "https://www.icpsr.umich.edu/files/NACJD/ORIs"
    
    driver.get(base_url + "/STATESoris.html")
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    state_ul = soup.find("ul")
    nums = []
    for li in state_ul.find_all("li"):
        ref = li.find("a")
        if state.upper() in ref.text:
            nums = re.findall('[0-9]+', ref.text)
            break    
    
    driver.get(base_url + "/{:02d}oris.html".format(int(nums[0])))
    soup = BeautifulSoup(driver.page_source, "html.parser")
    counties = soup.find_all("pre")

    city_ori = {}
    not_found = {}
    state_code = scrape_states[state]

    for city in cities:
        found = False
        cityName = city.replace("city", "")
        cityName = cityName.replace("town", "")
        cityName = cityName.replace("CDP", "")
      
        for county in counties:
            county = county.find(text=True)
            county = county.split("\n")
            
            for line in county:
                try:
                    res = re.search("{}[0-9]+".format(state_code), line)
                    index = res.start()
                    cmpLine = line[:index]
                except:
                    cmpLine = line
                if cityName.strip().upper() in line and ("POLICE DEPARTMENT" in line or "PD" in line or "POLICE DEPT" in line or "DEPARTMENT OF PUBLIC SAFETY" in line or cityName.strip().upper() == cmpLine.strip()):
                    try:
                        city_ori[city] = re.findall("{}[A-Za-z0-9][A-Za-z0-9]+".format(state_code), line)[-1] 
                        found = True
                    except:
                        print("Skipped ", city)
        if not found:
            not_found[city] = None
            
    return city_ori, not_found
    
def get_cities(year, state):
    df = pd.read_csv("./Data Acquisition/city_data.csv", sep=",",encoding="latin1")
    df.columns = df.columns.str.strip()
    
    filtered = df.loc[(df["YEAR"] == year) & (df["STATE"] == state)]
    cities = [city.strip() for city in filtered["CITY"]]
    return cities

def get_scrape_states():
    states = {}
    state_names = open("./Data Acquisition/states.csv", 'r')
    for (i, line) in enumerate(state_names):
        if i == 0:
            continue
        values = line.split(",")
        states[values[0].strip().replace('"', "")] = values[2].strip().replace('"', "")
    return states
        
scrape_states = get_scrape_states()