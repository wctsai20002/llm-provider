import os
import re
import time
from urllib.parse import urljoin
from typing import Dict, Any, List, Optional
from .base import BaseLLMProvider
from ..browsers.base import BaseBrowser
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class ChatGPTProvider(BaseLLMProvider):
    def __init__(self, browser: BaseBrowser, config: Dict[str, Any]):
        super().__init__(browser, config)
        self.browser.driver.get(self.config['url'])
        self.latest_response_id = None

    def send_message(self, message: str) -> bool:
        send_status = self.browser.send_keys(self.config['input_xpath'], message, clear_first=True)
        click_status = self.browser.click_element(self.config['send_button_xpath'])
        return send_status and click_status

    def stop_generating(self, interval: int = 0.5, attempts: int = 2) -> bool:
        for _ in range(attempts):
            if self.browser.click_element(self.config['stop_button_xpath']):
                return True
            time.sleep(interval)
        return False

    def get_response(self) -> dict:
        response_dict = {
            'chat': None,
            'canvas': None
        }
        
        # Find all response elements
        responses = self.browser.find_elements(self.config['response_xpath'])
        if not responses:
            return response_dict
            
        # Get the latest response element
        latest_response = responses[-1]
        response_dict['chat'] = latest_response.text
        
        # Get the parent element to check for canvas indicators
        parent_element = latest_response.find_element(By.XPATH, '..')
        
        # Check for canvas by looking for sibling button element
        try:
            sibling_button = parent_element.find_element(By.XPATH, './button')
        except:
            sibling_button = None

        if sibling_button:
            # First look for and click the textdoc button
            try:
                textdoc_button = self.browser.find_element("//div[@role='button' and starts-with(@id, 'textdoc-message')]")
                if textdoc_button:
                    textdoc_button.click()
                    # Add a small delay to allow the section to load
                    self.browser.random_delay(3, 7)
            except Exception as e:
                print(f"Error clicking textdoc button: {e}")
                return response_dict
            
            # Find the editor container by ID
            header_title = self.browser.find_element("//header//h2").text.strip()
            editor_container = self.browser.find_element("//div[@id='prosemirror-editor-container']")

            if editor_container:
                # Initialize content list with header
                canvas_content = [f"# {header_title}\n"]
                
                # Get all markdown content elements
                editor = editor_container.find_element(By.CLASS_NAME, 'ProseMirror')
                
                # Process each content element maintaining proper markdown structure
                for element in editor.find_elements(By.XPATH, './/*'):
                    if element.tag_name in ['h3', 'h4', 'h5', 'h6']:
                        header_text = element.text.strip()
                        if header_text:
                            level = int(element.tag_name[1])  # Get header level
                            canvas_content.append(f"\n{'#' * level} {header_text}\n")
                            
                    elif element.tag_name == 'p':
                        para_text = element.text.strip()
                        if para_text:
                            canvas_content.append(f"{para_text}\n")
                            
                    elif element.tag_name == 'li':
                        li_text = element.text.strip()
                        if li_text:
                            canvas_content.append(f"- {li_text}\n")
                            
                    elif element.tag_name == 'hr':
                        canvas_content.append("\n---\n")
                        
                    elif element.tag_name == 'ul':
                        # Add extra newline before lists for proper markdown formatting
                        if canvas_content and not canvas_content[-1].endswith('\n\n'):
                            canvas_content.append('\n')
                
                # Join all content and clean up extra newlines
                if canvas_content:
                    full_content = ''.join(canvas_content)
                    # Clean up multiple newlines
                    cleaned_content = '\n'.join(line for line in full_content.split('\n') if line.strip())
                    response_dict['canvas'] = cleaned_content
        
        return response_dict

    def get_responses(self) -> List[str]:
        responses = self.browser.find_elements(self.config['response_xpath'])
        return [response.text for response in responses]
    
    def list_chats(self) -> List[Dict[str, Any]]:
        chats = []
        sidebar = self.browser.find_element(self.config['sidebar_xpath'])
        if not sidebar:
            return chats

        # Reset scroll position
        self.browser.driver.execute_script("arguments[0].scrollTop = 0;", sidebar)
        time.sleep(0.3)

        # Scroll to load all chats
        while True:
            self.browser.driver.execute_script("arguments[0].scrollTop += arguments[1];", sidebar, 1000)
            time.sleep(0.5)
            scroll_height = self.browser.driver.execute_script("return arguments[0].scrollHeight;", sidebar)
            client_height = self.browser.driver.execute_script("return arguments[0].clientHeight;", sidebar)
            scroll_position = self.browser.driver.execute_script("return arguments[0].scrollTop;", sidebar)
            
            if abs((scroll_height - client_height) - scroll_position) <= 5:
                break

        # Get chat elements
        li_elements = sidebar.find_elements(By.TAG_NAME, 'li')
        for li in li_elements:
            try:
                a_element = li.find_element(By.TAG_NAME, 'a')
                url = a_element.get_attribute('href') if a_element else None
                title = li.text
                
                pattern = rf"{self.config['chat_base_url']}([^/]+)$"
                match = re.search(pattern, url)

                if match:
                    chat_id = match.group(1)
                    chats.append({
                        'title': title,
                        'url': url,
                        'chat_id': chat_id
                    })
            except Exception as e:
                print(f"Error processing chat element: {e}")
                continue
        
        return chats

    def select_chat(self, chat_id: str) -> bool:
        try:
            chat_url = urljoin(self.config['chat_base_url'], chat_id)
            self.browser.driver.get(chat_url)
            return True
        except Exception as e:
            print(f"Error selecting chat: {e}")
            return False

    def hide_models_menu(self) -> bool:
        try:
            model_selector = self.browser.find_element(self.config['model_xpath'])
            if not model_selector:
                print("Model selector not found")
                return False
            
            # Check if menu is opened via aria-expanded attribute
            is_expanded = model_selector.get_attribute('aria-expanded') == 'true'
            if is_expanded:
                if not self.browser.click_element(self.config['model_xpath']):
                    print("Failed to close model selector")
                    return False
                return True
            
            return True  # Already closed, no action needed
            
        except Exception as e:
            print(f"Error hiding models menu: {e}")
            return False

    def open_models_menu(self) -> bool:
        try:
            # Find model selector button
            model_selector = self.browser.find_element(self.config['model_xpath'])
            if not model_selector:
                print("Model selector not found")
                return False
            
            # Check if menu is already opened
            is_expanded = model_selector.get_attribute('aria-expanded') == 'true'
            if not is_expanded:
                if not self.browser.click_element(self.config['model_xpath']):
                    print("Failed to click model selector")
                    return False
            
            # Click more models
            more_models = self.browser.find_element(self.config['more_models_xpath'])
            if not more_models:
                print("More models element not found")
                return False
            
            # Add random delay
            self.browser.random_delay(1.5, 3.5)
            
            if not self.browser.click_element(self.config['more_models_xpath']):
                print("Failed to click more models")
                return False

            self.browser.random_delay(1.5, 3.5)
                
            return True
            
        except Exception as e:
            print(f"Error opening models menu: {e}")
            return False

    def get_current_model(self) -> Optional[str]:
        try:
            # Click model selector button
            if not self.open_models_menu():
                return None

            # Iterate through all model xpaths
            for model_name, model_xpath in self.config['models'].items():
                try:
                    model_element = self.browser.find_element(model_xpath)
                    if model_element:
                        # Check if this element contains an SVG
                        svg_elements = model_element.find_elements(By.TAG_NAME, 'svg')
                        if svg_elements:
                            return model_name
                except Exception as e:
                    print(f"Error checking model {model_name}: {e}")
                    continue

            return None
            
        except Exception as e:
            print(f"Error getting current model: {e}")
            return None

        finally:
            self.hide_models_menu()

    def select_model(self, model_name: str) -> bool:
        if model_name not in self.config['models']:
            print(f"Model {model_name} not found in supported models")
            return False
        
        if not self.open_models_menu():
            return False
        
        model_xpath = self.config['models'][model_name]
        
        if not self.browser.click_element(model_xpath):
            print(f"Failed to select model {model_name}")
            return False
        
        self.hide_models_menu()

        return True
    
    def wait_for_response_completion(self, timeout: int = 300) -> bool:
        status = self.check_llm_response_status()
        if status:
            start_time = time.time()
            prev_response = ""
            while time.time() - start_time < timeout:
                response = self.get_response()['chat']
                if response != prev_response:
                    prev_response = response
                else:
                    if self.check_audio_button_status(timeout=1):
                        return True
                time.sleep(0.3)
        return False
    
    def check_send_button_status(self, timeout=10):
        button_element = self.browser.find_element(self.config['send_button_xpath'], timeout)
        is_disabled = button_element.get_attribute('disabled')
        return not is_disabled

    def check_audio_button_status(self, timeout: int = 10) -> bool:
        return self.browser.is_element_present(self.config['audio_button_xpath'], timeout=timeout)

    def check_llm_response_status(self, timeout: int = 10) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = self.browser.find_element(self.config['response_xpath'], timeout=1)
            if response:
                current_id = response.get_attribute('data-message-id')
                if current_id != self.latest_response_id:
                    self.latest_response_id = current_id
                    return True
            time.sleep(1)
        return False
    
    def upload_file(self, path: str) -> bool:
        try:
            path = os.path.abspath(os.path.expanduser(path))
            input_element = self.browser.find_element(self.config['input_xpath'])
            if not input_element:
                return False
                
            file_input = input_element.find_element(By.XPATH, self.config['file_xpath'])
            if not file_input:
                return False
                
            file_input.send_keys(path)
            return True
        except Exception as e:
            print(f"Error uploading file: {e}")
            return False
    
    def wait_for_upload_completion(self, timeout: int = 600) -> bool:
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.check_send_button_status():
                return True
            time.sleep(1)
        return False