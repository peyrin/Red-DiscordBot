import discord
from discord.ext import commands
from .utils.chat_formatting import escape_mass_mentions, italics, pagify
from random import randint
from random import choice
from enum import Enum
from urllib.parse import quote_plus
import datetime
import time
import aiohttp
import asyncio

class Goodchat:
    """Goodchat-specific commands."""

    @commands.command(hidden=True)
    async def pong(self):
        """Ping."""
        await self.bot.say("Ping.")

    @commands.command(pass_context=True, no_pm=True)
    async def whodunit(self, ctx):
        """Whodunit?"""
        server = ctx.message.server
        member_list = list(server.members)
        await self.bot.say("It was " + choice(member_list).display_name + "!!!")

    @commands.command(name="fahrenheit")
    async def fahrenheit(self, *, temp : int):
        """Converts Fahrenheit temperature to Celsius
        """
        newtemp = (temp-32)*5.0/9.0
        if newtemp < 0:
            await self.bot.say(str(temp) + " degrees Fahrenheit is " + str(newtemp)[:5] + " degrees Celsius.")
        else:
            await self.bot.say(str(temp) + " degrees Fahrenheit is " + str(newtemp)[:4] + " degrees Celsius.")

    @commands.command(name="kelvin")
    async def kelvin(self, *, temp : int):
        """Converts Kelvin temperatures...for some reason
        """
        newcelsius = temp - 273.15
        newfahrenheit = ((temp - 273.15) * 9.0/5.0) + 32
        await self.bot.say(str(temp) + " Kelvin is " + str(round(newcelsius, 2)) + " degrees Celsius and " + str(round(newfahrenheit, 2)) + " degrees Fahrenheit.")

    @commands.command(name="celsius")
    async def celsius(self, *, temp : int):
        """Converts Celsius temperature to Fahrenheit
        """
        newtemp = (temp * 9.0/5.0) + 32
        await self.bot.say(str(temp) + " degrees Celsius is " + str(newtemp) + " degrees Fahrenheit.")

    @commands.command(pass_context=True, no_pm=True)
    async def sue(self, ctx, user : discord.Member):
        """Take a user to court."""
        if user.id == self.bot.user.id:
                user = ctx.message.author
                await self.bot.say("Nice try. You think this is funny? How about let's sue {}, huh?".format(user.mention))
        else:
            await self.bot.say("{} has been sued".format(user.mention))

    @commands.command(pass_context=True, no_pm=True)
    async def slap(self, ctx, user : discord.Member):
        """Slaps a user."""
        if user.id == self.bot.user.id:
                user = ctx.message.author
                await self.bot.say("Nice try. You think this is funny? *POW!* *slaps {}*".format(user.mention))
        else:
            await self.bot.say("*POW!* {} has been slapped".format(user.mention))


def setup(bot):
    n = General(bot)
    bot.add_listener(n.check_poll_votes, "on_message")
    bot.add_cog(n)
