# LLM Provider

A Python library for interacting with various LLM providers (ChatGPT, Claude) and AI video generation services (Sora) through browser automation. This library provides a unified interface for managing browser profiles and interacting with different AI services.

## Features
- **Free API**: Access ChatGPT and Claude through their web interfaces—ideal for users with budget constraints.
- **Higher TPM**: Web interfaces often have higher tokens-per-minute (TPM) limits compared to basic API tiers, which may allow for longer prompts.
- **Automation**: For services that don’t have an official API (e.g., Sora), this repository can offer a temporary Sora API to facilitate automation until an official API is published.

## Service Support
- [ChatGPT](https://chatgpt.com/)
- [Claude](https://claude.ai/)
- [Sora](https://sora.com/)

## Prerequisites

- **Chrome Browser**: Currently, only Chrome is fully supported and tested.
- **Python Version**: 
  - If you’re using Python 3.12 or higher, you may encounter issues with `undetected-chromedriver`.
  - To resolve this, please refer to [this GitHub issue](https://github.com/ultrafunkamsterdam/undetected-chromedriver/issues/1469) or using Python 3.11 or lower until the compatibility issue is resolved.
- **Accounts**: You must have valid accounts for the services you want to use (ChatGPT, Claude, or Sora).
- **Chrome Profile Setup**: 
  1. Create a new Chrome profile specifically for this automation
  2. Log in to your accounts (ChatGPT/Claude/Sora) manually in this profile
  3. Ensure you stay logged in by checking **Remember me** or similar options if available
  4. Disable the **Ask where to save each file before downloading** option in [Chrome](chrome://settings/downloads) so that Sora can download files automatically.
  5. The library will use this profile for automation

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/llm-provider.git
cd llm-provider
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

The library uses a YAML-based configuration system. Default settings are provided in `llm_provider/default_config.yaml`, which can be overridden by providing a custom configuration file.

### Browser Configuration

```yaml
chrome:
  use_undetected: true
  load_profile: true
  user_data_dir: "User Data"
  profile_directory: "Profile {number}"
```

### XPath Configuration
May need to change the xpath if frontend changed, but should careful of absolut paht or relative path.

## Usage

- For detailed usage examples, please refer to the [examples](./examples/) directory.

### ChatGPT Example

```python
from llm_provider import CONFIG, update_config, get_provider_config
from llm_provider.browsers import ChromeBrowser
from llm_provider.providers import ChatGPTProvider, ClaudeProvider

# Retrieve configuration for ChatGPT
gpt_config = get_provider_config('chatgpt')

# Initialize a Chrome browser instance
chrome_browser = ChromeBrowser()

# Create a ChatGPT provider using the browser and config
chatgpt = ChatGPTProvider(browser=chrome_browser, config=gpt_config)

# Select model
chatgpt.select_model('gpt-4o')

# Send a message
success = chatgpt.send_message_safely('Hello GPT! How are you today?')
print(f'Message sent successfully? {success}')

wait_status = chatgpt.wait_for_response_completion()
response_dict = chatgpt.get_response()
print('GPT Response (Text):', response_dict['chat']['text'])
print('GPT Response (Markdown):', response_dict['chat']['markdown'])

chatgpt.browser.close()
```

### Claude Example

```python
from llm_provider import CONFIG, update_config, get_provider_config
from llm_provider.browsers import ChromeBrowser
from llm_provider.providers import ChatGPTProvider, ClaudeProvider

# Retrieve configuration for Claude
claude_config = get_provider_config('claude')

# Initialize a Chrome browser instance
chrome_browser = ChromeBrowser()

# Create a Claude provider using the browser and config
claude = ClaudeProvider(browser=chrome_browser, config=claude_config)

# Select model
claude.select_model('sonnet')

# Send a message
success = claude.send_message('Hello Claude! How are you today?')
print(f'Message sent successfully? {success}')

wait_status = claude.wait_for_response_completion()
response_dict = claude.get_response()
print('Claude Response (Text):', response_dict['chat']['text'])
print('Claude Response (Markdown):', response_dict['chat']['markdown'])

claude.browser.close()
```

### Sora Example

```python
from llm_provider.browsers import ChromeBrowser
from llm_provider.directors import SoraDirector
from llm_provider.config import CONFIG

# Initialize browser and director
browser = ChromeBrowser()
director = SoraDirector(browser, CONFIG['sora'])

# Configure video settings
director.update_aspect_ratio('16:9')
director.update_resolution('480p')
director.update_duration(15)
director.update_variation(2)

# Create video
director.create_video('A cinematic shot of a serene lake at sunset')
director.browser.random_time_delay(30, 30)
director.download_videos()

browser.close()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Disclaimer

This library is for educational purposes only. Please ensure you comply with the terms of service of all AI services when using this library.