from multiprocessing.connection import wait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


def click_btn(xpath):
    btn = driver.find_element(By.XPATH, xpath)
    driver.execute_script ("arguments[0].click();", btn)

def wait_for_element(xpath):
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath)))

def wait_and_click(xpath):
    wait_for_element(xpath)
    click_btn(xpath)
    
def select_place():
    (place, state, cities) = "//*[@id='cmbGeoType']/option[7]", "//*[@id='geoCombosContainer']/div/select/option[6]", "//*[@id='listGeoItems']/option[2]"
    
    print("BEFORE")
    wait_and_click(place) # select PLACE
    print("AFTER")
    wait_and_click(state) # select State(CA)
    wait_and_click(cities) # select all places(cities) in state
    
    click_btn("//*[@id='btnAddGeoItem']") # click add
    click_btn("//*[@id='btnGeoNext']") # click next
    
def select_properties():
    pass
    
sol_explore = "https://www.socialexplorer.com/explore-tables"

driver = webdriver.Chrome(executable_path='C:/Users/manam/Desktop/chromedriver_win32/chromedriver.exe')
driver.get(sol_explore)
click_btn("//*[@id='dashboard']/div[5]/div/div/div[5]/div[1]/button")

for i in range(11):
    click_btn("//*[@id='dashboard']/div[5]/div/div/div[5]/div[2]/div[{}]/div[2]/a[1]".format(2 + i)) # iterating over begin     report buttons for years 2009-2019
   
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))   
    child = driver.window_handles[1]      
    driver.switch_to.window(child) 
    
    select_place()
    select_properties()
    
    # parse resultant html page
    

# Get crime data for every city(mentioned in ACS) in California from FBI api
