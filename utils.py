import discord
from random import choice
import time
import feedparser
import requests
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

def mock_message(msg:str):
    """
    Spongebob mocks the given input by randomly varying the case of each letter.

    Parameters:
        msg (str): Message to mock.

    Returns:
        str: Mocked message.
    """
    returnMsg = ""

    for char in msg:
        returnMsg += choice((char.upper, char.lower))()

    return returnMsg

async def get_message(ctx, message:int):
    """
    Returns a previous message for a given channel and location (relative to context).

    Parameters:
        ctx (context): Passthrough for context from command.
        message (int): Location of message relative to sent command.

    Returns:
        Message: The message object of the selected message.
    """
    channel = ctx.message.channel
    history = await channel.history().flatten()

    returnMsg = history[message]
    return returnMsg

async def get_text(ctx, inputArg):
    """
    Returns the text given as the argument or the message from history with the author.

    Parameters:
        ctx (context): Passthrough for context from command.
        inputArg (string): Argument given from user.
    
    Returns:
        message, author (tuple): The message to be modified and author if applicable.
    """
    author = ""
    if str.isdigit(inputArg):
        inputArg = int(inputArg)
        if inputArg > 99:
            await ctx.send("Hey mate, I can only get history for the past 99 messages.")
            return
        else:
            msgRaw = await get_message(ctx, inputArg)
            author = f"**{msgRaw.author.display_name}:** "
            msg = msgRaw.content
    else:
        msg = inputArg

    return msg, author

def get_xkcd():
    """
    Returns the latest xkcd comic URL

    Returns:
        str: The URL to the latest xkcd comic
    """
    xkcd_feed =  "https://xkcd.com/rss.xml"
    d = feedparser.parse(xkcd_feed)

    latest = d["entries"][0]
    return latest["link"]

def jims_picker():
    """
    Picks a random Jim's group company

    Returns:
        str: A Jim's group company
    """
    companies = []
    with open("jims.txt", mode="r") as data:
        for company in data :
            companies.append(company)
    selection = choice(companies)
    return f"Jim's {selection}"

def get_today_event():
    """
    Returns today's event from the custom event list. Returns None if no event is on today

    Returns:
        List: List of information for event. [Date, Type (H,B), Name/User ID, None/Name]
    """
    events = []
    today_event = []
    with open("events.csv", mode="r") as data:
        for event in data :
            events.append(event.split(","))

    date = get_local_time()
    for event in events:
        date_str = f"{event[0]}-{date.year}"
        event_date = datetime.strptime(date_str, "%d-%M-%Y")
        if date.date() == event_date.date():
            event_data = [event[1], event[2]]
            today_event.append(event_data)
    
    return today_event
   
def get_fun_holiday():
    """
    Returns a fun holiday from www.timedate.com

    Returns:
        List: List of today's events formatted ["H", name]
    """
    # current_date = get_local_time()
    current_date = datetime(2019,2,20)
    today_event = []

    # Grabs the fun holiday table from the website
    html = requests.get("https://www.timeanddate.com/holidays/fun/").content
    soup = BeautifulSoup(html, 'html.parser')
    holiday_table = soup.find_all(class_='c0') + soup.find_all(class_='c1') + soup.find_all(class_='hl')

    # Finds today's events in the table and adds them to the list
    for row in holiday_table:
        date_string = row.find('th').get_text(strip=True)
        event_string = row.find('a').get_text(strip=True)
        holiday_date = datetime.strptime(date_string, '%d %b')
        if holiday_date.day == current_date.day and holiday_date.month == current_date.month:
            today_event.append(["H", event_string])
    
    return today_event

def get_local_time():
    """
    Returns a date time object for the Australia/Brisbane timezone

    Returns:
        datetime: Datetime object that is in the Brisbane timezone
    """
    utc_time = datetime.utcnow()
    tz = pytz.timezone('Australia/Brisbane')
    return pytz.utc.localize(utc_time, is_dst=None).astimezone(tz)

if __name__ == "__main__":
    get_fun_holiday()