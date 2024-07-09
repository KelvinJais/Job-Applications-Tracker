import sqlite3
from simplegmail import Gmail
from simplegmail.query import construct_query
from bs4 import BeautifulSoup
import re
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from main import clear_terminal, feature_extractor
from sklearn.model_selection import train_test_split

class mail:
    def __init__(self):
        self.connection=sqlite3.connect('mail_database.db')
        self.cursor=self.connection.cursor()
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Email(
        thread TEXT,
        sender TEXT,
        subject TEXT,
        date TEXT,
        text TEXT,
        category TEXT
        )
              """)
        print("Database initialized")
    def insertMail(self,thread,sender,subject,date,text,category):
        with self.connection:
            self.cursor.execute("INSERT INTO Email VALUES (:thread,:sender,:subject,:date,:text,:category)",{"thread":thread,"sender":sender,"subject":subject,"date":date,"text":text,"category":category})
        return None
    def get_all_mail(self):
        self.cursor.execute("SELECT * FROM Email")
        all_mail=self.cursor.fetchall()
        return all_mail
    def print_all_mail(self):
        self.cursor.execute("SELECT * FROM Email")
        all_mail=self.cursor.fetchall()
        for mail in all_mail:
            #print(f"Thread_ID: {mail[0]}")
            print(f"Sender: {mail[1]}")
            print(f"Subject: {mail[2]}")
            #print(f"Date: {mail[3]}")
            print(f"Text: {mail[4]}")
            print(f"Category: {mail[5]}")
            print("--------------------------------------------------------------------------------------------------------------------------------------")
        return None

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    text = soup.get_text().strip()
    clean_text = re.sub(r'\n+', '\n', text).strip()
    clean_text = clean_text.replace('\t', ' ')
    clean_text = clean_text.replace('\xa0', ' ')
    clean_text = ' '.join(clean_text.split())
    return clean_text 

def create_db(): #converting all the text files to features and save it to a pandas dataframe to be evaluated
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
    df = pd.DataFrame(columns=all_patterns)
    return df

def predictor(text,model):
    df=create_db()
    features=feature_extractor(text)
    new_row_df = pd.DataFrame([features])
    # Ensure the new row has all columns, with NaN for missing columns
    new_row_df = new_row_df.reindex(columns=df.columns)
    # Concatenate the new row to the existing DataFrame
    new_row_df.fillna(0, inplace=True)
    return model.predict(new_row_df)

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

def get_mail_sort_by_hand(mail_db):
    gmail = Gmail()
    query_params = {
        #"newer_than": (1, "day"),
        "labels":[["intern letters"]]
        }
    messages = gmail.get_messages(query=construct_query(query_params))
    totalMessages=len(messages)
    count=1
    model=random_forrest_model()
    for message in messages:
        print(f"Message {count}/{totalMessages}")
        count+=1
        print(extract_text_from_html(message.html))
        choice=input("Enter h for apply l for reject: ")
        if choice=='h':
            mail_db.insertMail(message.thread_id,message.sender,message.subject,message.date,extract_text_from_html(message.html),"Apply")
        elif choice=='l':
            mail_db.insertMail(message.thread_id,message.sender,message.subject,message.date,extract_text_from_html(message.html),"Reject")

    return None

if __name__ == "__main__":
    mail_db=mail()
    get_mail_sort_by_hand(mail_db)
    
    
