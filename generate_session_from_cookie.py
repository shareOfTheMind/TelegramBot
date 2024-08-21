import time
import os

from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from instaloader import Instaloader, ConnectionException

from tgram_bot_logger import write_log


# Path to Edge WebDriver executable
EDGE_WEBDRIVER_PATH = '/usr/local/bin/msedgedriver'  # Replace with the actual path to your msedgedriver.exe

# Instagram credentials
INSTAGRAM_USERNAME = os.getenv('IG_USER')
INSTAGRAM_PASSWORD = os.getenv('IG_PASS')



def generate_session_from_cookies() -> bool:
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

    try:
        if not INSTAGRAM_PASSWORD:
            write_log(message=f"!! No Instagram Password Supplied for Session Generation !!", level='warning')
            raise ValueError('NO INSTAGRAM PASSWORD SUPPLIED')
        
        
        write_log(message="Using WebDriver to Access Instagram Login Page..", level='info')
        # Open Instagram login page
        driver.get('https://www.instagram.com/accounts/login/')
        time.sleep(3)  # Wait for the page to load

        write_log(message="Entering Credentials to login to Instagram.com with..", level='info')
        # Enter username
        username_input = driver.find_element(By.NAME, 'username')
        username_input.send_keys(INSTAGRAM_USERNAME)

        # Enter password
        password_input = driver.find_element(By.NAME, 'password')
        password_input.send_keys(INSTAGRAM_PASSWORD)
        password_input.send_keys(Keys.RETURN)

        # Wait for login to complete
        time.sleep(10)


        # Check if redirected to a challenge page
        if "challenge" in driver.current_url:
            write_log(message="Challenge page detected. Trying to dismiss.", level='info')
            try:
                # Locate and click the 'Dismiss' button
                dismiss_button = driver.find_element(By.XPATH, '//button[text()="Dismiss"]')
                dismiss_button.click()
                time.sleep(10)  # Wait for the action to complete
                
                # Verify if redirected back to the login page or another page
                if "challenge" in driver.current_url:
                    write_log(message="Still on the challenge page. Manual intervention may be required.", level='info')
                else:
                    write_log(message="Dismissed challenge successfully.", level='info')
            except Exception as e:
                write_log(message=f"An error occurred while trying to dismiss the challenge: {e}", level='error')
                return False


        write_log(message='Extracting necessary cookies after logging into Instagram', level='info')
        # Extract cookies
        cookies = driver.get_cookies()

        # Filter necessary cookies for Instagram login
        necessary_cookies = {cookie['name']: cookie['value'] for cookie in cookies if cookie['name'] in ['csrftoken', 'sessionid']}

        if 'csrftoken' not in necessary_cookies or 'sessionid' not in necessary_cookies:
            write_log(message="Required cookies not found. Please check your login process.", level='error')
            # raise SystemExit("Required cookies not found. Please check your login process.")
        
        # Initialize Instaloader
        instaloader = Instaloader(max_connection_attempts=1)

        # Update Instaloader session cookies
        for name, value in necessary_cookies.items():
            instaloader.context._session.cookies.set(name, value)


        # Test login
        try:
            username = instaloader.test_login()
            if not username:
                write_log(message="Login test failed. Check your cookies and login process.", level='warning')
                return False
                # raise SystemExit("Login test failed. Check your cookies and login process.")
        except ConnectionException as e:
            write_log(message=f"Unkown Error Occurred during IG Loader Session Generation: {e}", level='error')
            return False
            # raise SystemExit(f"An error occurred during login: {e}")

        # session_file = ''
        instaloader.context.username = username
        instaloader.save_session_to_file()
        write_log(message="Successfully imported cookies from Edge and logged in.", level='info')

    except Exception as ex:
        write_log(message=f"Unkown Script error occured in Session Generation\n{ex}", level='error')
        return False
    finally:
        driver.quit()

    return True





#     # Filter necessary cookies for Instagram login
#     necessary_cookies = ['sessionid', 'csrftoken', 'mid', 'ds_user_id', 'shbid', 'shbts']
#     extracted_cookies = {cookie['name']: cookie['value'] for cookie in cookies if cookie['name'] in necessary_cookies}

#     # Initialize Instaloader
#     instaloader = Instaloader(max_connection_attempts=1)

#     # Update Instaloader session cookies
#     for name, value in extracted_cookies.items():
#         instaloader.context._session.cookies.set(name, value)