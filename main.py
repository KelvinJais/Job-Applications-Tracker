import click
import simplegmail
import sqlite3
import pandas as pd
from datetime import datetime,timedelta
class mail:
    def __init__(self):
        self.connection=sqlite3.connect(':memory:')
        self.cursor=self.connection.cursor()
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Email(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread TEXT,
        sender TEXT,
        subject TEXT,
        date TEXT,
        text TEXT,
        category TEXT
        )
              """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS PrimTable(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        job TEXT,
        category TEXT,
        date TEXT
        )
              """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Dates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_date TEXT,
        current_date TEXT
        )
              """)

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS Stats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        current_applied INT,
        current_reject INT,
        total_applied INT,
        total_reject INT
        )
              """)
        self.inputing_test_data()

    def inputing_test_data(self):
        with self.connection:
            #self.cursor.execute("INSERT INTO Dates VALUES (:start_date,:current_date)",("08/11/2023","08/17/2023"))
            self.cursor.execute("INSERT INTO Dates (start_date,current_date) VALUES (\"08/11/2023\",\"08/17/2023\")")

        with self.connection:
            self.cursor.execute("INSERT INTO Stats (current_applied,current_reject,total_applied,total_reject) VALUES (5,1,100,20)")
            self.cursor.execute("INSERT INTO Stats (current_applied,current_reject,total_applied,total_reject) VALUES (6,2,200,30)")

    def insertMail(self,thread,sender,subject,date,text,category):
        with self.connection:
            self.cursor.execute("INSERT INTO Email VALUES (:thread,:sender,:subject,:date,:text,:category)",{"thread":thread,"sender":sender,"subject":subject,"date":date,"text":text,"category":category})
        return None

    def get_latest_dates(self):
        self.cursor.execute("SELECT * FROM Dates ORDER BY id DESC LIMIT 1")
        stats=self.cursor.fetchone()
        _,start_date,current_date=stats
        return start_date,current_date

    def set_dates(self,start_date,current_date):
        with self.connection:
            self.cursor.execute('INSERT INTO dates (start_date, current_date) VALUES (?, ?)',(start_date, current_date))

    def get_all_mail(self):
        self.cursor.execute("SELECT * FROM Email")
        all_mail=self.cursor.fetchall()
        return all_mail

    def get_latest_stats(self):
        self.cursor.execute("SELECT * FROM Stats ORDER BY id DESC LIMIT 1")
        stats=self.cursor.fetchone()
        _,current_applied,current_reject,total_applied,total_reject=stats
        return current_applied,current_reject,total_applied,total_reject


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

    def toPandas(self):
        query = "SELECT * FROM Email"
        df = pd.read_sql_query(query, self.connection)
        self.connection.close() 
        df['category_code'] = df['category'].map({'Apply': 0, 'Reject': 1, 'Other': 2})
        return df

@click.group()
@click.pass_context
def cli(ctx):
    maildb=mail()
    ctx.ensure_object(dict)
    ctx.obj['MAIL'] = maildb
    pass

def reload():
    print("reloading")

@cli.command()
@click.option('-r','--reload',is_flag=True,help="To reload and update the stats")
@click.option('-p','--print',is_flag=True,help="add this to print the newly added entries")
@click.pass_context
def stats(ctx,reload,print):
    """Describe the data"""
    maildb=ctx.obj['MAIL']
    if reload:
        click.echo("wasap")

    applied,rejects,total_applied,total_rejects=maildb.get_latest_stats()
    click.echo(f"""
    Current Active Applications(Applied-Rejects):{total_applied-total_rejects}

    Applied since last load:{applied}
    Rejects since last load:{rejects}

    Total Applied:{total_applied}
    Total Rejects:{total_rejects}
    """)
    if print:
        click.echo("print is active")

@cli.command()
@click.pass_context
def view(ctx):
    """To view the data"""
    maildb=ctx.obj['MAIL']
    df=maildb.toPandas()
    click.echo(df.head())

@cli.command()
@click.option("--type",default="xlsx", help="File type to export")
@click.pass_context
def export(ctx,type):
    """To export the data to an excel file"""


@cli.command()
@click.pass_context
def login(ctx,type):
    """To export the data to an excel file"""
    ##Check for whether the file exists. and do the login part i guess


@cli.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.option("--name", prompt="Your name", help="The person to greet.")
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for _ in range(count):
        click.echo(f"Hello, {name}!")

"""
I have to imagine how a user would start this working with this software. The first important thing is to handle the login.
main login

This will give you since last time how many applied and how many rejects and stuff
main stats -r

"""
