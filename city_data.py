from multiprocessing.connection import wait
from operator import truediv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from sensitive import get_keys

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
    print("OUTER")
    if(stateValue == None):
        global states
        states = get_state_data() # have to do this because HTML attributes doesn't show initially
        
    else:
        print("PRINTING", stateValue)
        wait_and_click(xpath, select, value=stateValue) # select state
        print("HERE")
        
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
    
    print("PROPERTIES OPTIONS")
    
    for prop in city_properties:
        for super in properties: # list of options
            if is_subset(super.text, prop):
                print(super.text, prop)
                wait_and_click(select_xpath, select, value=super["value"])
                click_btn("//*[@id='btnAddTable']") # click add
                break
            
    click_btn("//*[@id='btnTableNext']") # click next

def is_subset(super, sub):
    for word in sub:
        if word not in super:
            return False
    return True
    

def get_city_data():
    wait_and_click("//*[@id='dashboard']/div[5]/div/div/div[5]/div[1]/button", click_btn)
    init = False
    
    for i in range(11):
        click_btn("//*[@id='dashboard']/div[5]/div/div/div[5]/div[2]/div[{}]/div[2]/a[1]".format(2 + i)) # iterating over begin     report buttons for years 2009-2019
   
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))   
        child = driver.window_handles[1]      
        driver.switch_to.window(child)
        if not init: 
            select_place()
            init = True
        
        for (key, value) in states.items():
            if(key in state.scrape_states.keys()):
                select_place(value) # pass state(other terrorties included) num 1-72 and state name
                select_properties()

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
    
    # parse resultant html page
    

# Get crime data for every city(mentioned in ACS) in California from FBI api
     
sensitive = get_keys()
states = {} # parse HTML to get stateNums and stateNames for use in select_place function

city_properties = ["Total Population", "Population Density", "Land Area", "Sex by Age", "Race", "Households by Household Type", "Household Size (Renter-Occupied Housing Units", "Educational Attainment for Population 25 Years and Over", "School Dropout Rate for Population 16 to 19 Years", "Employment Status for Total Population", "Unemployment Rate for Civilian Population", "Industry by Occupation for Employed Civilian Population", "Occupation for Employed Civilian Population", "Average Household Income", "Average Household Income by Race", "Gini Index", "Housing Units by Monthly Housing Costs", "Poverty Status for Population Age 18 to 64", "Poverty Status for Population Age 65 and Over", "Means of Transportation to Work for Workers"]

sol_explore = "https://www.socialexplorer.com/explore-tables"
driver = webdriver.Chrome(executable_path='C:/Users/manam/Desktop/chromedriver_win32/chromedriver.exe')
driver.get(sol_explore)

try: # sometimes website asks to login other times it doesn't
    login()
    get_city_data()
except:
    get_city_data()

