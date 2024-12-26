import json
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import Optional
from fake_useragent import UserAgent
from ..utils.browser_utils import get_profile_paths
from ..config import CONFIG
from .base import BaseBrowser

class ChromeBrowser(BaseBrowser):
    def __init__(self, proxy: Optional[str] = None):
        super().__init__()
        self.browser_name = 'chrome'
        self.chrome_config = CONFIG[self.browser_name]
        self.use_undetected = self.chrome_config.get('use_undetected', True)
        self.user_data_dir, self.profile_directory = get_profile_paths(self.browser_name)
        
        self.user_agents = UserAgent(browsers='Chrome', platforms='desktop', min_version=120.0)
        self.user_agent = self.user_agents.random
        
        if self.use_undetected:
            options = uc.ChromeOptions()
        else:
            options = ChromeOptions()

        # Basic anti-detection options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-browser-side-navigation')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        options.add_argument(f'user-agent={self.user_agent}')
        
        # Add proxy if provided
        if proxy:
            options.add_argument(f'--proxy-server={proxy}')
        
        # Random window size to avoid detection
        window_sizes = [(1366, 768), (1920, 1080), (1536, 864), (1440, 900)]
        random_window_size = random.choice(window_sizes)
        options.add_argument(f"--window-size={random_window_size[0]},{random_window_size[1]}")
        
        # Load profile if configured
        if self.chrome_config.get('load_profile', True):
            options.add_argument(f'--user-data-dir={self.user_data_dir}')
            options.add_argument(f'--profile-directory={self.profile_directory}')

            print(f'--user-data-dir={self.user_data_dir}')
            print(f'--profile-directory={self.profile_directory}')
        
        # Additional options to mask automation
        self._add_experimental_options(options)
        
        if self.use_undetected:
            self.driver = uc.Chrome(options=options)
        else:
            self.driver = webdriver.Chrome(options=options)
        
        # Execute anti-detection scripts
        self._inject_anti_detection_scripts()
    
    def _inject_anti_detection_scripts(self):
        """Inject JavaScript to mask Selenium/WebDriver presence."""
        anti_detection_js = """
            // Mask WebDriver presence
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // Mask automation-controlled presence
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            
            // Add fake web GL vendor and renderer
            try {
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                if (gl) {
                    const getParameter = gl.getParameter.bind(gl);
                    gl.getParameter = function(parameter) {
                        if (parameter === 37445) {
                            return 'Intel Inc.' // vendor
                        }
                        if (parameter === 37446) {
                            return 'Intel Iris OpenGL Engine' // renderer
                        }
                        return getParameter(parameter);
                    };
                }
            } catch (err) {
                console.log('WebGL modification failed:', err);
            }
            
            // Add chrome.runtime for more realism
            if (!window.chrome) {
                window.chrome = {
                    runtime: {}
                };
            }
            
            // Modify user agent plugins and mime types
            const mockPluginsData = [
                {name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer'},
                {name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai'},
                {name: 'Native Client', filename: 'internal-nacl-plugin'}
            ];
            
            // Override navigator properties
            try {
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8
                });
                
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8
                });
                
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32'
                });
            } catch (err) {
                console.log('Navigator property modification failed:', err);
            }
            
            // Additional canvas fingerprint protection
            try {
                const originalGetContext = HTMLCanvasElement.prototype.getContext;
                HTMLCanvasElement.prototype.getContext = function(type, attributes) {
                    const context = originalGetContext.call(this, type, attributes);
                    if (type === '2d') {
                        const originalGetImageData = context.getImageData;
                        context.getImageData = function() {
                            return originalGetImageData.apply(this, arguments);
                        };
                    }
                    return context;
                };
            } catch (err) {
                console.log('Canvas fingerprint protection failed:', err);
            }
            
            // Mask Selenium-specific properties
            try {
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            } catch (err) {
                console.log('Selenium property removal failed:', err);
            }
        """
        
        try:
            self.driver.execute_script(anti_detection_js)
            print("Successfully injected anti-detection scripts")
        except Exception as e:
            print(f"Warning: Could not inject anti-detection scripts: {str(e)}")

    def _add_experimental_options(self, options):
        """Add experimental options to mask automation."""
        prefs = {
            'profile.default_content_setting_values.notifications': 2,
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
            'profile.default_content_settings.popups': 0,
            'plugins.always_open_pdf_externally': True,
            'download.prompt_for_download': False,
            'download.default_directory': "/dev/null",
            'profile.managed_default_content_settings.javascript': 1,
            'profile.managed_default_content_settings.images': 1
        }
        
        # Add experimental options
        options.add_experimental_option('prefs', prefs)
        if not self.use_undetected:
            options.add_experimental_option('excludeSwitches', [
                'enable-automation',
                'enable-logging',
                'ignore-certificate-errors',
                'safebrowsing-disable-download-protection',
                'safebrowsing-disable-auto-update'
            ])
            options.add_experimental_option('useAutomationExtension', False)
        
        # Additional Chrome options for stealth
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-infobars')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-popup-blocking')
    
    def add_random_delay(self, min_delay: float = 0.5, max_delay: float = 3.0):
        delay = random.uniform(min_delay, max_delay)
        self.driver.implicitly_wait(delay)
    
    def move_mouse_randomly(self):
        """Simulate random mouse movements."""
        script = """
            var events = ['mouseover', 'mouseout', 'mousemove'];
            var elements = document.querySelectorAll('a, button, input, select');
            var element = elements[Math.floor(Math.random() * elements.length)];
            if (element) {
                var event = new MouseEvent(events[Math.floor(Math.random() * events.length)], {
                    'view': window,
                    'bubbles': true,
                    'cancelable': true,
                    'clientX': Math.floor(Math.random() * window.innerWidth),
                    'clientY': Math.floor(Math.random() * window.innerHeight)
                });
                element.dispatchEvent(event);
            }
        """
        try:
            self.driver.execute_script(script)
        except Exception as e:
            print(f"Warning: Could not simulate mouse movement: {str(e)}")
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Wait for element with random delay to simulate human behavior."""
        self.add_random_delay(0.5, 2.0)
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def close(self):
        """Clean up and close the browser."""
        # try:
        #     # Clear cookies and cache before closing
        #     self.driver.execute_script("window.localStorage.clear();")
        #     self.driver.execute_script("window.sessionStorage.clear();")
        #     self.driver.delete_all_cookies()
        # except Exception as e:
        #     print(f"Warning: Could not clear browser data: {str(e)}")
        # finally:
        self.driver.quit()