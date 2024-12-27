from typing import Dict, Any, List
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from .base import BaseDirectorProvider
from ..browsers.base import BaseBrowser

class SoraDirector(BaseDirectorProvider):
    def __init__(self, browser: BaseBrowser, config: Dict[str, Any]):
        super().__init__(browser, config)
        self.browser.driver.get(self.config['url'])

    def create_video(self, message: str) -> bool:
        try:
            # Send the prompt message to the input field
            send_status = self.browser.send_keys(
                self.config['input_xpath'], 
                message,
                clear_first=True
            )
            if not send_status:
                print('Failed to send message to input field')
                return False

            # Click the general button
            click_status = self.browser.click_element(self.config['create_button_xpath'])
            if not click_status:
                print('Failed to click general button')
                return False

            return True
            
        except Exception as e:
            print(f'Error creating video: {e}')
            return False

    def _click_general_button_by_text(self, possible_texts: list) -> bool:
        """Helper method to click general button using list of possible text values"""
        try:
            # Generate xpath with OR conditions for all possible text values
            text_conditions = ' or '.join([f'contains(., "{text}")' for text in possible_texts])
            # Combine with general button xpath
            base_xpath = self.config['general_button_xpath']
            full_xpath = f'{base_xpath}[.//span[{text_conditions}]]'
            
            # Click the button
            click_status = self.browser.click_element(full_xpath)
            print('before delay')
            self.browser.add_random_delay(5, 7)
            print('after delay')

            if not click_status:
                print(f'No button found matching any of texts: {possible_texts}')
                return False
                
            return True
            
        except Exception as e:
            print(f'Error clicking general button: {e}')
            return False

    def _select_option_from_popup(self, option_text: str) -> bool:
        """Helper method to select option from popup menu"""
        try:
            # Wait for popup menu
            popup = self.browser.find_element('/html/body/div')
            if not popup:
                print('Popup menu not found')
                return False

            # Find and click the option with matching text
            options = popup.find_elements(By.XPATH, './/div[@role="option"]')
            for option in options:
                if option_text in option.text:
                    option.click()
                    self.browser.add_random_delay(3, 5)
                    return True

            print(f'Option not found: {option_text}')
            return False

        except Exception as e:
            print(f'Error selecting option: {e}')
            return False

    def update_aspect_ratio(self, aspect_ratio: str) -> bool:
        """Update aspect ratio setting"""
        if aspect_ratio not in self.config['aspect_ratios']:
            print(f'Invalid aspect ratio: {aspect_ratio}')
            return False

        # Click the aspect ratio button using all possible values
        if not self._click_general_button_by_text(self.config['aspect_ratios']):
            return False

        # Select the desired option
        return self._select_option_from_popup(aspect_ratio)

    def update_resolution(self, resolution: str) -> bool:
        """Update resolution setting"""
        if resolution not in self.config['resolutions']:
            print(f'Invalid resolution: {resolution}')
            return False

        # Click the resolution button using all possible values
        if not self._click_general_button_by_text(self.config['resolutions']):
            return False

        # Select the desired option
        return self._select_option_from_popup(resolution)

    def update_duration(self, duration: int) -> bool:
        """Update duration setting"""
        duration_str = f'{duration}s'
        if duration_str not in self.config['durations']:
            print(f'Invalid duration: {duration_str}')
            return False

        # Click the duration button using all possible values
        if not self._click_general_button_by_text(self.config['durations']):
            return False

        # Select the desired option
        return self._select_option_from_popup(duration_str.replace('s', ' seconds'))

    def update_variation(self, variation: int) -> bool:
        """Update variation setting"""
        variation_str = f'{variation}v'
        if variation_str not in self.config['variations']:
            print(f'Invalid variation: {variation_str}')
            return False

        # Click the variation button using all possible values
        if not self._click_general_button_by_text(self.config['variations']):
            return False

        # Select the desired option
        if variation_str == '1v':
            variation_str = '1 video'
        else:
            variation_str = variation_str.replace('v', ' videos')

        return self._select_option_from_popup(variation_str)

    def download_videos(self) -> bool:
        """Download all generated videos"""
        try:
            # Find the video container div
            video_container = self.browser.find_element("//div[@data-index='1']")
            if not video_container:
                print("Video container not found")
                return False
                
            # Find all video buttons (3-dot menu buttons)
            menu_buttons = video_container.find_elements(By.XPATH, ".//button[@aria-haspopup='menu']")
            if not menu_buttons:
                print("No video menu buttons found")
                return False
                
            for menu_button in menu_buttons:
                try:
                    # Click the menu button
                    menu_button.click()
                    self.browser.add_random_delay(3, 6)
                    
                    # Find and click the Download menu item
                    download_menu = self.browser.find_element("//div[@role='menuitem'][.//div[text()='Download']]")
                    if not download_menu:
                        print("Download menu item not found")
                        continue
                        
                    # First hover over the download menu
                    self.browser.driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('mouseover', { bubbles: true }));", download_menu)
                    self.browser.add_random_delay(2, 3)
                    
                    # Then click it
                    download_menu.click()
                    self.browser.add_random_delay(2, 3)
                    
                    # Find and click the Video menu item
                    video_menu = self.browser.find_element("//div[@role='menuitem'][.//div[text()='Video']]")
                    if not video_menu:
                        print("Video menu item not found")
                        continue
                        
                    video_menu.click()
                    self.browser.add_random_delay(3, 5)
                    
                    # Find and click the final download button
                    download_button = self.browser.find_element("//button[.//text()='Download']")
                    if not download_button:
                        print("Final download button not found")
                        continue
                        
                    download_button.click()
                    self.browser.add_random_delay(30, 60)
                    
                except Exception as e:
                    print(f"Error downloading video: {e}")
                    continue
                    
            return True
            
        except Exception as e:
            print(f"Error in download_videos: {e}")
            return False