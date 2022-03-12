from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from sensitive import get_keys

import time
import os.path
import state
        
def get_state_data():
    state_data = {}
    soup = BeautifulSoup(driver.page_source, "html.parser")
    states = [i for i in soup.find("select", {"label": "State"})]
    
    for state in states:
        if(state["value"] == ""):
            continue
        state_data[state.text] = state["value"]
    return state_data
    
        
def login():
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='email-field']")))
    username = driver.find_element(By.XPATH, "//*[@id='email-field']")
    username.send_keys(sensitive["USERNAME"]) # username for solution explorer
    pswd = driver.find_element(By.XPATH, "//*[@id='passwordInput']")
    pswd.send_keys(sensitive["PASSWORD"]) # password for solution explorer
    wait_and_click("//*[@id='application']/div/div/div[3]/form/div[1]/button", click_btn)

def click_btn(xpath):
    btn = driver.find_element(By.XPATH, xpath)
    driver.execute_script("arguments[0].click();", btn)

def wait_for_element(xpath):
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath)))

def wait_and_click(xpath, func, **values):
    wait_for_element(xpath)
    value = values.get("value")
    
    func(xpath, value) if value else func(xpath)
    
def select(xpath, value):
    selector = Select(driver.find_element(By.XPATH, xpath))
    selector.select_by_value(value)
    
def select_place(stateValue=None):
    xpath = "//*[@id='cmbGeoType']"
    wait_and_click(xpath, select, value="SL160") # select PLACE
    xpath = "//*[@id='geoCombosContainer']/div/select"
    wait_for_element(xpath)

    if(stateValue == None):
        global states
        states = get_state_data() # have to do this because HTML attributes doesn't show initially
        
    else:
        wait_and_click(xpath, select, value=stateValue) # select state
        
        xpath = "//*[@id='listGeoItems']"
        values = stateValue.split(";")
        wait_and_click(xpath, select, value="{};{}; ".format(values[0], values[1])) # select all places(cities) in state
    
        click_btn("//*[@id='btnAddGeoItem']") # click add
        click_btn("//*[@id='btnGeoNext']") # click next
    
def select_properties():
    soup = BeautifulSoup(driver.page_source, "html.parser")
    properties = [i for i in soup.find("select", {"id": "tableCombo"})]
    select_xpath = "//*[@id='tableCombo']"
    wait_for_element(select_xpath)
    
    for prop in city_properties:
        for super in properties: # list of options
            if is_subset(super.text, prop):
                wait_and_click(select_xpath, select, value=super["value"])
                click_btn("//*[@id='btnAddTable']") # click add
                break
            
    click_btn("//*[@id='btnTableNext']") # click next
    wait_for_element("//*[@id='geoItemsPagerContainer']")

def store_table_link(year, state, url):
    fileName = "./Data Acquisition/table_links.csv"
    if(not os.path.exists(fileName)):
        file = open(fileName, "a")
        file.write("YEAR, STATE, URL\n")
        file.close()
        
    file = open(fileName, "a")
    file.write("{}, {}, {}\n".format(year, state, url))
    
def is_subset(super, sub):
    for word in sub:
        if word not in super:
            return False
    return True
    

def get_city_data(rows=None):
    wait_and_click("//*[@id='dashboard']/div[5]/div/div/div[5]/div[1]/button", click_btn)
    init = False
    file_init = False
    processed = 0
    for yearI in range(10):
        click_btn("//*[@id='dashboard']/div[5]/div/div/div[5]/div[2]/div[{}]/div[2]/a[1]".format(2 + yearI)) # iterating over begin     report buttons for years 2010-2019
   
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))   
        child = driver.window_handles[1]      
        driver.switch_to.window(child)
        curr_url= driver.current_url
        
        if not init: 
            select_place()
            init = True
        for (stateName, value) in states.items():
            if(stateName in state.scrape_states.keys()):
                try:
                    select_place(value) # pass state(other terrorties included) num 1-72 and state name
                    select_properties()
                    # store_table_link(2019 - yearI, stateName, driver.current_url)
                    wait_for_element("//*[@id='resultsHtmlContainer']")
                    all_cities = []
                    city_span_init = False
                    while True:
                        city_data = []
                        for i in range(2): # 2 pages for all attribute tables. Cannot do it dynamically, so doing this instead
                            x = parse_table()
                            city_data.append(x) # holds the different table data for set of cities (since tables are on separate pages)
                        
                            wait_and_click("//*[@id='results']/tbody/tr/td[2]/div[1]/span[1]", click_btn)
                            time.sleep(1)
                            wait_for_element("//*[@id='resultTable']/table")
                        
                        combined = {}  # combine all tables into one dictionary
                        for i in range(0, len(city_data)):
                            city = city_data[i]
                            for key, value in city.items():
                                    if key in combined:
                                        combined[key].update(value)
                                    else:
                                        combined[key] = value
                    
                        time.sleep(1)       
                        all_cities.append(combined)
                        if exit_table(True):
                            break
            
                        if not city_span_init: # first page next button has a different xpath than subsequent pages
                            wait_and_click("/html/body/div[1]/div[5]/div[2]/div[1]/div[1]/table/tbody/tr/td[2]/div[2]/span[1]", click_btn)
                            city_span_init = True
                        else:
                            wait_and_click("/html/body/div[1]/div[5]/div[2]/div[1]/div[1]/table/tbody/tr/td[2]/div[2]/span[3]", click_btn)
                        time.sleep(1)
                        wait_for_element("//*[@id='results']")
                    
                    cities = all_cities[0]
                    for city in all_cities:
                        for key, value in city.items():
                            cities[key] = value

                    file = open("./Data Acquisition/city_data.csv", 'a')
                    for city, attrib in cities.items():
                        city = city.replace(", {}".format(stateName), "")
                        line = "{}, {}, {}, ".format(stateName, 2019 - yearI, city)
                        title = "STATE, YEAR, CITY, "
                        i = 0
                        for attribName, attribValue in attrib.items():
                            if not file_init:
                                attribName = attribName.replace(',', '')
                                if i < len(attrib.values()) - 1:
                                    title += "{},".format(attribName)
                                else:
                                    title += "{}\n".format(attribName)
                            try:
                                attribValue = attribValue.replace(',', '')
                                value = float(attribValue)
                            except:
                                if attribValue == "null":
                                    value = "null"
                                else:
                                    value = float(attribValue[1:]) # dollars
                            if i < len(attrib.values()) - 1:
                                line += "{}, ".format(value)
                            else:
                                line += "{}\n".format(value)
                            i += 1
                        if not file_init:
                            file.write(title)
                            file_init = True
                        file.write(line)
                        processed += 1
                        if rows != None and processed >= rows:
                            return
                
                    year = {2019 - yearI: cities}   
                    parsed_state_data[stateName] = year
                
                    driver.get(curr_url)
                except:
                    print("Skipping {} in {}".format(stateName, 2019-yearI))
                    driver.get(curr_url)
                    continue
                     
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

def exit_table(isCity):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    links = soup.find("td", {"class": "links"})
    if isCity:
        div = links.find_all("div")[1]
    else:
        div = links.find_all("div")[0]
    for span in div.find_all("span"):
        if span.text == "Next":
            return False
    return True

def parse_table():
    wait_for_element("//*[@id='resultTable']/table")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    cities = {}
    table = soup.find("table", {"class": "TableReportResults"})
    
    tBody = table.find("tbody")
    city_tr = tBody.find("tr", {"class": "RTGeoHeaderRow"})
    
    city_indices = {}
    for i, city in enumerate(city_tr.find_all("td", {"class": "RTGeoRowDataCol"})):
        city_indices[i] = city.text
        cities[city.text] = {}
      
    data_rows = tBody.find_all("tr", {"class": "RTVarRow"})
    for row in data_rows:
        attrib_name_elem = row.find("td", {"class": "RTVarName"})
        attrib_name_div = attrib_name_elem.find("div")
        attrib_name = attrib_name_div.text
        
        for i, attrib in enumerate(row.find_all("td", {"class": "RTVarRowDataCol"})):
            name = attrib_name.replace(":", "")
            if attrib.text == "":
                cities[city_indices[i]][name] = "null"
            else:
                cities[city_indices[i]][name] = attrib.text
    
    return cities
     
sensitive = get_keys()
states = {} # parse HTML to get stateNums and stateNames for use in select_place function
parsed_state_data = {}
    
city_properties = ["Total Population", "Population Density", "Land Area", "Sex", "Race", "Households by Household Type", "Household Size (Renter-Occupied Housing Units", "Educational Attainment for Population 25 Years and Over", "Employment Status for Total Population", "Unemployment Rate for Civilian Population", "Industry by Occupation for Employed Civilian Population", "Average Household Income", "Gini Index", "Means of Transportation to Work for Workers"]

sol_explore = "https://www.socialexplorer.com/explore-tables"
driver = webdriver.Chrome(executable_path='C:/Users/manam/Desktop/chromedriver_win32/chromedriver.exe')
driver.get(sol_explore)


