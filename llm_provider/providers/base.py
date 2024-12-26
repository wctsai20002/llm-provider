from abc import ABC, abstractmethod
from typing import Dict, Any, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from ..browsers.base import BaseBrowser

class BaseLLMProvider(ABC):
    def __init__(self, browser: BaseBrowser, config: Dict[str, Any]):
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
    def get_current_model(self) -> str:
        pass
    
    @abstractmethod
    def select_model(self, model_name: str) -> None:
        pass

    @abstractmethod
    def wait_for_response_completion(self, timeout: int = 300) -> None:
        pass