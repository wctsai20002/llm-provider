from abc import ABC, abstractmethod
from typing import Dict, Any, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class BaseLLMProvider(ABC):
    def __init__(self, browser, config: Dict[str, Any]):
        self.browser = browser
        self.config = config

    @abstractmethod
    def send_message(self, message: str) -> None:
        pass
    
    @abstractmethod
    def stop_generating(self) -> None:
        pass

    @abstractmethod
    def get_response(self) -> str:
        pass

    @abstractmethod
    def get_responses(self) -> str:
        pass

    @abstractmethod
    def list_chats(self) -> list:
        pass

    @abstractmethod
    def select_chat(self, chat_id: str) -> None:
        pass

    @abstractmethod
    def select_model(self, model_name: str) -> None:
        pass

    @abstractmethod
    def wait_for_response_completion(self, timeout: int = 300) -> None:
        pass

    def _find_element(self, xpath: str, timeout: int = 10):
        return WebDriverWait(self.browser.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )

    def _find_elements(self, xpath: str, timeout: int = 10) -> List:
        return WebDriverWait(self.browser.driver, timeout).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath))
        )

    def _click_element(self, xpath: str):
        element = self._find_element(xpath)
        element.click()

    def _send_keys(self, xpath: str, keys: str):
        element = self._find_element(xpath)
        element.send_keys(keys)
    
    def _is_element_present(self, xpath: str, timeout: int = 10) -> bool:
        try:
            WebDriverWait(self.browser.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return True
        except TimeoutException:
            return False