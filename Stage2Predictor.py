from Stage1Predictor import mail
from ollama import chat,generate
import spacy
from spacy.matcher import Matcher
import re
import pandas as pd

def getting_apply_reject_mail(mail_db):
    mails=mail_db.toPandas()
    mails=mails[(mails['category_code']==0 ) | ( mails['category_code']==1 )]
    return mails

def spacy_ner_test(mails):
    nlp = spacy.load("en_core_web_sm")# have the matcher code in a new function instead of creating one for every file
    for index, mail in mails.iterrows():#Updated
        doc=nlp(mail['text'])
        for ent in doc.ents:
            print(ent.text, ent.label_)
        print()
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
    for index, mail in mails[207:].iterrows():#Updated
        prompt=f"Sender:{mail['sender']}\nSubject:{mail['subject']}\nMail:{mail['text']} \nCan you extract only the Company name and the Job title and format it into a JSON like this 'company':company name, 'job':job title. If there is no job title then put job as "" "
        #response=generate('qwen2:1.5b',prompt)
        response=generate('llama3.1',prompt)
        print(f"Message {index}/{totalMessages}")
        count+=1
        response=response['response']
        pattern=r": *['\"](.*?)['\"]"
        matches = re.findall(pattern, response, re.DOTALL)
        print(matches)
        print()
        new_entry_df = pd.DataFrame([[prompt, matches]], columns=['text', 'output'])
        df = pd.concat([df, new_entry_df], ignore_index=True)
        #df.to_excel('stage2.xlsx',index=False)
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



def span_test():
    nlp = spacy.blank("en")
    training_data = [
      ("Tokyo Tower is 333m tall. My name is Kelvin.", [(0, 11, "BUILDING")]),
    ]
    for text, annotations in training_data:
        doc = nlp(text)
        print(doc.ents)
        ents = []
        for start, end, label in annotations:
            span = doc.char_span(start, end, label=label)
            ents.append(span)
        doc.ents = ents
        print(doc.ents)

if __name__ == "__main__":
    mail_db=mail()
    mails=getting_apply_reject_mail(mail_db)
    #creating_testingdata()
    spacy_ner_test(mails.head(10))



