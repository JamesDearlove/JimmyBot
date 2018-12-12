import discord
import utils
import asyncio
import os
import math
from datetime import datetime, time
from random import choice

from discord.ext import commands
from discord.utils import get

currentCommit = os.environ.get("HEROKU_SLUG_COMMIT")

prefix = "!"
activity = currentCommit[:7]
main_channel = int(os.environ.get("DEFAULT_CHANNEL_ID"))

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bg_task = self.loop.create_task(self.bot_schedule())

    async def on_ready(self):
        await bot.change_presence(activity=discord.Game(activity))
        print(f"Logged in as {bot.user.name}")
        print(f"With the ID {bot.user.id}")

    # Runs tasks at set times
    async def bot_schedule(self):
        await self.wait_until_ready() 
        channel = self.get_channel(main_channel)
        while not self.is_closed():
            minutesToSleep = 60 - datetime.utcnow().minute % 60
            await asyncio.sleep(minutesToSleep * 60)
            check_time = datetime.utcnow().time()

            # Good morning messasge (9am)
            if check_time >= time(23,0) and check_time <= time(23,5) :
                await channel.send("Good Morning!")
            
bot = MyBot(command_prefix=prefix, description="G'day mate, it's JimmyD")

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
    message = await utils.get_text(ctx, inputArg)

    mockedMsg = utils.mock_message(message[0])
    await ctx.send(message[1] + mockedMsg)

@bot.command()
async def ree(ctx, a:int = 1):
    """Ree to the power of Euler's Constant"""
    if a > 7:
        await ctx.send("Hey mate, I cannot REE higher than e^7")
    else:
        returnMsg = "R"
        numberE = int(math.exp(a))
        
        count = 0
        while count < numberE:
            returnMsg += "E"
            count += 1

        await ctx.send(returnMsg)

@bot.command()
async def synth(ctx, *, inputArg = "1"):
    """Returns text with some a e s t h e t i c""" 
    message = await utils.get_text(ctx, inputArg)

    output = " ".join(message[0])
    await ctx.send(message[1] + output)

@bot.command()
async def b(ctx, *, inputArg = "1"):
    """Returns text with b replaced with :b:"""
    message = await utils.get_text(ctx, inputArg)

    output = message[0]
    for letter in ("b", "B"):
        output = output.replace(letter, ":b:")
    await ctx.send(message[1] + output)

@bot.command(hidden=True)
async def commit(ctx):
    await ctx.send(f"Current commit: ```{currentCommit}```")    

# Error handlers
@synth.error
async def synth_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("Hey mate, I can't send messages over 2000 characters")

bot.run(os.environ.get("DISCORD_KEY"))