from bs4 import BeautifulSoup

def preprocess_prompt(message: str) -> list:
    newlines = [
        '\r\n',     # Carriage Return + Line Feed (Windows)
        '\n\r',     # Line Feed + Carriage Return (uncommon)
        '\v\n',     # Vertical Tab + Line Feed
        '\n\v',     # Line Feed + Vertical Tab
        '\f\n',     # Form Feed + Line Feed
        '\n\f',     # Line Feed + Form Feed
        '\v',       # Vertical Tab (\x0B)
        '\f',       # Form Feed (\x0C)
        '\n',       # Line Feed (\x0A) (Unix)
        '\r',       # Carriage Return (\x0D) (Mac OS before X)
        '\u2028',   # Line Separator
        '\u2029',   # Paragraph Separator
        '\u0085'    # Next Line (NEL)
    ]
    newlines.sort(key=len, reverse=True)
    
    result = message
    for nl in newlines:
        result = result.replace(nl, '\n')
    result_list = [ele for ele in result.split('\n')]

    return result_list

def clean_html_gpt(html_content):
    """
    Clean HTML by removing specific elements:
    1. Remove Copy buttons within pre.!overflow-visible
    2. Remove the first div grandson of pre.!overflow-visible
    
    Args:
        html_content (str): Input HTML string
    
    Returns:
        str: Cleaned HTML string
    """
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all pre elements with class="!overflow-visible"
    pre_elements = soup.find_all('pre', class_='!overflow-visible')
    
    for pre in pre_elements:
        # Remove Copy buttons
        copy_buttons = pre.find_all('button', attrs={'aria-label': 'Copy'})
        for button in copy_buttons:
            button.decompose()
            
        # Find and remove the first div grandson
        # Structure: pre > div > div (this is the one we want to remove)
        try:
            first_child_div = pre.find('div', recursive=False)
            if first_child_div:
                first_grandson_div = first_child_div.find('div', recursive=False)
                if first_grandson_div:
                    first_grandson_div.decompose()
        except AttributeError:
            continue
    
    # Return the cleaned HTML
    return str(soup)

def clean_html_claude(html_content):
    """
    Clean HTML by removing specific elements:
    1. Remove the first div grandson of pre (pre > div > div)
    2. Remove button elements under pre
    
    Args:
        html_content (str): Input HTML string
    
    Returns:
        str: Cleaned HTML string
    """
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all pre elements
    pre_elements = soup.find_all('pre')
    
    for pre in pre_elements:
        # Remove the first div grandson
        try:
            first_child_div = pre.find('div', recursive=False)
            if first_child_div:
                first_grandson_div = first_child_div.find('div', recursive=False)
                if first_grandson_div:
                    first_grandson_div.decompose()
        except AttributeError:
            continue
            
        # Remove button elements
        try:
            buttons = pre.find_all('button', recursive=True)
            for button in buttons:
                button.decompose()
        except AttributeError:
            continue
    
    # Return the cleaned HTML
    return str(soup)