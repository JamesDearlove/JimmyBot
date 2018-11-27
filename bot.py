import discord
import utils
from discord.ext import commands

import os
from random import choice
import time
import math

prefix = "!"
activity = ""
bot = commands.Bot(command_prefix=prefix, description="G'day mate, it's JimmyD")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(activity))
    print(f"Logged in as {bot.user.name}")
    print(f"With the ID {bot.user.id}")
    
@bot.command()
async def hello(ctx):
    """Says g'day"""
    author = ctx.message.author.mention
    await ctx.send(f":wave: G'day, {author}")

@bot.command()
async def ping(ctx):
    """Pings you back"""
    author = ctx.message.author.mention
    await ctx.send(f":ping_pong: Pong! {author}")

@bot.command()
async def mock(ctx, *, inputArg = "1"):
    """Mocks selected message (if nothing given, most recent) or mocks text given."""
    author = ""
    if str.isdigit(inputArg):
        inputArg = int(inputArg)
        if inputArg > 99:
            await ctx.send("I can only get history for the past 99 messages.")
            return
        else:
            msgRaw = await utils.get_history(ctx, inputArg)
            author = f"**{msgRaw.author.display_name}:** "
            msg = msgRaw.content
    else:
        msg = inputArg

    mockedMsg = utils.mock_message(msg)
    await ctx.send(author + mockedMsg)

@bot.command()
async def history(ctx, location:int):
    """Gets the history for selected message (up to 99 messages in the past)"""
    if location > 99:
        await ctx.send("The limit of message history is 99")
    else:
        msg = await utils.get_history(ctx, location)
        await ctx.send(f"**{msg.author.display_name}:** {msg.content}")

@bot.command()
async def ree(ctx, a:int = 1):
    """Ree to the power of Euler's Constant"""
    if a > 7:
        await ctx.send("I cannot REE higher than e^7")
    else:
        returnMsg = "R"
        numberE = int(math.exp(a))
        
        count = 0
        while count < numberE:
            returnMsg += "E"
            count += 1

        await ctx.send(returnMsg)

@bot.command()
async def synth(ctx, *, inputArg):
    """Returns text with some a e s t h e t i c""" 
    output = " ".join(inputArg)
    await ctx.send(output)

@synth.error
async def synth_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Hey mate, I need text to meme")

@bot.command(hidden=True)
async def commit(ctx):
    build = os.environ.get("HEROKU_SLUG_COMMIT")

    await ctx.send(f"Current commit: ```{build}```")    

bot.run(os.environ.get("DISCORD_KEY"))