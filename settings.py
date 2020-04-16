import discord

import database
import bom
import utils

from datetime import datetime, time, timezone
from random import choice

from discord.ext import commands
from discord.utils import get

class Settings(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.command() 
    @commands.has_permissions(manage_guild=True)
    async def slist(self, ctx):
        settingData = self.db.fetchSetting(ctx.guild.id)

        if settingData == None or str(settingData) == '':
            await ctx.send("This server doesn't have any custom settings.")
            return

        output = ""
        if settingData.motd_channel != None:
            channel = self.bot.get_channel(settingData.motd_channel)
            output += f"**MOTD channel:** {channel}\n"
        if settingData.mcstatus_server != None:
            output += f"**Default MC server status:** {settingData.mcstatus_server}\n"
        if settingData.xkcd_channel != None:
            channel = self.bot.get_channel(settingData.xkcd_channel)
            output += f"**xkcd channel:** {channel}\n"


        embed = discord.Embed(title=f"Settings for {ctx.guild}", description=output)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def sclear(self, ctx, setting):
        await self.sset(ctx, setting)

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def sclearall(self, ctx):
        settingData = self.db.fetchSetting(ctx.guild.id)

        if settingData == None or str(settingData) == '':
            await ctx.send("This server doesn't have any custom settings.")
            return

        self.db.deleteSetting(ctx.guild.id)

        await ctx.send(f"Settings cleared for {ctx.guild}")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def sset(self, ctx, setting, value = None):
        settingUpdated = False

        settingData = self.db.fetchSetting(ctx.guild.id)

        if settingData == None:
            self.db.createSetting(ctx.guild.id)

        if setting == "motd_channel":
            if value == None:
                self.db.updateMotdChannel(ctx.guild.id, value)
                settingUpdated = True
            else:
                value = utils.strip_non_digits(value)

                if await self.channel_validate(ctx, value):
                    self.db.updateMotdChannel(ctx.guild.id, value)
                    settingUpdated = True

        elif setting == "mcstatus_server":
            self.db.updateMcServer(ctx.guild.id, value)
            settingUpdated = True

        elif setting == "xkcd_channel":
            if value == None:
                self.db.updateXkcdChannel(ctx.guild.id, value)
                settingUpdated = True
            else:
                value = utils.strip_non_digits(value)

                if await self.channel_validate(ctx, value):
                    self.db.updateXkcdChannel(ctx.guild.id, value)
                    settingUpdated = True

        if (settingUpdated):
            await ctx.send("Setting updated")
            await self.slist(ctx)

    async def channel_validate(self, ctx, channelid):
        if channelid == "":
            await ctx.send("Channel is invalid")
            return

        channel = self.bot.get_channel(int(channelid))

        if channel == None:
            await ctx.send("Channel is invalid")
        elif channel.guild != ctx.guild:
            await ctx.send("Channel must be in this server")
        elif channel.type != discord.ChannelType.text:
            await ctx.send("Channel must be a text channel")
        else:
            return True
        
        return False
