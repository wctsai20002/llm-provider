from selenium import webdriver
from selenium.webdriver.edge.options import Options
from ..utils.browser_utils import get_profile_paths
from ..config import CONFIG

class EdgeBrowser:
    def __init__(self):
        self.broswer_name = 'edge'
        self.edge_config = CONFIG[self.broswer_name]
        self.user_data_dir, self.profile_directory = get_profile_paths(self.broswer_name)

        options = Options()
        
        if self.edge_config.get('load_profile', True):
            options.add_argument(f'--user-data-dir={self.user_data_dir}')
            options.add_argument(f'--profile-directory={self.profile_directory}')
        
        self.driver = webdriver.Edge(options=options)

    def close(self):
        self.driver.quit()