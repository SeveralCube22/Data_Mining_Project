from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sol_explore = "https://www.socialexplorer.com/explore-tables"

driver = webdriver.Chrome(executable_path='C:/Users/manam/Desktop/chromedriver_win32/chromedriver.exe')
driver.get(sol_explore)
acs_btn = driver.find_element(By.XPATH, "//*[@id='dashboard']/div[5]/div/div/div[5]/div[1]/button")
driver.execute_script ("arguments[0].click();", acs_btn)

for i in range(11):
    report_btn = driver.find_element(By.XPATH, "//*[@id='dashboard']/div[5]/div/div/div[5]/div[2]/div[{}]/div[2]/a[1]".format(2 + i)) # iterating over begin report   
                                                                                                                                     # buttons for years 2009-2019
    
    driver.execute_script ("arguments[0].click();", report_btn)
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))   
    child = driver.window_handles[1]      
    driver.switch_to.window(child) 
    print(driver.current_url)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

# Get crime data for every city(mentioned in ACS) in California from FBI api
