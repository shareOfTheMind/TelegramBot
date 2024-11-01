import os
import subprocess
from config.tgram_bot_logger import write_log

from seleniumwire import webdriver
import time
import signal


# Configure Selenium to use the Mitmproxy
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors') 

driver = webdriver.Chrome(options=options, seleniumwire_options={"enable_har": True})

def parse_tiktok_data(account_link: str):
    try:
        #write_log(message=f"Navigating to {account_link}", level="info")
        print(f"Navigating to {account_link}")
        driver.get(account_link)
        # Pause if necessary to allow data to load
        time.sleep(5)
        with open("/tmp/output.har", "w") as o:
            o.write(driver.har)
        # write_log(message=f"Data loaded from {account_link}", level="info")
        print(f"Data loaded from {account_link}")
    except Exception as e:
        # write_log(message=f"Error while loading {account_link}: {e}", level="info")
        print(f"Error while loading {account_link}: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    try:
        # Run the parse function with a test account link
        parse_tiktok_data("https://www.tiktok.com/@mrbeast")
    finally:
        pass
