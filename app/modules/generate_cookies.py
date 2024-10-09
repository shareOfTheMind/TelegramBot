import time
import os

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from config.tgram_bot_logger import write_log
from . import IG_PASS


# Path to Edge WebDriver executable
EDGE_WEBDRIVER_PATH = '/usr/local/bin/msedgedriver'  # Replace with the actual path to your msedgedriver.exe



def generate_cookies(user='tgrambotlord', pwd='') -> bool:
    '''
        #### Generates an IG loader session from cookies extracted from an on-the-fly browser driver session
    '''

    # Initialize WebDriver service
    service = EdgeService(executable_path=EDGE_WEBDRIVER_PATH)

    # Initialize WebDriver
    options = webdriver.EdgeOptions()
    options.use_chromium = True
    options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--no-sandbox')  # Disable sandbox (may be necessary)
    options.add_argument('--disable-dev-shm-usage')  # Overcome some resource limitations
    driver = webdriver.Edge(service=service, options=options)

    if not pwd:
        pwd = IG_PASS

    try:

        if not pwd:
            write_log(message=f"!! No Instagram Password Supplied for Session Generation !!", level='warning')
            raise ValueError('NO INSTAGRAM PASSWORD SUPPLIED')
        
        
        write_log(message="Using WebDriver to Access Instagram Login Page..", level='info')
        # Open Instagram login page
        driver.get('https://www.instagram.com/accounts/login/')
        time.sleep(3)  # Wait for the page to load

        write_log(message="Entering Credentials to login to Instagram.com with..", level='info')
        # Enter username
        username_input = driver.find_element(By.NAME, 'username')
        username_input.send_keys(user)

        # Enter password
        password_input = driver.find_element(By.NAME, 'password')
        password_input.send_keys(pwd)
        password_input.send_keys(Keys.RETURN)

        # Wait for login to complete
        time.sleep(10)


        # Check if redirected to a challenge page
        if "challenge" in driver.current_url:
            write_log(message="Challenge page detected. Trying to dismiss.", level='info')
            try:
                
                # Wait for the "Dismiss" button to become clickable (updated method to handle the dynamically loaded challenge modal)
                dismiss_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button/span[contains(text(), 'Dismiss')]/.."))
                )

                dismiss_button.click()

                time.sleep(10)  # Wait for the action to complete

                # Verify if redirected back to the login page or another page
                if "challenge" in driver.current_url:
                    write_log(message="Still on the challenge page. Manual intervention may be required.", level='warning')
                else:
                    write_log(message="Dismissed challenge successfully.", level='info')
            except Exception as e:
                write_log(message=f"An error occurred while trying to dismiss the challenge ({type(e)})", level='error')
                write_log(message=f"Page returned as PDF for Anaylsis ({driver.print_page()}", level='debug')
                # write_log(message=f"Here is the page source code for the challenge {driver.page_source}.", level='error')
                return False


        write_log(message='Extracting necessary cookies after logging into Instagram', level='info')
        # Extract cookies
        cookies = driver.get_cookies()

        # Filter necessary cookies for Instagram login
        necessary_cookies = {cookie['name']: cookie['value'] for cookie in cookies if cookie['name'] in ['csrftoken', 'sessionid']}

        if 'csrftoken' not in necessary_cookies or 'sessionid' not in necessary_cookies:
            write_log(message="Required cookies not found. Please check your login process.", level='error')
            # raise SystemExit("Required cookies not found. Please check your login process.")
        
        # Write cookies to a file
        with open('instagram_cookie_info.txt', 'w') as f:
            for name, value in necessary_cookies.items():
                f.write(f"{name}={value}\n")
       
        write_log(message="Successfully imported cookies from Edge and saved to file.", level='info')

    except Exception as ex:
        write_log(message=f"Unkown Script error occured in Session Generation\n{ex}", level='error')
        return False
    finally:
        driver.quit()

    return True

def read_cookies_from_file(path:str) -> dict:
    '''
        Reads cookies from a file and returns them as a dictionary. 

        path: the path to the cookie info file. currently should only be: 
                'instagram_cookie_info.txt'
                'tiktok_cookie_info.txt'
    '''

    cookies = {}
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()  # Remove any surrounding whitespace or newline characters
                if '=' in line:  # Ensure the line has the correct format
                    name, value = line.split('=', 0)  # Split only at the first '='
                    cookies[name] = value
    except FileNotFoundError:
        write_log(message=f"Cookie file '{path}' not found. Please generate cookies first.", level='error')

    return cookies