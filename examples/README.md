# LLM Provider Usage Guide

## ChatGPT

### Important Notes

1. **Model Configuration**:
   - When new models are released, update the xpath in `default_config.yaml`.
   - Example config structure:
   ```yaml
   models:
     "model-name": "//div[@data-testid='model-switcher-model-name' and @role='menuitem']"
   ```

2. **Message Sending**:
   - Safe mode `send_message_safely()`: More reliable but slower. It processes the prompt line by line, as ChatGPT interprets `\n` as `Enter`.

3. **Response Handling**:
   - ChatGPT only supports one canvas per response.
   - Response structure:
   ```python
   {
       'chat': {
           'html': 'Raw HTML content',
           'text': 'Plain text content',
           'markdown': 'Markdown formatted content'
       },
       'canvas': {
           'html': 'Canvas HTML content if exists',
           'text': 'Canvas text content if exists',
           'markdown': 'Canvas markdown content if exists'
       }
   }
   ```

## Claude

### Important Notes

1. **Model Configuration**:
   - Update both name and description in config for new models. Need both of name and description to locate the button.
   - Example config structure:
   ```yaml
   models:
     "sonnet":
       name: "Claude 3.5 Sonnet"
       description: "Most intelligent model"
   ```

2. **Response Handling**:
   - Multiple artifacts per response supported.
   - Current limitations:
     - Code artifacts: ✅ Fully supported
     - Text artifacts: ✅ Fully supported
     - Other artifacts (iframe-based): ❌ Not supported
   - Response structure:
   ```python
   {
       'chat': {
           'html': 'Raw HTML content',
           'text': 'Plain text content',
           'markdown': 'Markdown formatted content'
       },
       'artifact': [
           {
               'html': 'Artifact HTML content',
               'text': 'Artifact text content',
               'markdown': 'Artifact markdown content'
           },
           # ... more artifacts if exist
       ]
   }
   ```

## Sora

### Important Notes

1. **Video Generation Process**:
   - Multiple waiting periods are required due to unpredictable generation times.
   - Model improvement system:
     - Sometimes Sora requests user feedback.
     - Code automatically selects "Keep none".
     - Returns `False` to indicate need for regeneration.

2. **Download Handling**:
   - Disable Chrome's **Ask where to save each file before downloading** option.

3. **Get dowload video**:
   - The function below sorts all `.mp4` files in the default Downloads folder, then copies the newest one to a specified directory:
        ```python
        def copy_latest_mp4(destination_path, new_filename=None):
        """
        Copy the most recent MP4 file from Downloads to a new location.
        
        Args:
            destination_path (str): Target directory
            new_filename (str, optional): New name without extension
        
        Returns:
            str/bool: New file path if successful, False if failed
        """
        try:
            downloads_path = os.path.expanduser('~\\Downloads')
            mp4_files = glob.glob(os.path.join(downloads_path, '*.mp4'))
            
            if not mp4_files:
                print('No MP4 files found in Downloads')
                return False
                
            latest_file = max(mp4_files, key=os.path.getmtime)
            os.makedirs(destination_path, exist_ok=True)
            
            new_path = os.path.join(
                destination_path, 
                f'{new_filename}.mp4' if new_filename else os.path.basename(latest_file)
            )
            
            shutil.copy2(latest_file, new_path)
            print(f'Successfully copied {latest_file} to {new_path}')
            return new_path
            
        except Exception as e:
            print(f'Error copying file: {str(e)}')
            return False
        ```