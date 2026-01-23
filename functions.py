from pathlib import Path
from ollama import chat, ChatResponse

current_directory = Path.cwd()

def confirm_action(tool_name, arguments) -> bool:
    print(f"Request: {tool_name} with {arguments}")
    answer = input("Want to allow this action (yes/no)?").strip()
    return answer in {"y", "yes"}

def create_file(file_path: str, file_name: str) -> bool:
    '''
        Creates a new file.
        
        This function takes the file_path and file_name of a file as input and creates a new
        file names file_name at file_path
        
        Args: 
            file_path (str): The file path where the file is to be created
            file_name (str): The name of the file that is to be created
            
        Returns: 
            True if file is created successfully. 
            False if file is not created successfully.
        
        Raises:
            FileExistsError: If the file already exists at given location
            IOError: Something went wrong with pathlib library
    '''
    
    full_path = Path(f"{file_path}/{file_name}")
    try:
        full_path.touch()
        print(f"Empty file created at {full_path}")
        return True
    except FileExistsError:
        print(f"Error: The file already exists at {full_path}")
        return False
    except IOError as e:
        print(f"An error has occured: {e}")
        return False
    
def list_files_in_directory(directory: str) -> list:
    '''
        Lists all the file with its path in a given directory
        
        This function takes the directory as an input and returns list of all the files along with its path present in the directory
        
        Args:
            directory (str): The directory where there are some files present, perhaps None as well.
            
        Returns: 
            List containing all files along with its path present in the directory
        
        Raises:
            IOError: Something went wrong
    '''
    
    dir = Path(directory)
    try:
        arr = []
        for child in dir.iterdir(): 
            arr.append(child)
        return arr
    except IOError as e:
        print(f"An error has occured: {e}")
        return []

def read_file(file_path: str) -> str:
    '''
        Reads a given file.
        
        This function takes the file_path as input and reads all the contents of the file.
        
        Args:
            file_path (str): Path of the file that is to be read.
        
        Returns:
            File Contents as a string. 
        
        Raises:
            IOError if something went wrong.
    
    ''' 
    file = Path(file_path)
    try: 
        file_contents = file.read_text()
        return file_contents
    except IOError as e:
        print(f"An error occured: {e}")
        return ""

def write_in_file(file_path: str, content) -> bool:
    '''
        Writes in a give file.
        
        This function takes the file_path and content as the parameters and writes to the file.
        
        Args:
            file_path (str): Path of the file where write operation is to be performed.
            content : The information or piece of text that is to be written
        
        Returns:
            bool : Whether the write was successful or not.
        
        Raises:
            IOError if something went wrong.
    
    '''
    
    file = Path(file_path)
    try:
        file.write_text(content)
        return True
    except IOError as e:
        print(f"An error has occured: {e}")
        return False

def update_in_file(file_path: str, old: str, new: str) -> bool:
    '''
        Updates content in a given file by replacing all occurrences of old with new.

        Args:
            file_path (str): Path of the file where update operation is to be performed.
            old (str): The text to be replaced.
            new (str): The replacement text.

        Returns:
            bool : Whether the update was successful or not.

        Raises:
            IOError if something went wrong.

    '''

    file = Path(file_path)
    try:
        contents = file.read_text()
        updated = contents.replace(old, new)
        file.write_text(updated)
        return True
    except IOError as e:
        print(f"An error has occured: {e}")
        return False



available_functions = {
    'create_file': create_file,
    'list_files_in_directory': list_files_in_directory,
    'read_file': read_file,
    'write_in_file': write_in_file,
    'update_in_file': update_in_file
}

sensitive_tools = {
    "create_file",
    "write_in_file",
    "update_in_file"
}

# messages = [{
#     "role": "user",
#     # "content": f"Create a new python file named snake.py at {current_directory} and also list all the files at the same location. Write a function to add two numbers in to snake.py in python programming language. Now, read the contents of the file snake.py",
#     # "content": f"Browse and use this directory at location: {current_directory}. I want to build a portfolio website using html, css and javascript. Create all of the required files and also write the code for my portfolio website."
#     "content": f"Browse the current directory at location: {current_directory}. I want to add some colors to my portfolio website. so please change some code in styles.css and make it look more elegant and rich"
# }]

messages = [
    {
        "role":"system",
        "content": (
            "You are a helpful assistant. You always perform actions at the current directory located at: "
            f"{current_directory}. Prefer concise answers. "
            "When the user asks to create, update, or delete files, you MUST call the appropriate tool "
            "(create_file, write_in_file, update_in_file, read_file, list_files_in_directory) instead of "
            "only describing changes or printing code. If you propose edits, apply them using tools."
        )
    }
]

while True:
    user_input = input("How may I help you? ").strip()
    if user_input.lower() in {"bye"}:
        break
    
    messages.append(
        {
            "role": "user", 
            "content": user_input
        }
    )
    
    while True:
    
        response: ChatResponse = chat(
            model = 'gpt-oss:20b',
            messages = messages,
            tools = [create_file, list_files_in_directory, read_file, write_in_file, update_in_file],
            think = True
        )
        
        messages.append(response.message)
        print("Thinking: ", response.message.thinking)
        print("Content: ", response.message.content)
        
        if not response.message.tool_calls:
            break
        
        for tc in response.message.tool_calls:
            if tc.function.name in available_functions:
                if tc.function.name in sensitive_tools:
                    if not confirm_action(tc.function.name, tc.function.arguments):
                        print("Skipping ...")
                        messages.append(
                            {
                                "role": "tool",
                                "tool_name": tc.function.name,
                                "content" : "Skipped by user."
                            }
                        )
                        continue
                print(f"Calling {tc.function.name} with arguments {tc.function.arguments}")
                result = available_functions[tc.function.name](**tc.function.arguments)
                print(f"Result: {result}")
                messages.append({"role": "tool", "tool_name": tc.function.name, "content": str(result)})
        # else:
        #     break
        

