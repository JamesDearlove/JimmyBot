import discord
import asyncio
import os
import math
import feedparser
import requests
import shlex

import database
import bom
import utils
from settings import *

from datetime import datetime, time, timezone
from random import choice

from discord.ext import commands
from discord.utils import get

import atexit

CURRENT_COMMIT = os.environ["HEROKU_SLUG_COMMIT"]

MAIN_CHANNEL = int(os.environ["DEFAULT_CHANNEL_ID"])
MAIN_GUILD = int(os.environ["DEFAULT_GUILD_ID"])

dbConnection = database.Database()

prefix = "!"
activity = utils.jims_picker()

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bg_task = self.loop.create_task(self.bot_schedule())

        # Disabled as no server is running.
        # self.loop.create_task(self.mcstatus_loop())

    async def on_ready(self):
        print(f"Logged in as {bot.user.name}")
        print(f"With the ID {bot.user.id}")

    async def mcstatus_loop(self):
        await self.wait_until_ready()
        # could break if there is more than one 'minecraft-life' channel.
        # TODO: avoid requiring a #minecraft-life channel.
        channel = next(ch for ch in self.get_all_channels() if ch.name == 'minecraft-life')
        
        # used to make the datetime timezone-aware
        local_tz = datetime.now(timezone.utc).astimezone().tzinfo
        def make_embed():
            embed = discord.Embed(description=utils.get_mcstatus_text('tms.jamesdearlove.com'))
            embed.colour = 0x5b8731 # Minecraft green
            embed.set_footer(text='!mcstatus')
            embed.timestamp = datetime.now(tz=local_tz)
            return embed

        # look for a pinned message with !mcstatus in the embed footer.
        pins = await channel.pins()
        mcstatus_id = None
        for p in pins:
            try:
                if p.embeds[0].footer.text == '!mcstatus':
                    mcstatus_id = p.id
                    break
            except Exception as e:
                continue 
        if mcstatus_id is None:
            # no existing mcstatus message. send a new one.
            mcstatus_id = (await channel.send(embed=make_embed())).id

        while not self.is_closed():
            # update mcstatus message every 5 minutes.
            message = await channel.fetch_message(mcstatus_id)
            await message.edit(embed=make_embed())
            await asyncio.sleep(5*60)

    # Runs tasks at set times
    async def bot_schedule(self):
        await self.wait_until_ready() 
        channel = self.get_channel(MAIN_CHANNEL)

        while not self.is_closed():
            # Grabs the current time (Brisbane timezone)
            await self.update_activity()
            check_time = utils.get_local_time().time()

            # Good morning message (9am)
            if time(9,0) <= check_time <= time(9,2):
                await self.send_motd()

            # New xkcd comic (3pm)
            if time(15,0) <= check_time <= time(15,2):
                check_day = datetime.utcnow().weekday()
                if check_day == 0 or check_day == 2 or check_day == 4 :
                    await self.send_xkcd()
            
            # Sleep until the next hour
            minutesToSleep = 60 - datetime.utcnow().minute % 60
            await asyncio.sleep(minutesToSleep * 60)

    async def update_activity(self):
        activity = utils.jims_picker()
        await bot.change_presence(activity=discord.Game(activity))

    async def send_xkcd(self):
        xkcd_comic = utils.get_xkcd()

        servers = dbConnection.fetchAllSettings()

        for server in servers:
            if server.xkcd_channel == None:
                continue

            channel = self.get_channel(server.motd_channel)

            await channel.send("New xkcd comic!")
            await channel.send(xkcd_comic)

    async def send_motd(self):
        """Sends the message of the day to the default channel"""
        # channel = self.get_channel(MAIN_CHANNEL)
        servers = dbConnection.fetchAllSettings()

        todays_holidays = utils.get_fun_holiday()

        for server in servers:
            if server.motd_channel == None:
                continue

            channel = bot.get_channel(server.motd_channel)
            emojis = bot.get_guild(server.server_id).emojis
            if len(emojis) == 0:
                emojis = ["🎉"]
            
            await channel.send("Good Morning!")

            # Checks for any events for today in the group calendar
            # If there's no event, grab today's fun holiday and react accordingly
            # TODO: Move group events out to database (Currently checks if in home server)
            today_event = utils.get_today_event()
            if today_event == [] or server.server_id != MAIN_GUILD:
                holiday = choice(todays_holidays)
                msg = await channel.send(f"Today is {holiday}!")
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

@atexit.register
def goodbye():
    print("Shutting down")
    dbConnection.close()
    print("See you later")

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

@bot.command(hidden=True)
async def commit(ctx):
    await ctx.send(f"Current commit: ```{CURRENT_COMMIT}```")    

@bot.command()
async def holiday(ctx):
    today = utils.get_fun_holiday()
    for event in today:
        await ctx.send("Today is " + event)

@bot.command()
async def mcstatus(ctx, *, inputArg = 'tms.jamesdearlove.com'):
    """Gets information about a Minecraft server."""
    await ctx.send(utils.get_mcstatus_text(inputArg))

dabs = ["normal", "dabbing", "fast", "hyper", "ludicrous"]

@bot.command()
async def dab(ctx, speed = "normal"):
    """Dab on command. Speeds between 0-4 or normal, dabbing, fast, hyper, or ludicrous"""
    if not any(speed in s for s in dabs):
        if (speed.isdigit()):
            speed_int = int(speed)
            speed = dabs[speed_int]
        else:
            return
    
    dab_image = discord.File(f"emotes/dab_{speed}.gif", "dab.gif")

    await ctx.send(file=dab_image)


@bot.command()
async def poll(ctx, question, *, options=None):
    """Creates a poll, defaults to Yes/No with a maximum of 9 options
    Syntax: !poll "Question" "Option 1" "Option 2" ..."""
    # Checks if the user specified options, assume yes/no if no options are given
    responses = []
    if options == None:
        responses.append(("Yes", "👍"))
        responses.append(("No", "👎"))
    else:
        # Splits the options argument into different responses
        split_options = shlex.split(options)
        if split_options.__len__() > 9:
            await ctx.send("Cannot have more than 9 options")
            return
        for indx, s in enumerate(split_options):
            responses.append((s, f"{indx + 1}\N{COMBINING ENCLOSING KEYCAP}"))

    # Create an embed for the message
    poll_creator = ctx.message.author.display_name
    embed_text = []
    for answer in responses:
        embed_text.append(f"{answer[1]} {answer[0]}\n")
    embed = discord.Embed(title=question, description="\n".join(embed_text))
    embed.set_footer(text=f"Poll created by {poll_creator}")
    
    # Send message and add reacts to the message
    message = await ctx.send(embed=embed)
    for answer in responses:
        await message.add_reaction(answer[1])

bot.add_cog(Settings(bot, dbConnection))

# Error handlers
# @settings.error
async def setting_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You don't have authority over me")

@synth.error
async def synth_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("Sorry mate, I can't send messages over 2000 characters")

bot.run(os.environ.get("DISCORD_KEY"))