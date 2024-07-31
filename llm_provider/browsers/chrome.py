from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
import undetected_chromedriver as uc
from ..utils.browser_utils import get_profile_paths
from ..config import CONFIG

class ChromeBrowser:
    def __init__(self):
        self.broswer_name = 'chrome'
        self.chrome_config = CONFIG[self.broswer_name]
        self.use_undetected = self.chrome_config.get('use_undetected', True)
        self.user_data_dir, self.profile_directory = get_profile_paths(self.broswer_name)

        if self.use_undetected:
            options = uc.ChromeOptions()
        else:
            options = ChromeOptions()
        
        if self.chrome_config.get('load_profile', True):
            options.add_argument(f"--user-data-dir={self.user_data_dir}")
            options.add_argument(f"--profile-directory={self.profile_directory}")
        
        print('user_data_dir : ', self.user_data_dir)
        print('profile_directory : ', self.profile_directory)

        if self.use_undetected:
            self.driver = uc.Chrome(options=options)
        else:
            self.driver = webdriver.Chrome(options=options)

    def close(self):
        self.driver.quit()