import time
from abc import ABC, abstractmethod
from typing import Optional, List
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException

class BaseBrowser(ABC):
    """Base class for browser interactions with enhanced error handling and typing."""
    
    def __init__(self):
        self.driver = None
    
    def wait_presence(self, xpath: str, timeout: int = 3) -> bool:
        """Wait for element presence with explicit typing and error handling."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return True
        except TimeoutException:
            return False
        except WebDriverException as e:
            print(f"Browser error while waiting for element: {e}")
            return False

    def find_element(
        self, 
        xpath: str, 
        timeout: int = 10,
        wait_type: str = "presence"
    ) -> Optional[WebElement]:
        """Find element with multiple wait conditions and error handling."""
        try:
            wait_conditions = {
                "presence": EC.presence_of_element_located,
                "clickable": EC.element_to_be_clickable,
                "visible": EC.visibility_of_element_located
            }
            condition = wait_conditions.get(wait_type, EC.presence_of_element_located)
            return WebDriverWait(self.driver, timeout).until(
                condition((By.XPATH, xpath))
            )
        except TimeoutException:
            print(f"Timeout waiting for element: {xpath}")
            return None
        except WebDriverException as e:
            print(f"Browser error finding element: {e}")
            return None

    def find_elements(
        self, 
        xpath: str, 
        timeout: int = 10
    ) -> List[WebElement]:
        """Find multiple elements with error handling."""
        try:
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
            return elements
        except TimeoutException:
            print(f"Timeout waiting for elements: {xpath}")
            return []
        except WebDriverException as e:
            print(f"Browser error finding elements: {e}")
            return []

    def click_element(
        self, 
        xpath: str, 
        timeout: int = 10,
        retry_count: int = 2
    ) -> bool:
        """Click element with retry mechanism and error handling."""
        for attempt in range(retry_count):
            try:
                element = self.find_element(xpath, timeout, wait_type="clickable")
                if element:
                    element.click()
                    return True
                time.sleep(0.5)
            except WebDriverException as e:
                if attempt == retry_count - 1:
                    print(f"Failed to click element after {retry_count} attempts: {e}")
                    return False
        return False

    def send_keys(
        self, 
        xpath: str, 
        keys: str,
        clear_first: bool = True
    ) -> bool:
        """Send keys to element with optional clearing."""
        try:
            element = self.find_element(xpath)
            if element:
                if clear_first:
                    element.clear()
                element.send_keys(keys)
                return True
            return False
        except WebDriverException as e:
            print(f"Error sending keys to element: {e}")
            return False

    def is_element_present(
        self, 
        xpath: str, 
        timeout: int = 10
    ) -> bool:
        """Check element presence with explicit timeout."""
        return self.wait_presence(xpath, timeout)

    def get_element_text(
        self, 
        xpath: str, 
        timeout: int = 10
    ) -> Optional[str]:
        """Get element text with error handling."""
        element = self.find_element(xpath, timeout)
        if element:
            return element.text
        return None

    def get_element_attribute(
        self, 
        xpath: str, 
        attribute: str, 
        timeout: int = 10
    ) -> Optional[str]:
        """Get element attribute with error handling."""
        element = self.find_element(xpath, timeout)
        if element:
            return element.get_attribute(attribute)
        return None