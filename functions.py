from pathlib import Path
from ollama import chat, ChatResponse

current_directory = Path.cwd()


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
    
    dir = Path(current_directory)
    try:
        arr = []
        for child in dir.iterdir(): 
            arr.append(child)
        return arr
    except IOError as e:
        print(f"An error has occured: {e}")

def read_file(file_path: str) -> str:
    '''
        Reads a given file.
        
        This functions takes the file_path as input and reads all the contents of the file.
        
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
    


available_functions = {
    'create_file': create_file,
    'list_files_in_directory': list_files_in_directory,
    'read_file': read_file
}

messages = [{
    "role": "user",
    "content": f"Create a new python file named snake.py at {current_directory} and also list all the files at the same location. Now, read the contents of the file snake.py"
}]


while True:
    response: ChatResponse = chat(
        model = 'qwen3:0.6B',
        messages = messages,
        tools = [create_file, list_files_in_directory, read_file],
        think = True
    )
    
    messages.append(response.message)
    print("Thiking: ", response.message.thinking)
    print("Content: ", response.message.content)
    
    if response.message.tool_calls:
        for tc in response.message.tool_calls:
            if tc.function.name in available_functions:
                print(f"Calling {tc.function.name} with arguments {tc.function.arguments}")
                result = available_functions[tc.function.name](**tc.function.arguments)
                print(f"Result: {result}")
                messages.append({"role": "tool", "tool_name": tc.function.name, "content": str(result)})
    else:
        break
        

