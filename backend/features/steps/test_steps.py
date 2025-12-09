from behave import given, when, then
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Helper to wait for elements
def wait_for_element(context, by, value):
    return WebDriverWait(context.driver, 10).until(
        EC.presence_of_element_located((by, value))
    )

@given('I open the Nexus AI application')
def step_open_app(context):
    # Ensure your React app is running on localhost:3000
    context.driver.get("http://localhost:5173")

@given('I enter "{text}" into the email field')
def step_enter_email(context, text):
    email_input = context.driver.find_element(By.CSS_SELECTOR, '[data-testid="email-input"]')
    email_input.clear()
    email_input.send_keys(text)

@given('I enter "{text}" into the password field')
def step_enter_password(context, text):
    pass_input = context.driver.find_element(By.CSS_SELECTOR, '[data-testid="password-input"]')
    pass_input.clear()
    pass_input.send_keys(text)

@given('I click the Login button')
def step_click_login(context,):
    btn = context.driver.find_element(By.CSS_SELECTOR, '[data-testid="login-btn"]')
    btn.click()
    time.sleep(2) # Wait for Firebase Auth to process

@then('I should see the dashboard')
def step_see_dashboard(context):
    # Check for the synthesize button as proof we are logged in
    wait_for_element(context, By.CSS_SELECTOR, '[data-testid="synthesize-btn"]')

@when('I enter "{text}" into the first text input')
def step_enter_summary_text(context, text):
    # Target the first card (index 0)
    text_area = context.driver.find_element(By.CSS_SELECTOR, '[data-testid="input-textarea-0"]')
    text_area.send_keys(text)

@when('I click the Synthesize button')
def step_click_synthesize(context):
    btn = context.driver.find_element(By.CSS_SELECTOR, '[data-testid="synthesize-btn"]')
    # Check if disabled, wait if needed
    if not btn.is_enabled():
        time.sleep(1) 
    btn.click()

@then('I should see the Summary Result section')
def step_see_results(context):
    # Wait for the result container to appear
    # Note: AI takes time, so we increase wait time here
    WebDriverWait(context.driver, 80).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="summary-result"]'))
    )

@then('the summary should contain text')
def step_verify_content(context):
    result_box = context.driver.find_element(By.CSS_SELECTOR, '[data-testid="summary-result"]')
    text = result_box.text
    assert len(text) > 0, "Summary result was empty"
    print(f"TEST PASSED: Generated Summary -> {text[:50]}...")