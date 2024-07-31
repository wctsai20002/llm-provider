# File: llm_provider/providers/chatgpt.py

from ..base import BaseLLMProvider
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ChatGPTProvider(BaseLLMProvider):
    def __init__(self, browser, config):
        super().__init__(browser, config)
        self.browser.driver.get(self.config['url'])

    def send_message(self, message: str) -> None:
        input_box = self._find_element(self.config['input_xpath'])
        input_box.clear()
        input_box.send_keys(message)
        input_box.send_keys(Keys.RETURN)

    def get_response(self) -> str:
        response_element = self._find_element(self.config['response_xpath'], timeout=30)
        return response_element.text

    def list_chats(self) -> list:
        chat_elements = self.browser.driver.find_elements(By.XPATH, self.config['chat_list_xpath'])
        return [chat.text for chat in chat_elements]

    def select_chat(self, chat_id: str) -> None:
        chat_xpath = f"{self.config['chat_list_xpath']}[contains(@data-id, '{chat_id}')]"
        self._click_element(chat_xpath)

    def select_model(self, model_name: str) -> None:
        selector = self._find_element(self.config['model_selector_xpath'])
        selector.click()
        model_option = self._find_element(f"//option[text()='{model_name}']")
        model_option.click()