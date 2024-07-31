import time
from ..base import BaseLLMProvider
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ChatGPTProvider(BaseLLMProvider):
    def __init__(self, browser, config):
        super().__init__(browser, config)
        self.browser.driver.get(self.config['url'])
        self.latest_response_id = None

    def send_message(self, message: str) -> None:
        input_box = self._find_element(self.config['input_xpath'])
        input_box.clear()
        input_box.send_keys(message)
        self._click_element(self.config['send_button_xpath'])
        # input_box.send_keys(Keys.RETURN)

    def stop_generating(self, interval:int = 0.5, attempts: int = 2) -> bool:
        for _ in range(attempts):
            try:
                self._click_element(self.config['stop_button_xpath'])
                return True
            except:
                time.sleep(interval)
        return False

    def get_response(self) -> str:
        responses = self._find_elements(self.config['response_xpath'])
        if responses:
            return responses[-1].text
        return ""

    def get_responses(self) -> str:
        responses = self._find_elements(self.config['response_xpath'])
        return [response.text for response in responses]

    def list_chats(self) -> list:
        chat_elements = self.browser.driver.find_elements(By.XPATH, self.config['chat_list_xpath'])
        chat_elements = self._find_elements(By.XPATH, self.config['chat_list_xpath'])
        return [chat.text for chat in chat_elements]

    def select_chat(self, chat_id: str) -> None:
        chat_xpath = f"{self.config['chat_list_xpath']}[contains(@data-id, '{chat_id}')]"
        self._click_element(chat_xpath)

    def select_model(self, model_name: str) -> None:
        selector = self._find_element(self.config['model_selector_xpath'])
        selector.click()
        model_option = self._find_element(f"//option[text()='{model_name}']")
        model_option.click()
    
    def wait_for_response_completion(self, timeout: int = 300) -> bool:
        status = self.check_llm_response_status()
        if status:
            start_time = time.time()
            prev_response = ""
            while time.time() - start_time < timeout:
                response = self.get_response()
                if prev_response != response:
                    prev_response = response
                else:
                    if self._is_element_present(self.config['send_button_xpath'], timeout=1):
                        return True
                time.sleep(0.3)
            return False
        return False
    
    def update_latest_response_id(self):
        try:
            response = self._find_element(self.config['response_xpath'])
            if response:
                self.latest_response_id = response.get_attribute("data-message-id")
        except Exception as e:
            pass
    
    def check_llm_response_status(self, timeout: int = 10) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self._find_element(self.config['response_xpath'], timeout=1)
                current_id = response.get_attribute("data-message-id")
                if current_id != self.latest_response_id:
                    self.latest_response_id = current_id
                    return True
            except Exception as e:
                pass
            time.sleep(1)
        return False