from openai import OpenAI
import os
import re
import dump
import json

api_key = os.environ.get("OPENAI_API_KEY")
# Initialize the OpenAI client

model = "gpt-4o-mini"
client = OpenAI(api_key=api_key)
#client.base_url= "http://localhost:1234/v1"

with open(".\\sysprompt.txt", 'r') as f:
    data = f.read()
sys_prompt = data
#print(sys_prompt)
# Define a system prompt
system_prompt = {
    "role": "system",
    "content": sys_prompt
    }


# Initialize the list with the system prompt to maintain conversation history
chat_history = [system_prompt]
chat_history2 = [system_prompt]

def reset_chat_history2():
    chat_history2.clear()
    chat_history2.append(system_prompt)
    return chat_history2

def append_history(text):
    chat_history.append({
        "role": "user",
        "content": text
    })
    
def extract_result_tag_content(text):
    # Regular expression to find content between <result> and </result>
    pattern = r"<result>(.*?)</result>"
    matches = re.findall(pattern, text, re.DOTALL)  # Use re.DOTALL to handle multiline content
    for stre in matches:
        return stre
    return text

def chat_with_ai(user_input):
    # Add the user's message to the chat history
    append_history(user_input)

    # Prepare and send the request to the GPT-4 model

    response = client.chat.completions.create(
        model=model,
        messages=chat_history,
        max_completion_tokens=2048,
        frequency_penalty=0,
        temperature= 0.6,
        tools= dump.tools
    )
    response_message = response.choices[0].message
    toolcall = response_message.tool_calls
    if toolcall:
        #print(response.choices[0].message.content)
        #print(response_message)
        chat_history.append(response_message)
        function_list = {
            "get_file_tree": dump.read_treejs,
            "readfile": dump.readfile,
            "writefile": dump.writefile,
            "get_user_input": dump.getuserinput
        }
        for tool_call in toolcall:
            calling = function_list[tool_call.function.name]
            print(tool_call.function.name)
            args = tool_call.function.arguments
            #args = json.loads(args)
            func_response = calling(args)
            #print(func_response)
            chat_history.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": func_response
                }
            )
        response2 = client.chat.completions.create(
            model=model,
            messages=chat_history,
            max_completion_tokens=2048,
            frequency_penalty=0,
            temperature= 0.6
        )
        chat_history.append(
            {
                "role": "assistant",
                "content": response2.choices[0].message.content
            }
        )
        return response2.choices[0].message.content
    else:
        # Get the assistant's response
        assistant_response = response.choices[0].message.content

        # Add the assistant's response to the chat history
        chat_history.append({
            "role": "assistant",
            "content": assistant_response
        })

        return assistant_response

def aireply():

    # Prepare and send the request to the GPT-4 model

    response = client.chat.completions.create(
        model=model,
        messages=chat_history2,
        max_completion_tokens=2048,
        frequency_penalty=0,
        temperature= 0.6,
        tools= dump.tools
    )
    response_message = response.choices[0].message
    toolcall = response_message.tool_calls
    if toolcall:
        chat_history2.append(response_message)
        function_list = {
            "get_file_tree": dump.read_treejs,
            "readfile": dump.readfile,
            "writefile": dump.writefile,
            "get_user_input": dump.getuserinput
        }
        for tool_call in toolcall:
            calling = function_list[tool_call.function.name]
            print(tool_call.function.name)
            args = tool_call.function.arguments
            #args = json.loads(args)
            func_response = calling(args)
            #print(func_response)
            chat_history2.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": func_response
                }
            )
        return aireply()
        response2 = client.chat.completions.create(
            model=model,
            messages=chat_history2,
            max_completion_tokens=2048,
            frequency_penalty=0,
            temperature= 0.6
        )
        chat_history.append(
            {
                "role": "assistant",
                "content": response2.choices[0].message.content
            }
        )
        return response2.choices[0].message.content
    else:
        # Get the assistant's response
        assistant_response = response.choices[0].message.content

        # Add the assistant's response to the chat history
        chat_history.append({
            "role": "assistant",
            "content": assistant_response
        })

        return assistant_response

def sendAIMessage(input, sysmessage):
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": sysmessage}, {"role": "user", "content": input}],
        max_completion_tokens=2048,
        frequency_penalty=0,
        temperature= 0.6
    )
    assistant_response = response.choices[0].message.content
    return assistant_response

# Example usage
def summarize_chat_history2():
    # Prepare and send the request to the GPT-4 model
    chat_history2.append({
        "role": "user",
        "content": """Please think step by step and summarize last message and the chat history using provided logic:
        1- think on what should be remembered,
        2- think on what are ok to be summarized,
        3- think on what should be ignored,
        
        after doing that, note down key points and important details that should be remembered for future reference. and them encapsulated in <result> and </result> tags."""
    })
    response = client.chat.completions.create(
        model=model,
        messages=chat_history2,
        max_completion_tokens=2048,
        frequency_penalty=0,
        temperature= 0.6
    )
    print("Token Usage:")
    print(f"Prompt tokens: {response.usage.prompt_tokens}")
    print(f"Completion tokens: {response.usage.completion_tokens}")
    print(f"Total tokens: {response.usage.total_tokens}")
    reset_chat_history2()
    chat_history2.append({
        "role": "user",
        "content": "your previous summary: " + extract_result_tag_content(response.choices[0].message.content)
    })
    print(response.choices[0].message.content)

#response = "user input: " + input("you:")
while False:
    user_input = input("you:")
    response = chat_with_ai(user_input)
    print(response)

#response = dump.process_ai_output(response)
#responsecounter = 0
while(True):
    #response = dump.process_ai_output(chat_with_ai(response))
    response = aireply()
    #print(response)
    summarize_chat_history2()
    
