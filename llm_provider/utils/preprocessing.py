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