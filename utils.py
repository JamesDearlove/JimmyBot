import discord
from random import choice
import time

def is_number(input):
    """
    Checks if input is a number.

    Parameters:
        input (str|int): Input to check

    Returns:
        bool: If the input was a number or not
    """
    try:
        int(input)
    except:
        return False
    return True

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

async def get_history(ctx, message:int):
    """
    Returns the history for a given channel and location (relative to context).

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