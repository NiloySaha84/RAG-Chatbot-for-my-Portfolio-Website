# Clipboard Manager

A simple Python-based clipboard manager that allows you to save, load, and list clipboard content using a JSON file for persistent storage. This program uses the `clipboard` library to interact with the system clipboard.

## Features

- Save clipboard content with a unique key.
- Load clipboard content by key and copy it back to the clipboard.
- List all saved clipboard content.

## Requirements

- Python 3.x
- `clipboard` module

## File Structure
	•	clipboard_manager.py: The main script.
	•	clipboard.json: The storage file for saved clipboard data (automatically created if it doesn’t exist).

## Error Handling
	•	If the clipboard.json file is missing, a new one is created automatically.
	•	Invalid keys or commands result in an appropriate error message.

## Notes
	•	Ensure the clipboard.json file is in the same directory as the script.
	•	Avoid manually editing the clipboard.json file unless necessary.

## License

This project is licensed under the MIT License. Feel free to use, modify, and distribute it.
