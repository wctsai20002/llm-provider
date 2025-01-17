import os
import re
import time
from urllib.parse import urljoin
from typing import Dict, Any, List
from .base import BaseLLMProvider
from ..browsers.base import BaseBrowser
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from markdownify import markdownify as md
from bs4 import BeautifulSoup
from ..utils.preprocessing import *

class ClaudeProvider(BaseLLMProvider):
    def __init__(self, browser: BaseBrowser, config: Dict[str, Any]):
        super().__init__(browser, config)
        self.browser.driver.get(self.config['url'])

    def send_message(self, message: str) -> bool:
        send_status = self.browser.send_keys(self.config['input_xpath'], message, clear_first=True)
        click_status = self.browser.click_element(self.config['send_button_xpath'])
        return send_status and click_status

    def stop_generating(self, interval:int = 0.5, attempts: int = 2) -> bool:
        for _ in range(attempts):
            try:
                self.browser.click_element(self.config['stop_button_xpath'])
                return True
            except:
                time.sleep(interval)
        return False

    def get_response(self) -> dict:
        response_dict = {
            'chat': {
                'html': None,
                'text': None,
                'markdown': None
            }, 
            'artifact': [

            ]
        }

        responses = self.browser.find_elements(self.config['response_xpath'])
        if not responses:
            return response_dict
        
        # Get the latest response element
        latest_response = responses[-1]
        html_content = latest_response.get_attribute('outerHTML')
        soup = BeautifulSoup(html_content, 'html.parser')
        target_span = soup.find('button', {
            'aria-label': 'Preview contents'
        })
        if target_span and target_span.parent:
            target_span.parent.decompose()
        html_content = str(soup)

        response_dict['chat']['html'] = html_content
        response_dict['chat']['text'] = soup.text
        response_dict['chat']['markdown'] = md(clean_html_claude(response_dict['chat']['html']))
        
        if not self.config['artifact_button_xpath'].startswith('.'):
            self.config['artifact_button_xpath'] = f".{self.config['artifact_button_xpath']}"

        try:
            artifact_buttons = latest_response.find_elements(By.XPATH, self.config['artifact_button_xpath'])
        except:
            artifact_buttons = None
        
        if artifact_buttons:
            for artifact_index in range(len(artifact_buttons)):
                artifact_buttons = latest_response.find_elements(By.XPATH, self.config['artifact_button_xpath'])
                if artifact_index >= len(artifact_buttons):
                    continue
                artifact_button = artifact_buttons[artifact_index]

                try:
                    if artifact_button:
                        self.browser.driver.execute_script('arguments[0].scrollIntoView(true);', artifact_button)
                        self.browser.random_delay(3, 5)
                        artifact_button.click()
                        self.browser.random_delay(5, 10)
                except Exception as e:
                    print(f'Error clicking textdoc button: {e}')
                    continue
                
                artifact_response = {
                    'html': None,
                    'text': None,
                    'markdown': None
                }

                code_artifact = self.browser.find_element(self.config['code_artifact_xpath'])
                if code_artifact:
                    code_language = code_artifact.get_attribute('class').replace('language-', '')
                    artifact_response['html'] = code_artifact.get_attribute('outerHTML')
                    artifact_response['text'] = code_artifact.get_attribute('innerText')
                    artifact_response['markdown'] = f'```{code_language}\n{artifact_response["text"]}\n```'
                    response_dict['artifact'].append(artifact_response)
                    continue

                text_artifact = self.browser.find_element(self.config['text_artifact_xpath'])
                if text_artifact:
                    artifact_response['html'] = text_artifact.get_attribute('outerHTML')
                    artifact_response['text'] = text_artifact.get_attribute('innerText')
                    artifact_response['markdown'] = md(artifact_response['html'])
                    response_dict['artifact'].append(artifact_response)
                    continue

                iframe_artifact = self.browser.find_element(self.config['iframe_artifact_xpath'])
                if iframe_artifact:
                    print('Unsupported iframe artifact!')
                    # artifact_response['html'] = iframe_artifact.get_attribute('outerHTML')
                    # artifact_response['text'] = iframe_artifact.get_attribute('innerText')
                    # artifact_response['markdown'] = md(artifact_response['html'])
                    # response_dict['artifact'].append(artifact_response)
                    continue
        
        return response_dict

    def get_responses(self) -> str:
        responses = self.browser.find_elements(self.config['response_xpath'])
        return [response.get_attribute('innerText') for response in responses]

    def list_chats(self) -> list:
        original_url = self.browser.driver.current_url
        chats = []

        self.browser.driver.get(self.config['chat_list_url'])
        self.browser.wait_presence(self.config['chat_list_xpath'])

        last_height = self.browser.driver.execute_script('return document.body.scrollHeight')
        
        while True:
            self.browser.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(0.5)
            new_height = self.browser.driver.execute_script('return document.body.scrollHeight')
            if new_height == last_height:
                break
            last_height = new_height
        
        li_elements = self.browser.find_elements(self.config['chat_list_xpath'])
        for li in li_elements:
            a_element = li.find_element(By.TAG_NAME, 'a')
            url = a_element.get_attribute('href') if a_element else None

            div_element = a_element.find_element(By.XPATH, './div/div[1]')
            title = div_element.get_attribute('innerText')

            pattern = rf"{self.config['chat_base_url']}([^/]+)$"
            match = re.search(pattern, url)

            if match:
                chat_id = match.group(1)
                chats.append({
                    'title' : title, 
                    'url' : url, 
                    'chat_id' : chat_id
                })
        
        self.browser.driver.get(original_url)
        self.browser.random_delay(10, 30)

        return chats

    def select_chat(self, chat_id: str) -> bool:
        try:
            chat_url = urljoin(self.config['chat_base_url'], chat_id)
            self.browser.driver.get(chat_url)
            self.browser.random_delay(10, 30)
            return True
        except:
            return False

    def hide_models_menu(self) -> bool:
        try:
            model_selector = self.browser.find_element(self.config['model_button_xpath'])
            if not model_selector:
                print('Model selector not found')
                return False
            
            # Check if menu is opened via aria-expanded attribute
            is_expanded = model_selector.get_attribute('aria-expanded') == 'true'
            if is_expanded:
                if not self.browser.click_element(self.config['model_button_xpath']):
                    print('Failed to close model selector')
                    return False
                return True
            
            return True  # Already closed, no action needed
            
        except Exception as e:
            print(f'Error hiding models menu: {e}')
            return False

    def open_models_menu(self) -> bool:
        try:
            model_selector = self.browser.find_element(self.config['model_button_xpath'])
            if not model_selector:
                print('Model selector not found')
                return False
            
            is_expanded = model_selector.get_attribute('aria-expanded') == 'true'
            if not is_expanded:
                if not self.browser.click_element(self.config['model_button_xpath']):
                    print('Failed to click model selector')
                    return False
            
            self.browser.random_delay(2, 5)

            more_models = self.browser.find_element(self.config['more_models_xpath'])
            if not more_models:
                print('More models element not found')
                return False
            
            actions = ActionChains(self.browser.driver)
            actions.move_to_element(more_models).perform()

            self.browser.random_delay(2, 5)
                
            return True
            
        except Exception as e:
            print(f'Error opening models menu: {e}')
            return False

    def get_current_model(self) -> str:
        model_element = self.browser.find_element(self.config['model_button_xpath'])
        if not model_element:
            return ''
            
        current_text = model_element.get_attribute('innerText')
        current_text = current_text.replace('Claude ', '').strip()
        
        for key, model_info in self.config['models'].items():
            model_name = model_info['name'].replace('Claude ', '').strip()
            if current_text == model_name:
                return key
                
        return ''

    def select_model(self, model_name: str) -> bool:
        if not self.open_models_menu():
            print('Failed to open models menu')
            return False
            
        model_info = self.config['models'].get(model_name)
        if not model_info:
            print(f'Model {model_name} not found in configuration')
            return False
            
        # XPath that matches both the model name and description
        model_xpath = self.config['model_description_xpath'].format(
            name=model_info['name'],
            description=model_info['description']
        )

        model_element = self.browser.find_element(model_xpath)
        if not model_element:
            print(f'Model element not found for {model_name}')
            return False
            
        model_element.click()
        self.browser.random_delay(5, 7)

        current_model = self.get_current_model()

        self.hide_models_menu()
        self.browser.random_delay(3, 5)

        return model_name == current_model
    
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
                    if self.check_file_button_status(timeout=1):
                        return True
                time.sleep(0.3)
            return False
        return False
    
    def check_send_button_status(self, timeout=10):
        button_element = self.browser.find_element(self.config['send_button_xpath'], timeout)
        is_disabled = button_element.get_attribute('disabled')
        return not is_disabled
    
    def check_file_button_status(self, timeout: int = 10) -> bool:
        return self.browser.is_element_present(self.config['file_button_xpath'], timeout=timeout)

    def check_llm_response_status(self, timeout: int = 10) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Find all response elements using the font-claude-message class
                responses = self.browser.find_elements(self.config['response_xpath'])
                if responses:
                    # Get the last (most recent) response
                    latest_response = responses[-1]
                    
                    # Check streaming status in parent div
                    parent_div = latest_response.find_element(By.XPATH, './/ancestor::div[@data-is-streaming]')
                    is_streaming = parent_div.get_attribute('data-is-streaming')
                    
                    # Use the response content and streaming status as the identifier
                    response_text = latest_response.get_attribute('innerText')
                    current_id = f'{response_text}_{is_streaming}'
                    
                    # Compare with stored latest response ID
                    if not hasattr(self, 'latest_response_id') or current_id != self.latest_response_id:
                        self.latest_response_id = current_id
                        return True
            except Exception as e:
                pass
            time.sleep(0.5)
        return False