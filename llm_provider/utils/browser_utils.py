import os
from ..config import CONFIG

def get_profile_paths(browser):
    home = os.path.expanduser("~")
    
    user_data_dir = os.path.join(home, "LLMProvider")
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
    profile_directory = "Default"

    if CONFIG[browser]['user_data_dir']:
        user_data_dir = CONFIG[browser]['user_data_dir']
    if CONFIG[browser]['profile_directory']:
        profile_directory = CONFIG[browser]['profile_directory']

    return user_data_dir, profile_directory