import click
import simplegmail
import sqlite3

@click.command()
@click.option("--type",default="xlsx", help="File type to export")
def cli(type):
    """To display applications made in a tabular form"""
    click.echo(type)
    # Display new stats. reloaded since date. new applications and new reject applications

@click.command()
@click.option("--type", help="File type to export")
def export(type):
    """To export the data to an excel file"""

@click.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.option("--name", prompt="Your name", help="The person to greet.")
def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for _ in range(count):
        click.echo(f"Hello, {name}!")


