import re
import time
from urllib.parse import urljoin
from typing import Dict, Any, List
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
        chats = []
        try:
            sidebar = self._find_element(self.config['sidebar_xpath'])
        except:
            return chats
        self.browser.driver.execute_script("arguments[0].scrollTop = 0;", sidebar)
        time.sleep(0.3)

        while True:
            self.browser.driver.execute_script("arguments[0].scrollTop += arguments[1];", sidebar, 1000)
            time.sleep(0.5)
            scroll_height = self.browser.driver.execute_script("return arguments[0].scrollHeight;", sidebar)
            client_height = self.browser.driver.execute_script("return arguments[0].clientHeight;", sidebar)
            scroll_position = self.browser.driver.execute_script("return arguments[0].scrollTop;", sidebar)
            
            if abs((scroll_height - client_height) - scroll_position) <= 5:
                break
        
        chats_element = self._find_element(self.config['sidebar_xpath'])
        li_elements = chats_element.find_elements(By.TAG_NAME, 'li')
        for li in li_elements:
            a_element = li.find_element(By.TAG_NAME, 'a')
            url = a_element.get_attribute('href') if a_element else None
            title = li.text

            pattern = r"/c/([^/]+)$"
            match = re.search(pattern, url)

            if match:
                chat_id = match.group(1)
                chats.append({
                    'title' : title, 
                    'url' : url, 
                    'chat_id' : chat_id
                })
        
        return chats

    def select_chat(self, chat_id: str) -> None:
        chat_url = urljoin(self.config['chat_base_url'], chat_id)
        self.browser.driver.get(chat_url)

    def get_current_model(self) -> str:
        model_element = self._find_element(self.config['model_xpath'])
        return model_element.text

    def select_model(self, model_name: str) -> None:
        model_selector = self._find_element(self.config['model_xpath'])
        model_selector.click()
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