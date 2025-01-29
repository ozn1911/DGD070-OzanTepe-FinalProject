import os
import subprocess
import re
import json
from openai import OpenAI


api_key = api_key = os.environ.get("OPENAI_API_KEY")
model = "gpt-4o-mini"
client = OpenAI(api_key=api_key)
#client.base_url= "http://localhost:1234/v1"

def sendAIMessage2(input, sysmessage):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": sysmessage}, {"role": "user", "content": input}],
        max_completion_tokens=2048,
        frequency_penalty=0,
        temperature= 0.6
    )
    assistant_response = response.choices[0].message.content
    return assistant_response


def read_tree():
    """
    Reads the file tree of the project and returns a list of all file paths.
    """
    file_paths = []
    for root, dirs, files in os.walk("."):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return " ".join(file_paths)

def read_treejs(js):
    return read_tree()

def read_doc(file_path, message):
    """
    Reads the content of a document and returns it as a string.
    """
    try:
        with open(file_path, 'r') as file:
            file_content = file.read()
            #print(file_content)
            ee = sendAIMessage2(file_content, "give summary of the input. unless asked for exact text, give summary and description of functions and their usages, the summary will be readen by another AI component, thus it doesnt have to be understandable by humans. the requesting AI's message: " + message)
            print(ee)
            return ee
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except Exception as e:
        return f"Error reading file: {e}"

def readfile(js):
    aa = ""
    aa = json.loads(js)
    return read_doc(aa.get("file_path"), aa.get("message_to_reader"))

def write_doc(file_path, content):
    """
    Writes the given content to a file. If the file exists, it asks for user confirmation before overwriting.
    """
    if os.path.exists(file_path):
        overwrite = ask_user(f"File {file_path} already exists. Do you want to overwrite it? (yes/no): ")
        if overwrite.lower() != "yes":
            return "Write operation canceled by the user."

    try:
        with open(file_path, 'w') as file:
            if(input("allow write in: " + file_path + "? ") == "n"):
                print("user rejected")
                return "user rejected"
            file.write(content)
        print(f"File written successfully to {file_path}")
        return f"File written successfully to {file_path}"
    except Exception as e:
        print(f"Error writing to file: {e}")
        return f"Error writing to file: {e}"
    
def writefile(js):
    aa = json.loads(js)
    return write_doc(aa.get("path"), aa.get("text"))

def ask_user(prompt):
    """
    Asks the user for input based on the given prompt and returns their response.
    """
    return input(prompt)
def getuserinput(js):
    aa = json.loads(js)
    return ask_user(aa.get("message"))

def run_command(command):
    """
    Executes a command in the terminal and returns the output or error.
    """
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error running command: {e}"

def process_ai_output(output):
    """
    Processes the AI output to determine and execute actions.
    """
    while "<" in output and ">" in output:
        start_index = output.find("<")
        end_index = output.find(">", start_index)
        if end_index == -1:
            break

        tag = output[start_index + 1:end_index]
        end_tag = f"</{tag}>"
        if end_tag not in output:
            break

        full_tagged_section = output[start_index:output.find(end_tag) + len(end_tag)]
        content = output[output.find(">", start_index) + 1:output.find(end_tag)].strip()

        if tag == "tree":
            print("tree used")
            #return read_tree()
            file_tree = read_tree()
            outge = "File tree:"
            for path in file_tree:
                outge += path
            return "    "+ outge

        elif tag == "read":
            print("read " + content)
            file_content = read_doc(content)
            return file_content
            print("File content:")
            print(file_content)

        elif tag == "write":
            print("write attempt")
            # Using regex to extract path and code content
            path_match = re.search(r"(?<=<write>)(.*?)(?=</write>)", output)
            code_match = re.search(r"(?<=<text>)(.*?)(?=</text>)", output)

            if path_match and code_match:
                file_path = path_match.group(0).strip()  # Extracted path
                text_content = code_match.group(0).strip()  # Extracted code
                result = write_doc(file_path, text_content)
                return result
            else:
                print("Error: Could not find valid path or code in the input.")
                return "Error: Invalid input format,maybe ask user for help"

        elif tag == "cmd":
            print(content)
            if(input("allow?") == "n"):
                return "user not allowed it"
            result = run_command(content)
            print("Command output:")
            print(result)
            return result

        elif tag == "output":
            print(content)
            return "user input: " + ask_user("you:")

        elif tag == "log":
            print(content)
            return "message printed"
        else:
            print("no command entered")
            return "no command entered"
        output = output.replace(full_tagged_section, "")

tools = [
    {
        "type": "function",
        "function": {
  "name": "get_file_tree",
  "description": "Retrieves the file tree structure that the you are allowed to access",
  "strict": True,
  "parameters": {
    "type": "object",
    "properties": {},
    "additionalProperties": False
  }
}},
         {
        "type": "function",
        "function": {
  "name": "readfile",
  "description": "Reads a document from the specified path and provides a summary.",
  "strict": True,
  "parameters": {
    "type": "object",
    "required": [
      "file_path",
      "message_to_reader"
    ],
    "properties": {
      "file_path": {
        "type": "string",
        "description": "The path to the document file to be summarized"
      },
        "message_to_reader": {
        "type": "string",
        "description": "The message to be sent to the reader AI component, you are suggested to request a summary of the document content, unless you believe you need exact text"
      }
    },
    "additionalProperties": False
  }
}},
         {
        "type": "function",
        "function": {
  "name": "writefile",
  "description": "Writes text to a specified file path.",
  "strict": True,
  "parameters": {
    "type": "object",
    "required": [
      "path",
      "text"
    ],
    "properties": {
      "path": {
        "type": "string",
        "description": "The file path where the text should be written."
      },
      "text": {
        "type": "string",
        "description": "The text content to be written to the file."
      }
    },
    "additionalProperties": False
  }
}},
         {
        "type": "function",
        "function": {
  "name": "get_user_input",
  "description": "Get user input command that will give output to user, taking a string to tell or ask the user, this is your primary means of communication with the user. you can use this to ask for your task or ask for help.",
  "strict": True,
  "parameters": {
    "type": "object",
    "required": [
      "message"
    ],
    "properties": {
      "message": {
        "type": "string",
        "description": "The message or question to present to the user"
      }
    },
    "additionalProperties": False
  }
}}
         ]
# Prompt for AI usage
ai_prompt = """
You are an AI designed to think and execute commands. Use the following functions to interact with the system and the user:

1. <tree></tree>: Reads the file tree.
2. <read>path</read>: Reads the content of a file at the given path.
3. <write>path</write><text>...</text>: Writes the given text to the file at the specified path. Use <text>...</text> to specify the content. Ask for user confirmation if the file already exists.
4. <cmd>command</cmd>: Runs the specified terminal command and returns the output.
5. <output>message</output>: Sends a message to the user, prints the message to the screen, and halts action until the user replies.
6. <log>message</log>: Sends a message to the user and continues executing actions.

Output your actions in the format <action>...</action>. For example:
<tree></tree>
<read>./file.txt</read>
<write>/my/project/new_script.cs</write><text>public class NewScript {}</text>
<cmd>ls -la</cmd>

after user grants you freedom(when user inputs "freedom granted") you will be able to use actions to do things, 
do not try to use commands until being granted freedom.

DO NOT TRY TO USE COMMANDS UNTIL USER SENDS MESSAGE "freedom granted"
DO NOT TRY TO USE MORE THAN ONE COMMAND AT ONCE.


after being granted freedom you wont be able to get user input until you use output command,
"""

"""
you can only use one command at a time.
You can use the following functions to interact with the system and the user to proceed with provided goal:

1. <tree></tree>: Reads the parent file tree, your code will be in a subfolder named "ELYTRA".
2. <read>path</read>: Reads the content of a file at the given path.
3. <write>path</write><text></text>: Writes the given text to the file at the specified path. Use <text>...</text> to specify the content. Ask for user confirmation if the file already exists. just output the code to user if you seem to fail
4. <cmd>command</cmd>: Runs the specified terminal command and returns the output.
5. <output>message</output>: Sends a message to the user, prints the message to the screen, and halts action until the user replies. you can ask user for help using this.
6. <log>message</log>: Sends a message to the user and continues executing actions.

Output your actions in the format <action>...</action>. For example:
<tree></tree> this command shows the parent folder of your folder.
<read>..\file.txt</read>
<write>..\new_script.cs</write><text>public class NewScript {}</text>
<cmd>command</cmd>
"""