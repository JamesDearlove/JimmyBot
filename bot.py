import discord
import utils
import asyncio
import os
import math
import feedparser
import requests
import bom

from mcstatus import MinecraftServer
from datetime import datetime, time
from random import choice

from discord.ext import commands
from discord.utils import get

currentCommit = os.environ.get("HEROKU_SLUG_COMMIT")

prefix = "!"
activity = utils.jims_picker()
main_channel = int(os.environ.get("DEFAULT_CHANNEL_ID"))
main_guild = int(os.environ.get("DEFAULT_GUILD_ID"))

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bg_task = self.loop.create_task(self.bot_schedule())

    async def on_ready(self):
        print(f"Logged in as {bot.user.name}")
        print(f"With the ID {bot.user.id}")
        
    # Runs tasks at set times
    async def bot_schedule(self):
        await self.wait_until_ready() 
        channel = self.get_channel(main_channel)

        while not self.is_closed():
            # Update presence message
            activity = utils.jims_picker()
            await bot.change_presence(activity=discord.Game(activity))

            # Grabs the current time (Brisbane timezone)
            check_time = utils.get_local_time().time()

            # Good morning message (9am)
            if time(9,0) <= check_time <= time(9,2):
                await channel.send("Good Morning!")
                await self.send_motd()

            # New xkcd comic (3pm)
            if time(15,0) <= check_time <= time(15,2):
                check_day = datetime.utcnow().weekday()
                if check_day == 0 or check_day == 2 or check_day == 4 :
                    await asyncio.sleep(60)
                    xkcd_comic = utils.get_xkcd()
                    await channel.send("New xkcd comic!")
                    await channel.send(xkcd_comic)
            
            # Sleep until the next hour
            minutesToSleep = 60 - datetime.utcnow().minute % 60
            await asyncio.sleep(minutesToSleep * 60)

    async def send_motd(self):
        """Sends the message of the day to the default channel"""
        channel = self.get_channel(main_channel)
        emojis = bot.get_guild(main_guild).emojis
        
        # Checks for any events for today in the group calendar
        # If there's no event, grab today's fun holiday and react accordingly
        today_event = utils.get_today_event()
        if today_event == []:
            today_event = utils.get_fun_holiday()
            holiday = choice(today_event)
            msg = await channel.send(f"Today is {holiday[1]}!")
            await msg.add_reaction(choice(emojis))
        else:
            for event in today_event:
                # Checks what type of custom event it is and acts accordingly
                if event[0] == "H":
                    msg = await channel.send(f"Today is {event[1]}!")
                    await msg.add_reaction(choice(emojis))
                elif event[0] == "B":
                    user = bot.get_user(int(event[1]))
                    msg = await channel.send(f"Today is {user.mention}'s Birthday!")
                    await msg.add_reaction("🎂")

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

@bot.command()
async def xkcd(ctx):
    """Gets a random xkcd comic"""
    random_redirect = requests.get("http://c.xkcd.com/random/comic/")
    comic_url = random_redirect.history[1].url
    await ctx.send(comic_url)

@bot.command()
async def weather(ctx):
    """Gets the current weather"""
    await ctx.message.add_reaction("🤔")
    default_loc = "Coolangatta"

    observation = bom.get_observation(default_loc)
    forecast = bom.get_forecast(default_loc, 0)
    precis = forecast["precis"]
    forecast_icon = int(forecast["forecast_icon_code"])
    forecast_icon = bom.icon_emote(forecast_icon)
    current_temp = observation["air_temperature"]
    apparent_temp = observation["apparent_temp"]

    await ctx.message.remove_reaction("🤔", bot.user)

    await ctx.send(f"Currently at {default_loc} the temperature is {current_temp}°C (feels like {apparent_temp}°C)\n{precis}")
    await ctx.send(forecast_icon)

@bot.command()
async def today(ctx):
    await bot.send_motd()

@bot.command(hidden=True)
async def commit(ctx):
    await ctx.send(f"Current commit: ```{currentCommit}```")    

@bot.command()
async def mcstatus(ctx, *, inputArg = 'tms.jamesdearlove.com'):
    """Gets information about a Minecraft server."""
    server = MinecraftServer.lookup(inputArg)

    status = server.status() 

    address = f'{server.host}:{server.port}'
    motd = status.description['text'] if type(status.description) is dict else status.description

    version = status.version.name
    software = version

    ping = f'{status.latency} ms'

    players = f'{status.players.online}/{status.players.max}'

    if status.players.sample:
        players = f'({players}) ' + ', '.join([x.name for x in status.players.sample])

    full_status = [
        '**Minecraft Server Status**',
        ':globe_with_meridians: ' + address,
        ':loudspeaker: ' + motd,
        ':desktop: ' + software,
        ':left_right_arrow: ' + ping,
        '👤 ' + players
    ]

    message = '\n'.join(full_status)

    await ctx.send(message)

# Error handlers
@synth.error
async def synth_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("Sorry mate, I can't send messages over 2000 characters")

bot.run(os.environ.get("DISCORD_KEY"))