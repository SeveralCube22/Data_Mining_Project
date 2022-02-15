from multiprocessing.connection import wait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

def get_keys():
    f = open("./sensitive.txt", "r")
    for line in f:
        (key, value) = line.split(",")
        sensitive[key] = value
        
def login():
    username = driver.find_element(By.XPATH, "//*[@id='email-field']")
    username.send_keys(sensitive["USERNAME"])
    pswd = driver.find_element(By.XPATH, "//*[@id='passwordInput']")
    pswd.send_keys(sensitive["PASSWORD"])
    wait_and_click("//*[@id='application']/div/div/div[3]/form/div[1]/button", click_btn)

def click_btn(xpath):
    btn = driver.find_element(By.XPATH, xpath)
    driver.execute_script ("arguments[0].click();", btn)

def wait_for_element(xpath):
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath)))

def wait_and_click(xpath, func, **values):
    wait_for_element(xpath)
    value = values.get("value")
    func(xpath, value) if value else func(xpath)
    
def select(xpath, value):
    selector = Select(driver.find_element(By.XPATH, xpath))
    selector.select_by_value(value)
    
def select_place():
    xpath = "//*[@id='cmbGeoType']"
    wait_and_click(xpath, select, value="SL160") # select PLACE
    xpath = "//*[@id='geoCombosContainer']/div/select"
    wait_and_click(xpath, select, value="06;160;California") # select State(CA)
    xpath = "//*[@id='listGeoItems']"
    wait_and_click(xpath, select, value="06;160; ") # select all places(cities) in state
    
    click_btn("//*[@id='btnAddGeoItem']") # click add
    click_btn("//*[@id='btnGeoNext']") # click next
    
def select_properties():
    pass
    
    
sensitive = {}
get_keys()

sol_explore = "https://www.socialexplorer.com/explore-tables"
driver = webdriver.Chrome(executable_path='C:/Users/manam/Desktop/chromedriver_win32/chromedriver.exe')
driver.get(sol_explore)
login()

wait_and_click("//*[@id='dashboard']/div[5]/div/div/div[5]/div[1]/button", click_btn)

for i in range(11):
    click_btn("//*[@id='dashboard']/div[5]/div/div/div[5]/div[2]/div[{}]/div[2]/a[1]".format(2 + i)) # iterating over begin     report buttons for years 2009-2019
   
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))   
    child = driver.window_handles[1]      
    driver.switch_to.window(child) 
    
    select_place()
    select_properties()
    
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    
    # parse resultant html page
    

# Get crime data for every city(mentioned in ACS) in California from FBI api
