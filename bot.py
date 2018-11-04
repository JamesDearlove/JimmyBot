import discord
from discord.ext import commands

import random
import time

bot = commands.Bot(command_prefix='!', description='The helpful JimmyD bot')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    
@bot.command()
async def hello(ctx):
    await ctx.send(":wave: Hello, there!")

@bot.command()
async def mock(ctx, a):
    msg = ctx.message.content[5:].lower()
    returnMsg = ""

    for char in msg:
        if random.randint(0,1) == 0:
            returnMsg += char.upper()
        else:
            returnMsg += char.lower()
        time.sleep(0.001)

    await ctx.send(returnMsg)

bot.run('NDgxMzM1Mzc5MzA4NTc2NzY5.Dl02lQ.y-X6tbHA1Z47vggCVxuipCB5ZPc')