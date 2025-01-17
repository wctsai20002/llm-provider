from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from ..utils.browser_utils import get_profile_paths
from ..config import CONFIG

class FirefoxBrowser:
    def __init__(self, config):
        options = Options()
        profile_path = config.get('profile_path')
        
        if profile_path:
            options.add_argument(f'-profile {profile_path}')
        
        self.driver = webdriver.Firefox(options=options)

    def close(self):
        self.driver.quit()
    
    def __init__(self):
        self.broswer_name = 'firefox'
        self.firefox_config = CONFIG[self.broswer_name]
        self.user_data_dir, self.profile_directory = get_profile_paths(self.broswer_name)

        options = Options()
        
        if self.firefox_config.get('load_profile', True):
            options.set_preference('profile', self.user_data_dir)
        
        self.driver = webdriver.Edge(options=options)

    def close(self):
        self.driver.quit()