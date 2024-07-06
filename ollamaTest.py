from ollama import generate
import os
import re

def Ollamatest(text):
    response=generate('qwen2:1.5b',text+"Can you extract only the Company name and the Job title and format it into a JSON.")
    the_response=response['response']
    print(the_response)
    # Return the first match if found, otherwise return None

def Ollamatest_alone(text):
    response=generate('llama2',text)
    the_response=response['response']
    print(the_response)
    
def read_file(file_path):
    with open(file_path) as f:
        content = f.read()
    return content
def check_fn_all_files(directory,fn):
    all_files=os.listdir(directory)
    for file in all_files:
        print(file)
        content=read_file(os.path.join(directory,file))
        fn(content)
    # Iterate through all files in the folder
if __name__ == "__main__":
    check_fn_all_files("apply",Ollamatest)
