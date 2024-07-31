import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from llm_provider import CONFIG, update_config, get_provider_config
from llm_provider.browsers import ChromeBrowser
from llm_provider.providers import ChatGPTProvider

def main():
    user_config_path = os.path.join(os.path.dirname(__file__), 'user_config.yaml')
    update_config(user_config_path)
    
    try:
        browser = ChromeBrowser()
        
        chatgpt_config = get_provider_config('chatgpt')
        print("ChatGPT config:", chatgpt_config)
        
        chatgpt = ChatGPTProvider(browser, chatgpt_config)
        
        chatgpt.send_message("Hello, how are you?")
        
        response = chatgpt.get_response()
        print("ChatGPT says:", response)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if 'browser' in locals():
            browser.close()

if __name__ == "__main__":
    main()