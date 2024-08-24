from Stage1Predictor import mail
import language_tool_python
import random
from ollama import chat,generate
import spacy
from spacy.matcher import Matcher
import re
import pandas as pd
from spacy import displacy
import json
from spacy.tokens import DocBin

def getting_apply_reject_mail(mail_db):
    mails=mail_db.toPandas()
    mails=mails[(mails['category_code']==0 ) | ( mails['category_code']==1 )]
    return mails

def spacy_ner_test(mails):
    nlp = spacy.load("en_core_web_sm")# have the matcher code in a new function instead of creating one for every file
    for index, mail in mails[:2].iterrows():#Updated
        doc=nlp(mail['text'])

def ollama_test(mails):
    totalMessages=len(mails)
    count=1
    for index, mail in mails.iterrows():#Updated
        prompt=f"""Sender:{mail['sender']}\nSubject:{mail['subject']}\nMail:{mail['text']}
        Can you extract all instaces of the Company name and the Job title and format it into a JSON like this 'company':[company names,], 'job':job title. If there is no job title then put job as "" """
        response=generate('qwen2:1.5b',prompt)
        response=response['response']
        print(prompt)
        print(response)
        #response=generate('llama3.1',prompt)
        print(f"Message {index}/{totalMessages}")

def ollama_extractor(mails):
    df=pd.read_excel('stage2.xlsx')
    totalMessages=len(mails)
    count=1 
    for index, mail in mails[270:].iterrows():#Updated
        prompt=f"""Sender:{mail['sender']}\nSubject:{mail['subject']}\nMail:{mail['text']}
        Can you extract only the Company name and the Job title and format it into a JSON like this 'company':company name, 'job':job title. """
        print(prompt)
        response=generate('qwen2:1.5b',prompt)
        #response=generate('llama3.1',prompt)
        print(f"Message {index}/{totalMessages}")
        count+=1
        response=response['response']
        pattern=r": *['\"](.*?)['\"]"
        matches = re.findall(pattern, response, re.DOTALL)
        print(matches)
        print()
        new_entry_df = pd.DataFrame([[prompt, matches[0],matches[1]]], columns=['text', 'company','job'])
        df = pd.concat([df, new_entry_df], ignore_index=True)
        df.to_excel('stage2.xlsx',index=False)
    return df

def creating_testingdata():
    df=pd.read_excel('stage2.xlsx')
    nlp = spacy.load("en_core_web_sm")# have the matcher code in a new function instead of creating one for every file
    matcher = Matcher(nlp.vocab)
    for index,mail in df.iterrows():
        pattern=r"'(.*?)'"
        matches = re.findall(pattern, mail['output'] , re.DOTALL)
        if matches:
            word=matches[0]
            print(word)
            matcher.add("company",[[{"lower":word.lower()}]])
            doc = nlp(mail['text'])
            matches = matcher(doc)
            for match_id, start, end in matches:
                string_id = nlp.vocab.strings[match_id]  # Get string representation
                span = doc[start:end]  # The matched span
                print(match_id, string_id, start, end, span.text)
            print()


def creating_testingdata_2():
    df=pd.read_excel('stage2_alt.xlsx')
    for index,mail in df.iterrows():
        word=mail['company']
        #get multiple words
        pattern = re.compile(rf"\b{re.escape(word)}\b")
        matches = pattern.finditer(mail['text'])
        for match in matches:
            print(mail['text'][match.start():match.end()])
            print("Span (start, end):", match.span())
        print()


def replace_names(text):
    first_names = [
        "James", "John", "Robert", "Michael", "William",
        "David", "Richard", "Joseph", "Thomas", "Charles",
        "Christopher", "Daniel", "Matthew", "Anthony", "Donald",
        "Mark", "Paul", "Steven", "Andrew", "Kenneth"
    ]

    last_names = [
        "Smith", "Johnson", "Williams", "Jones", "Brown",
        "Davis", "Miller", "Wilson", "Moore", "Taylor",
        "Anderson", "Thomas", "Jackson", "White", "Harris",
        "Martin", "Thompson", "Garcia", "Martinez", "Robinson"
    ]

    first=random.choice(first_names)
    last=random.choice(last_names)
    text = text.replace("Kelvin", first)
    text = text.replace("Konnoth", last)
    email = f"{first.lower()}.{last.lower()}@gmail.com"
    text=text.replace("kelvin4jaison@gmail.com",email)
    return text

def change_names():
    df=pd.read_excel('stage2.xlsx')
    nf = pd.DataFrame(columns=['text', 'company','job'])
    first_names = [
        "James", "John", "Robert", "Michael", "William",
        "David", "Richard", "Joseph", "Thomas", "Charles",
        "Christopher", "Daniel", "Matthew", "Anthony", "Donald",
        "Mark", "Paul", "Steven", "Andrew", "Kenneth"
    ]

    last_names = [
        "Smith", "Johnson", "Williams", "Jones", "Brown",
        "Davis", "Miller", "Wilson", "Moore", "Taylor",
        "Anderson", "Thomas", "Jackson", "White", "Harris",
        "Martin", "Thompson", "Garcia", "Martinez", "Robinson"
    ]
    for index, mail in df.iterrows():#Updated
        first=random.choice(first_names)
        last=random.choice(last_names)
        text=mail['text']
        text = text.replace("Kelvin", first)
        text = text.replace("Konnoth", last)
        email = f"{first.lower()}.{last.lower()}@gmail.com"
        text=text.replace("kelvin4jaison@gmail.com",email)
        new_entry_df = pd.DataFrame([[text, mail['company'],mail['job']]], columns=['text', 'company','job'])
        nf = pd.concat([nf, new_entry_df], ignore_index=True)
    nf.to_excel('stage2_alt.xlsx',index=False)
        

def create_text_file(mails):
    file = open("train.txt", "w")
    totalMessages=len(mails)
    count=1 
    for index,mail in mails.iterrows():
        prompt=f"Sender:{mail['sender']}. Subject:{mail['subject']}. Mail:{mail['text']}"
        text=replace_names(prompt)
        print(f"Message {count}/{totalMessages}")
        count+=1
        file.write(text)
        file.write("end-of-line")
    file.close()

def open_json():
    with open('annotations86.json', 'r') as file:
        data = json.load(file)
    ideal_format=[]
    for row in data["annotations"]:
        text=row[0]
        entities=[tuple(i) for i in row[1]['entities']]
        ideal_format.append((text,entities))
    return ideal_format

def training(training_data):
    nlp = spacy.load("en_core_web_sm")
    db = DocBin()
    nulls_bro=0
    for text, annotations in training_data:
        print(text)
        doc = nlp(text)
        ents = []
        for start, end, label in annotations:
            print(start,end)
            span = doc.char_span(start, end, label=label)
            if span != None:
                ents.append(span)
            else:
                nulls_bro+=1
        print(ents)
        doc.ents = ents
        db.add(doc)
    print(f" The nulls you got {nulls_bro}")
    db.to_disk("./train.spacy")

def prediction_test():
    nlp=spacy.load("output/model-last")
    text=""" Subject: Application Status: Software Intern Position

Dear Kelvin,

Thank you for your interest in the Software Intern position at Adobe and for taking the time to meet with our team. We appreciate the effort you put into your application and the enthusiasm you have shown for this opportunity.

After careful consideration, we regret to inform you that we have chosen to move forward with another candidate whose experience and skills more closely align with the current needs of our team. This decision was not easy, as we were impressed with your qualifications and potential.

We want to acknowledge your hard work and encourage you to apply for future opportunities at Adobe that align with your interests and expertise. We are confident that with your talent and dedication, you will find success in your career pursuits.

Thank you again for your interest in Adobe, and we wish you all the best in your future endeavors.

Sincerely,
Kelvin
Adobe Systems Incorporated"""
    doc=nlp(text)
    for ent in doc.ents:
        print(ent.text,ent.label_)

if __name__ == "__main__":
    #mail_db=mail()
    #mails=getting_apply_reject_mail(mail_db)
    prediction_test()

    #training_data=open_json()
    #training(training_data)


