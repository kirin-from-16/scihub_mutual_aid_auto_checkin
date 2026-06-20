"""
Automate daily check-in on SmartQuant (smartquantai.com).
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
import logging

# Header check-in link from are_sign plugin (see debug_page_after_login.html).
CHECKIN_LINK_HREF = "are_sign:getaward"
# Icon shown after check-in is done for the day (see already_checkin.html).
ALREADY_CHECKIN_ICON = "yqd.png"

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Clear default handlers to prevent duplicate logging
logger.handlers.clear()

# Add main handler for INFO and below (excluding ERROR)
main_handler = logging.FileHandler("smartquant_login.log", mode='a')
main_handler.setLevel(logging.INFO)
main_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
main_handler.addFilter(lambda record: record.levelno < logging.ERROR)
logger.addHandler(main_handler)

# Add error logger
error_handler = logging.FileHandler("smartquant_error.log", mode='a')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(error_handler)

# Add console handler for non-error messages only
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
console_handler.addFilter(lambda record: record.levelno < logging.ERROR)
logger.addHandler(console_handler)

# # Set logger level
# logger.setLevel(logging.INFO)

class SmartQuantAutoCheckin:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.url = "https://www.smartquantai.com/"
        self.setup_driver()
        
    def setup_driver(self):
        """Set up the Chrome WebDriver with appropriate options."""
        try:
            chrome_options = Options()
            # Uncomment the line below to run in headless mode (no browser UI)
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--start-maximized")
            # chrome_options.add_experimental_option("detach", True)  # Keep browser open
            
            # service = Service(ChromeDriverManager().install())
            # self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver = webdriver.Chrome(options=chrome_options)
            
            logger.info("WebDriver set up successfully")
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {e}")
            raise
    
    def login(self):
        """Navigate to the website and log in."""
        try:
            logger.info(f"Navigating to {self.url}")
            self.driver.get(self.url)
            time.sleep(3)  # Wait for page to load
            
            # Click on Sign in button
            logger.info("Clicking Sign in button")
            sign_in_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Sign in')]"))
            )
            sign_in_button.click()
            time.sleep(2)
            
            # Enter username
            logger.info("Entering username")
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))  # Adjust ID as needed
            )
            username_field.send_keys(self.username)
            time.sleep(2)
            
            # Enter password
            logger.info("Entering password")
            password_field = self.driver.find_element(By.NAME, "password")  # Adjust ID as needed
            password_field.send_keys(self.password)
            time.sleep(2)
            
            # Click login button
            logger.info("Clicking login button")
            login_button = self.driver.find_element(By.NAME, "loginsubmit")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            # Check if login was successful
            if "visit my space" in self.driver.page_source.lower():
                logger.info("Login successful")
                return True
            else:
                logger.error("Login failed")
                return False
                
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False

    def _is_already_checked_in(self):
        """Return True when today's check-in icon is shown in the header."""
        return ALREADY_CHECKIN_ICON in self.driver.page_source.lower()

    def check_in(self):
        """Click the daily check-in link in the site header and verify the result."""
        try:
            if self._is_already_checked_in():
                logger.info("Already checked in today")
                return True

            # <a href="plugin.php?id=are_sign:getaward&typeid=1">
            checkin_links = self.driver.find_elements(
                By.XPATH, f"//a[contains(@href, '{CHECKIN_LINK_HREF}')]"
            )
            if not checkin_links:
                logger.error("Check-in link not found and not already checked in today")
                return False

            logger.info("Clicking daily check-in link")
            checkin_link = checkin_links[0]
            href = checkin_link.get_attribute("href")
            logger.info(f"Opening check-in URL: {href}")
            checkin_link.click()
            time.sleep(3)  # Wait for check-in to complete

            return self._verify_checkin_success()

        except Exception as e:
            logger.error(f"Error during check-in: {e}")
            return False

    def _verify_checkin_success(self):
        """Confirm check-in: header icon changes to yqd.png (see already_checkin.html)."""
        if self._is_already_checked_in():
            logger.info("Check-in successful (yqd.png detected)")
            return True

        logger.error(
            f"Check-in could not be confirmed (yqd.png not found). "
            f"Current URL: {self.driver.current_url}"
        )
        return False

    def run(self):
        """Log in, perform daily check-in, and return overall success."""
        logger.info("Starting auto check-in")
        if not self.login():
            return False
        if not self.check_in():
            return False
        logger.info("Auto check-in completed successfully")
        return True
    
    def close(self):
        """Close the browser."""
        try:
            self.driver.quit()
            logger.info("Browser closed successfully")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")

def main():
    # Get credentials from environment variables or enter them directly
    username = os.environ.get("SMARTQUANT_USERNAME", "your_username")
    password = os.environ.get("SMARTQUANT_PASSWORD", "your_password")
    
    bot = SmartQuantAutoCheckin(username, password)
    
    # try:
    success = bot.run()
    if not success:
        logger.error("Auto check-in did not complete successfully")

    # finally:
    #     pass    
    # bot.close()

if __name__ == "__main__":
    import time
    from dotenv import load_dotenv
    load_dotenv('.env', override=True)
    main() 
    with open(".script_log.txt", "a") as f:
        f.write(f"Finish running auto check in script at {time.ctime()}\n")
