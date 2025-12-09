from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def before_all(context):
    # Setup Chrome Driver
    service = Service(ChromeDriverManager().install())
    context.driver = webdriver.Chrome(service=service)
    context.driver.implicitly_wait(5) # Wait up to 5 seconds for elements to appear
    context.driver.maximize_window()

def after_all(context):
    # Close browser after tests
    context.driver.quit()