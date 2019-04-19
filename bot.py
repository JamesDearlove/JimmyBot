import discord
import utils
import asyncio
import os
import math
import feedparser
import requests
import bom
import shlex

from datetime import datetime, time, timezone
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

        self.loop.create_task(self.mcstatus_loop())

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

@bot.command(hidden=True)
async def commit(ctx):
    await ctx.send(f"Current commit: ```{currentCommit}```")    

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

# Error handlers
@synth.error
async def synth_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        await ctx.send("Sorry mate, I can't send messages over 2000 characters")

bot.run(os.environ.get("DISCORD_KEY"))