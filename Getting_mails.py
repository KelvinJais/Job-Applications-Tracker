from simplegmail import Gmail
from simplegmail.query import construct_query
import os
from bs4 import BeautifulSoup

gmail = Gmail()

# Ensure the directories exist
os.makedirs("apply", exist_ok=True)
os.makedirs("reject", exist_ok=True)

# Function to extract text from an HTML file
def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    text = soup.get_text()
    return text

def save_to_file(filename, content):
    with open(filename, 'a') as file:
        file.write(content + '\n')

def clear_terminal():
    os.system('clear')


query_params = {
    "labels":[["intern letters"]]
}
messages = gmail.get_messages(query=construct_query(query_params))

apply=1
reject=1
for message in messages[0:5]:
    
    string=message.sender+"\n"+message.subject+"\n"+extract_text_from_html(message.html)
    print(string)
    option=input("Enter h for apply and l for reject:")
    if option=="h":
        save_to_file(os.path.join("apply", f"apply{apply}.txt"), string)
        apply+=1 
    elif option=="l":
        save_to_file(os.path.join("reject", f"reject{reject}.txt"), string)
        reject+=1
    clear_terminal()     