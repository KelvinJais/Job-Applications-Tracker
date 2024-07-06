import sqlite3
from simplegmail import Gmail
from simplegmail.query import construct_query
import os
from bs4 import BeautifulSoup
import re

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
def database_init():
    conn = sqlite3.connect('mail_database.db')
    c= conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS Email(
        thread TEXT,
        sender TEXT,
        subject TEXT,
        date TEXT,
        text TEXT
        )
              """)
    return c,conn

def insert_mail(c,conn,thread,sender,subject,date,text):
    with conn:
        c.execute("INSERT INTO Email VALUES (:thread,:sender,:subject,:date,:text)",{"thread":thread,"sender":sender,"subject":subject,"date":date,"text":text})
    return None
def get_all_mail(c,conn):
    c.execute("SELECT * FROM Email")
    all_mail=c.fetchall()
    return all_mail

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    text = soup.get_text().strip()
    clean_text = re.sub(r'\n+', '\n', text).strip()
    clean_text = clean_text.replace('\t', ' ')
    clean_text = clean_text.replace('\xa0', ' ')
    clean_text = ' '.join(clean_text.split())
    return clean_text 

def get_mail(c,conn):
    gmail = Gmail()
    query_params = {
        #"newer_than": (1, "day"),
        "labels":[["september intern letters"]]
        }
    messages = gmail.get_messages(query=construct_query(query_params))
    totalMessages=len(messages)
    count=1
    for message in messages:
        print(f"Message {count}/{totalMessages}")
        count+=1
        #print(message.thread_id,message.sender,message.subject,message.date,message.html)
        insert_mail(c,conn,message.thread_id,message.sender,message.subject,message.date,extract_text_from_html(message.html))

import spacy
from spacy.matcher import Matcher
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
    matcher.add("appreciate", [[{"LEMMA":"application"}]],greedy="LONGEST")
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

def create_df(): #converting all the text files to features and save it to a pandas dataframe to be evaluated
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
    df = pd.DataFrame(columns=all_patterns)
    return df

def mail_sort(c,conn,model):
    all_mail=get_all_mail(c,conn)
    df=create_df()
    for mail in all_mail:
        text=mail[-1]
        print(text)
        features=feature_extractor(text)
        new_row_df = pd.DataFrame([features])
        # Ensure the new row has all columns, with NaN for missing columns
        new_row_df = new_row_df.reindex(columns=df.columns)
        new_row_df.fillna(0, inplace=True)
        print("*** the mail is of type*** ",model.predict(new_row_df))
        print()


def random_forrest_model():
    df = pd.read_excel('features.xlsx')
    df.fillna(0, inplace=True)
    # Assuming df is your pandas DataFrame
    X = df.drop(columns=['mail type'])
    Y = df['mail type']
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=22)
    # Create the Random Forest model
    rf_model = RandomForestClassifier(n_estimators=50, random_state=42)
    # Train the model
    rf_model.fit(X_train, Y_train)

    # Evaluate the model
    train_score = rf_model.score(X_train, Y_train)
    test_score = rf_model.score(X_test, Y_test)
    print(f'random Forrest Training Accuracy: {train_score}')
    print(f'random Forrest Test Accuracy: {test_score}')
    return rf_model

if __name__ == "__main__":
    c,conn=database_init()
    model=random_forrest_model()
    mail_sort(c,conn,model)
