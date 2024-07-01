from simplegmail import Gmail
from simplegmail.query import construct_query
import os
from bs4 import BeautifulSoup
import re
import os
import spacy
from spacy.matcher import Matcher
import pandas as pd

# Function to extract text from an HTML file
def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    text = soup.get_text().strip()
    clean_text = re.sub(r'\n+', '\n', text).strip()
    clean_text = clean_text.replace('\t', ' ')
    clean_text = ' '.join(clean_text.split())
    return clean_text 

def save_to_file(filename, content):
    with open(filename, 'a') as file:
        file.write(content + '\n')

def clear_terminal():
    os.system('clear')

def get_mail(directory):
    gmail = Gmail()
    # Ensure the directories exist
    os.makedirs(directory, exist_ok=True)
    query_params = {
        "newer_than": (20, "day"),
        }
    
    messages = gmail.get_messages(query=construct_query(query_params))
    
    totalMessages=len(messages)
    count=1
    for message in messages[:200]:
        if message.html:
            string=message.id+"\n"+message.sender+"\n"+message.subject+"\n"+extract_text_from_html(message.html)
        print(f"Message {count}/{totalMessages}")
        print(string)
        print()
        save_to_file(os.path.join("other", f"other{count}.txt"), string)
        count+=1
        
def get_mail_sort_by_hand(directory1, directory2):
    gmail = Gmail()
    os.makedirs(directory1, exist_ok=True)
    os.makedirs(directory2, exist_ok=True)
    query_params = {
        "newer_than": (20, "day"),
        }
    messages = gmail.get_messages(query=construct_query(query_params))
    totalMessages=len(messages)
    directory1_count,directory2_count=1
    count=1
    for message in messages:
        if message.html:
            string=message.id+"\n"+message.sender+"\n"+message.subject+"\n"+extract_text_from_html(message.html)
        print("Message {count}/{totalMessages}")
        count+=1
        print(string)
        print()
        option=input("Enter h for apply and l for reject:")
        if option=="h":
            save_to_file(os.path.join(directory1, f"{directory1}{directory1_count}.txt"), string)
            directory1_count+=1 
        elif option=="l":
            save_to_file(os.path.join(directory2, f"{directory2}{directory2_count}.txt"), string)
            directory2_count+=1
        clear_terminal()     
        
def dataframe_appending(data,df):# Accepts a dictionary and a pandas dataframe. And appends the values in dictionary to dataframe and returns datafram
    # Convert the dictionary to a DataFrame
    new_row_df = pd.DataFrame([data])
    # Ensure the new row has all columns, with NaN for missing columns
    new_row_df = new_row_df.reindex(columns=df.columns)
    # Concatenate the new row to the existing DataFrame
    df = pd.concat([df, new_row_df], ignore_index=True)
    return df

def feature_extractor(content):# Accepts a content of text and outputs a dictionary
    nlp = spacy.load("en_core_web_sm")# have the matcher code in a new function instead of creating one for every file
    matcher = Matcher(nlp.vocab)
    #apply patterns
    matcher.add("receive application",[[{"lemma":"receive"},{"lower": "your"},{"lower": "application"}]])
    matcher.add("receive your submsission",[[{"lemma":"receive"},{"lower": "your"},{"lower": "submission"}]])
    matcher.add("review your application",[[{"lemma":"review"},{"lower": "your"},{"lower": "application"}]])
    matcher.add("review your submission",[[{"lemma":"review"},{"lower": "your"},{"lower": "submission"}]])
    matcher.add("review your resume",[[{"lemma":"review"},{"lower": "your"},{"lower": "resume"}]])
    matcher.add("receive your resume",[[{"lemma":"receive"},{"lower": "your"},{"lower": "resume"}]])
    matcher.add("application has been received",[[{"lower":"application"},{"lower": "has"},{"lower": "been"},{"LEMMA": "receive"}]])
    matcher.add("we will review",[[{"LOWER":"we"},{"LOWER": "will"},{"LOWER": "review"}]])
    matcher.add("currenly reviewing",[[{'LOWER': 'currently'},{'LOWER': 'reviewing'}]])
    matcher.add("thanks for aplying",[[{'LEMMA': 'thank'},{'LOWER': 'for'},{'LOWER': 'applying'}]])
    matcher.add("thank you very much for your application",[[{'LOWER': 'thank'},{'LOWER': 'you'},{'POS': 'ADV', 'OP': '*'},{'LOWER': 'for'},{'LOWER': 'your'},{'LOWER': 'application'}]])
    matcher.add("thank you very much for your interest in company name",[[{'LOWER': 'thank'},{'LOWER': 'you'},{'POS': 'ADV', 'OP': '*'},{'LOWER': 'for'},{'LOWER': 'your'},{'LOWER': 'interest'},{'POS': 'ADP', 'OP': '?'},{'POS': 'PROPN', 'OP': '*'}]])
    matcher.add("thank you for applying to company",[[{'LOWER': 'thank'},{'LOWER': 'you'},{'LOWER': 'for'},{'LOWER': 'applying'},{'IS_STOP': True},{'POS':"PROPN","OP":'*'}]])
    matcher.add("than you for submitting resume",[[{'LOWER': 'thank'},{'LOWER': 'you'},{'LOWER': 'for'},{'LOWER': 'submitting'},{'LOWER': 'your'},{'LOWER': 'resume'}]])
    matcher.add("will be reviewed", [[{"LOWER":"will"},{"LOWER": "be"},{"LEMMA": "review"}]])
    matcher.add("your application", [[{"LOWER":"your"},{"LOWER": "application"}]])
    matcher.add("submit", [[{"LEMMA":"submit"}]])
    matcher.add("apply", [[{"LEMMA":"apply"}]])
    matcher.add("appreciate", [[{"LEMMA":"appreciate"}]])
    matcher.add("interest", [[{"LEMMA":"interest"}]])
    matcher.add("review", [[{"LEMMA":"review"}]])
    matcher.add("appreciate", [[{"LEMMA":"application"}]])
    matcher.add("talent team", [[{'POS':"NOUN"},{"LOWER":'team'}]])
    matcher.add("company team", [[{'POS':"PROPN","OP":"*"},{"LOWER":'team'}]])
    #reject patterns
    matcher.add("although",[[{"LOWER":"although"}]])
    matcher.add("however",[[{"LOWER":"however"}]])
    matcher.add("regret",[[{"LOWER":"regret"}]])
    matcher.add("unable",[[{"LOWER":"unable"}]])
    matcher.add("unfortunately",[[{"LOWER":"unfortunately"}]])
    matcher.add("unsuccessful",[[{"LOWER":"unsuccessful"}]])
    matcher.add("not been selected",[[{"LOWER":"not"},{"POS":"AUX","OP":"?"},{"LEMMA":"select"}]])
    matcher.add("at this time", [[{"LOWER":"at"},{"LOWER": "this"},{"LOWER": "time"}]])
    matcher.add("not moving forward", [[{"LOWER":"not"},{"POS": "AUX"},{"LEMMA": "move"},{"LOWER": "forward"}]])# what is this exactly?
    matcher.add("no longer under considerations", [[{'LOWER': 'no'},{'LOWER': 'longer'},{'LOWER': 'under'},{'LOWER': 'consideration'}]])
    matcher.add("has been filled", [[{'LOWER': 'has'},{'LOWER': 'been'},{'LOWER': 'filled'}]])
    matcher.add("other candidate", [[{'LOWER': 'other'},{'LEMMA': 'candidate'}]])
    matcher.add("different candidate", [[{'LOWER': 'different'},{'LEMMA': 'candidate'}]])
    matcher.add("other applicatns", [[{'LOWER': 'other'},{'LEMMA': 'applicant'}]])
    matcher.add("different applicant", [[{'LOWER': 'different'},{'LEMMA': 'applicant'}]])
    matcher.add("we have decided", [[{'LOWER': 'we'},{'LOWER': 'have'},{'LOWER': 'decided'}]])

    #other mail
    matcher.add("yet",[[{"LOWER":"yet"}]])
    matcher.add("yet to finish", [[{'LOWER': 'yet'},{'LOWER': 'to'},{'LOWER': 'finish'}]])
    matcher.add("yet to submit", [[{'LOWER': 'yet'},{'LOWER': 'to'},{'LOWER': 'submit'}]])
    matcher.add("continue applying", [[{'LOWER': 'continue'},{'LEMMA': 'apply'}]])
    
    all_patterns=[# this variable contains all the patterns and will be used to create the column names for the pandas dataframe.
        "receive application",
        "receive your submsission",
        "review your application",
        "review your submission",
        "review your resume",
        "receive your resume",
        "application has been received",
        "we will review",
        "currenly reviewing",
        "thanks for aplying",
        "thank you very much for your application",
        "thank you very much for your interest in company name",
        "thank you for applying to company",
        "than you for submitting resume",
        "will be reviewed",
        "your application",
        "submit",
        "apply",
        "appreciate",
        "interest",
        "review",
        "appreciate",
        "talent team",
        "company team",
        "although",
        "however",
        "regret",
        "unable",
        "unfortunately",
        "unsuccessful",
        "not been selected",
        "at this time",
        "not moving forward",
        "no longer under considerations",
        "has been filled",
        "other candidate",
        "different candidate",
        "other applicatns",
        "different applicant",
        "we have decided",
        "yet",
        "yet to finish",
        "yet to submit",
        "continue applying",
        ]
    df = pd.DataFrame(columns=all_patterns+['mail type'])
    doc = nlp(content)
    matches = matcher(doc)
    features={}
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]  # Get string representation
        span = doc[start:end]  # The matched span
        features[string_id] = features.setdefault(string_id, 0) + 1
        #print(match_id, string_id, start, end, span.text)
    return features
if __name__=="__main__":
    print(feature_extractor("Thank you for applying to Kelvin Corp."))