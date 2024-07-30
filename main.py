from simplegmail import Gmail

import os
from bs4 import BeautifulSoup
import re
import os
import spacy
from spacy.matcher import Matcher
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import lightgbm as lgb
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

def sgmail_getmail(directory):
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
        string=message.id+"\n"+message.sender+"\n"+message.subject+"\n"+extract_text_from_html(message.html)
        print(f"Message {count}/{totalMessages}")
        print(string)
        print()
        save_to_file(os.path.join("other", f"other{count}.txt"), string)
        count+=1
        
def sgmail_sort_by_hand(directory1, directory2):
    gmail = Gmail()
    os.makedirs(directory1, exist_ok=True)
    os.makedirs(directory2, exist_ok=True)
    query_params = {
        "newer_than": (20, "day"),
        }
    messages = gmail.get_messages(query=construct_query(query_params))
    totalMessages=len(messages)
    directory1_count=1
    directory2_count=1
    count=1
    for message in messages:
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
    matcher.add("receive application",[[{"lemma":"receive"},{"lower": "your"},{"lower": "application"}]],greedy="LONGEST")
    matcher.add("receive your submsission",[[{"lemma":"receive"},{"lower": "your"},{"lower": "submission"}]],greedy="LONGEST")
    matcher.add("review your application",[[{"lemma":"review"},{"lower": "your"},{"lower": "application"}]],greedy="LONGEST")
    matcher.add("review your submission",[[{"lemma":"review"},{"lower": "your"},{"lower": "submission"}]],greedy="LONGEST")
    matcher.add("review your resume",[[{"lemma":"review"},{"lower": "your"},{"lower": "resume"}]],greedy="LONGEST")
    matcher.add("receive your resume",[[{"lemma":"receive"},{"lower": "your"},{"lower": "resume"}]],greedy="LONGEST")
    matcher.add("application has been received",[[{"lower":"application"},{"lower": "has"},{"lower": "been"},{"LEMMA": "receive"}]],greedy="LONGEST")
    matcher.add("we will review",[[{"LOWER":"we"},{"LOWER": "will"},{"LOWER": "review"}]],greedy="LONGEST")
    matcher.add("currenly reviewing",[[{'LOWER': 'currently'},{'LOWER': 'reviewing'}]],greedy="LONGEST")
    matcher.add("thanks for aplying",[[{'LEMMA': 'thank'},{'LOWER': 'for'},{'LOWER': 'applying'}]],greedy="LONGEST")
    matcher.add("thank you very much for your application",[[{'LOWER': 'thank'},{'LOWER': 'you'},{'POS': 'ADV', 'OP': '*'},{'LOWER': 'for'},{'LOWER': 'your'},{'LOWER': 'application'}]],greedy="LONGEST")
    matcher.add("thank you very much for your interest in company name",[[{'LOWER': 'thank'},{'LOWER': 'you'},{'POS': 'ADV', 'OP': '*'},{'LOWER': 'for'},{'LOWER': 'your'},{'LOWER': 'interest'},{'POS': 'ADP', 'OP': '?'},{'POS': 'PROPN', 'OP': '*'}]],greedy="LONGEST")
    matcher.add("thank you for applying to company",[[{'LOWER': 'thank'},{'LOWER': 'you'},{'LOWER': 'for'},{'LOWER': 'applying'},{'IS_STOP': True},{'POS':"PROPN","OP":'*'}]],greedy="LONGEST")
    matcher.add("than you for submitting resume",[[{'LOWER': 'thank'},{'LOWER': 'you'},{'LOWER': 'for'},{'LOWER': 'submitting'},{'LOWER': 'your'},{'LOWER': 'resume'}]],greedy="LONGEST")
    matcher.add("will be reviewed", [[{"LOWER":"will"},{"LOWER": "be"},{"LEMMA": "review"}]],greedy="LONGEST")
    matcher.add("your application", [[{"LOWER":"your"},{"LOWER": "application"}]],greedy="LONGEST")
    matcher.add("submit", [[{"LEMMA":"submit"}]],greedy="LONGEST")
    matcher.add("apply", [[{"LEMMA":"apply"}]],greedy="LONGEST")
    matcher.add("appreciate", [[{"LEMMA":"appreciate"}]],greedy="LONGEST")
    matcher.add("interest", [[{"LEMMA":"interest"}]],greedy="LONGEST")
    matcher.add("review", [[{"LEMMA":"review"}]],greedy="LONGEST")
    matcher.add("talent team", [[{'POS':"NOUN"},{"LOWER":'team'}]],greedy="LONGEST")
    matcher.add("company team", [[{'POS':"PROPN","OP":"*"},{"LOWER":'team'}]],greedy="LONGEST")
    #reject patterns
    matcher.add("although",[[{"LOWER":"although"}]],greedy="LONGEST")
    matcher.add("however",[[{"LOWER":"however"}]],greedy="LONGEST")
    matcher.add("regret",[[{"LOWER":"regret"}]],greedy="LONGEST")
    matcher.add("unable",[[{"LOWER":"unable"}]],greedy="LONGEST")
    matcher.add("unfortunately",[[{"LOWER":"unfortunately"}]],greedy="LONGEST")
    matcher.add("unsuccessful",[[{"LOWER":"unsuccessful"}]],greedy="LONGEST")
    matcher.add("not been selected",[[{"LOWER":"not"},{"POS":"AUX","OP":"?"},{"LEMMA":"select"}]],greedy="LONGEST")
    matcher.add("at this time", [[{"LOWER":"at"},{"LOWER": "this"},{"LOWER": "time"}]],greedy="LONGEST")
    matcher.add("not moving forward", [[{"LOWER":"not"},{"POS": "AUX"},{"LEMMA": "move"},{"LOWER": "forward"}]],greedy="LONGEST")# what is this exactly?
    matcher.add("no longer under considerations", [[{'LOWER': 'no'},{'LOWER': 'longer'},{'LOWER': 'under'},{'LOWER': 'consideration'}]],greedy="LONGEST")
    matcher.add("has been filled", [[{'LOWER': 'has'},{'LOWER': 'been'},{'LOWER': 'filled'}]],greedy="LONGEST")
    matcher.add("other candidate", [[{'LOWER': 'other'},{'LEMMA': 'candidate'}]],greedy="LONGEST")
    matcher.add("different candidate", [[{'LOWER': 'different'},{'LEMMA': 'candidate'}]],greedy="LONGEST")
    matcher.add("other applicatns", [[{'LOWER': 'other'},{'LEMMA': 'applicant'}]],greedy="LONGEST")
    matcher.add("different applicant", [[{'LOWER': 'different'},{'LEMMA': 'applicant'}]],greedy="LONGEST")
    matcher.add("we have decided", [[{'LOWER': 'we'},{'LOWER': 'have'},{'LOWER': 'decided'}]],greedy="LONGEST")

    #other mail
    matcher.add("yet",[[{"LOWER":"yet"}]],greedy="LONGEST")
    matcher.add("yet to finish", [[{'LOWER': 'yet'},{'LOWER': 'to'},{'LOWER': 'finish'}]],greedy="LONGEST")
    matcher.add("yet to submit", [[{'LOWER': 'yet'},{'LOWER': 'to'},{'LOWER': 'submit'}]],greedy="LONGEST")
    matcher.add("continue applying", [[{'LOWER': 'continue'},{'LEMMA': 'apply'}]],greedy="LONGEST")
    
    doc = nlp(content)
    matches = matcher(doc)
    features={}
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]  # Get string representation
        span = doc[start:end]  # The matched span
        features[string_id] = features.setdefault(string_id, 0) + 1
        #print(match_id, string_id, start, end, span.text)
    return features

def create_feature_bank(): #converting all the text files to features and save it to a pandas dataframe to be evaluated
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

    def create_feature_bank_directory_old(directory,mail_type,df):
        all_files=os.listdir(directory)
        for file in all_files:
            print(file)
            with open(os.path.join(directory,file), 'r') as f:
                content = f.read()
            features=feature_extractor(content)
            features['mail type']=mail_type 
            df=dataframe_appending(features,df)
        return df

    df=create_feature_bank_directory_old("reject",0,df) # 0 for reject
    df=create_feature_bank_directory_old("apply",1,df) # 1 for apply   
    df=create_feature_bank_directory_old("other",2,df) # 2 for other mails   
    df.to_excel('features.xlsx', index=False)
        
def random_forrest_model():
    df = pd.read_excel('features.xlsx')
    df.fillna(0, inplace=True)
    # Assuming df is your pandas DataFrame
    X = df.drop(columns=['mail type'])
    Y = df['mail type']
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, random_state=22)
    # Create the Random Forest model
    rf_model = RandomForestClassifier(n_estimators=50, random_state=42)
    # Train the model
    rf_model.fit(X_train, Y_train)

    # Evaluate the model
    train_score = rf_model.score(X_train, Y_train)
    #test_score = rf_model.score(X_test, Y_test)

    print(f'random Forrest Training Accuracy: {train_score}')
    #print(f'random Forrest Test Accuracy: {test_score}')
    
def check_ent(text):
    nlp = spacy.load("en_core_web_sm")
    doc=nlp(text)
    if not doc.ents:
        print("no ents")
    for ent in doc.ents:
        if ent.label_=="ORG":
            print("\t ",ent.text)

def read_file(file_path):
    with open(file_path) as f:
        content = f.read()
    return content

def getting_name_matcher(content):
    nlp=spacy.load("en_core_web_sm")
    matcher=Matcher(nlp.vocab)
    matcher.add("position of",[[{"lemma":"position"},{"lower":"of"},{'POS':"PROPN","OP":"*"}]],greedy="LONGEST")
    matcher.add("position for",[[{"lemma":"position"},{"lower":"for"},{'POS':"PROPN","OP":"*"}]],greedy="LONGEST")
    matcher.add("position for the",[[{"lemma":"position"},{"lower":"for"},{"lower":"the"},{'POS':"PROPN","OP":"*"}]],greedy="LONGEST")
    doc = nlp(content)
    matches = matcher(doc)
    for match_id, start, end in matches:
        string_id = nlp.vocab.strings[match_id]  # Get string representation
        span = doc[start:end]  # The matched span
        ##print("\t",match_id, string_id, start, end, span.text)
        print("\t",span.text)
    
def check_fn_all_files(directory,fn):
    all_files=os.listdir(directory)
    for file in all_files:
        print(file)
        content=read_file(os.path.join(directory,file))
        fn(content)
if __name__=="__main__":
    create_feature_bank()
    random_forrest_model() 
    #check_fn_all_files("apply",check_ent)

