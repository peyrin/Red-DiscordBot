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
import pylast
import pafy
import json
import requests

settings = {"POLL_DURATION" : 60}



#class RPS(Enum):
#    rock     = "\N{MOYAI}"
#    paper    = "\N{PAGE FACING UP}"
#    scissors = "\N{BLACK SCISSORS}"


#class RPSParser:
#    def __init__(self, argument):
#        argument = argument.lower()
#        if argument == "rock":
#            self.choice = RPS.rock
#        elif argument == "paper":
#            self.choice = RPS.paper
#        elif argument == "scissors":
#            self.choice = RPS.scissors
#        else:
#            raise


class General:
    """General commands."""

    def __init__(self, bot):
        self.bot = bot
        self.stopwatches = {}
        self.ball = ["As I see it, yes", "It is certain", "It is decidedly so", "Most likely", "Outlook good",
                     "Signs point to yes", "Without a doubt", "Yes", "Yes – definitely", "You may rely on it", "Reply hazy, try again",
                     "Ask again later", "Better not tell you now", "Cannot predict now", "Concentrate and ask again",
                     "Don't count on it", "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful"]
        self.poll_sessions = []
        self.livelisten_sessions = []
        self.showdown_mode = False

    @commands.command(hidden=True)
    async def ping(self):
        """Pong."""
        await self.bot.say("Pong.")

    @commands.command()
    async def choose(self, *choices):
        """Chooses between multiple choices.

        To denote multiple choices, you should use double quotes.
        """
        choices = [escape_mass_mentions(c) for c in choices]
        if len(choices) < 2:
            await self.bot.say('Not enough choices to pick from.')
        else:
            await self.bot.say(choice(choices))

    @commands.command(pass_context=True, name="avatar", aliases=["av"])
    async def avatar(self, ctx, user : discord.Member):
        header = {'Authorization': 'Client-ID 7404ac1d65b0973'}
        url = 'https://api.imgur.com/3/image'
        if user.avatar_url:
            avatar = user.avatar_url.replace('webp','png')
        else:
            avatar = user.default_avatar_url.replace('webp','png')
        r=requests.post(url,data=avatar,headers=header)
        avatar_image = json.loads(r.content)['data']['link']
        await self.bot.say(avatar_image)

    @commands.command(pass_context=True, name="imgur")
    async def imgur(self, ctx, image : str):
        """Uploads image to Imgur and returns a URL.
        !imgur [link to image]
        !imgur attached [upload the image as an attachment to the post]
        """
        header = {'Authorization': 'Client-ID 7404ac1d65b0973'}
        url = 'https://api.imgur.com/3/image'
        if image == 'attached' and len(ctx.message.attachments) > 0:
            image = ctx.message.attachments[0]['url']
        r=requests.post(url,data=image,headers=header)
        if r.status_code == 200:
            await self.bot.say(json.loads(r.content)['data']['link'])
        else:
            await self.bot.say('Upload failed.')

    @commands.command(pass_context=True)
    async def roll(self, ctx, number : int = 100):
        """Rolls random number (between 1 and user choice)

        Defaults to 100.
        """
        author = ctx.message.author
        if number > 1:
            n = randint(1, number)
            await self.bot.say("{} :game_die: {} :game_die:".format(author.mention, n))
        else:
            await self.bot.say("{} Maybe higher than 1? ;P".format(author.mention))

    @commands.command(pass_context=True)
    async def flip(self, ctx, user : discord.Member=None):
        """Flips a coin... or a user.

        Defaults to coin.
        """
        if user != None:
            msg = ""
            if user.id == self.bot.user.id:
                user = ctx.message.author
                msg = "Nice try. You think this is funny? How about *this* instead:\n\n"
            char = "abcdefghijklmnopqrstuvwxyz"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
            table = str.maketrans(char, tran)
            name = user.display_name.translate(table)
            char = char.upper()
            tran = "∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
            table = str.maketrans(char, tran)
            name = name.translate(table)
            await self.bot.say(msg + "(╯°□°）╯︵ " + name[::-1])
        else:
            await self.bot.say("*flips a coin and... " + choice(["HEADS!*", "TAILS!*"]))

#    @commands.command(pass_context=True)
#    async def rps(self, ctx, your_choice : RPSParser):
#        """Play rock paper scissors"""
#        author = ctx.message.author
#        player_choice = your_choice.choice
#        red_choice = choice((RPS.rock, RPS.paper, RPS.scissors))
#        cond = {
#                (RPS.rock,     RPS.paper)    : False,
#                (RPS.rock,     RPS.scissors) : True,
#                (RPS.paper,    RPS.rock)     : True,
#                (RPS.paper,    RPS.scissors) : False,
#                (RPS.scissors, RPS.rock)     : False,
#                (RPS.scissors, RPS.paper)    : True
#               }
#
#        if red_choice == player_choice:
#            outcome = None # Tie
#        else:
#            outcome = cond[(player_choice, red_choice)]
#
#        if outcome is True:
#            await self.bot.say("{} You win {}!"
#                               "".format(red_choice.value, author.mention))
#        elif outcome is False:
#            await self.bot.say("{} You lose {}!"
#                               "".format(red_choice.value, author.mention))
#        else:
#            await self.bot.say("{} We're square {}!"
#                               "".format(red_choice.value, author.mention))

    @commands.command(name="8", aliases=["8ball"])
    async def _8ball(self, *, question : str):
        """Ask 8 ball a question
        """
        await self.bot.say("`" + choice(self.ball) + "`")

    @commands.command(aliases=["sw"], pass_context=True)
    async def stopwatch(self, ctx):
        """Starts/stops stopwatch"""
        author = ctx.message.author
        if not author.id in self.stopwatches:
            self.stopwatches[author.id] = int(time.perf_counter())
            await self.bot.say(author.mention + " Stopwatch started!")
        else:
            tmp = abs(self.stopwatches[author.id] - int(time.perf_counter()))
            tmp = str(datetime.timedelta(seconds=tmp))
            await self.bot.say(author.mention + " Stopwatch stopped! Time: **" + tmp + "**")
            self.stopwatches.pop(author.id, None)

    @commands.command()
    async def lmgtfy(self, *, search_terms : str):
        """Creates a lmgtfy link"""
        search_terms = escape_mass_mentions(search_terms.replace(" ", "+"))
        await self.bot.say("https://lmgtfy.com/?q={}".format(search_terms))

    @commands.command(no_pm=True, hidden=True)
    async def hug(self, user : discord.Member, intensity : int=1):
        """Because everyone likes hugs

        Up to 10 intensity levels."""
        name = italics(user.display_name)
        if intensity <= -3:
            msg = name + " (っ˘̩╭╮˘̩)っ"
        elif intensity <= 0:
            msg = "(っ˘̩╭╮˘̩)っ " + name
        if intensity <= 0:
            msg = "(っ˘̩╭╮˘̩)っ" + name
        elif intensity <= 3:
            msg = "(っ´▽｀)っ " + name
        elif intensity <= 6:
            msg = "╰(*´︶`*)╯ " + name
        elif intensity <= 9:
            msg = "(つ≧▽≦)つ " + name
        elif intensity <= 12:
            msg = "(づ￣ ³￣)づ " + name + " ⊂(´・ω・｀⊂)"
        elif intensity >= 15:
            msg = "(づ♡ 3♡)づ " + name + " ⊂('^▽^´⊂)"
        await self.bot.say(msg)

    @commands.command(pass_context=True, no_pm=True)
    async def userinfo(self, ctx, *, user: discord.Member=None):
        """Shows users's informations"""
        author = ctx.message.author
        server = ctx.message.server

        if not user:
            user = author

        roles = [x.name for x in user.roles if x.name != "@everyone"]

        joined_at = self.fetch_joined_at(user, server)
        since_created = (ctx.message.timestamp - user.created_at).days
        since_joined = (ctx.message.timestamp - joined_at).days
        user_joined = joined_at.strftime("%d %b %Y %H:%M")
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        member_number = sorted(server.members,
                               key=lambda m: m.joined_at).index(user) + 1

        created_on = "{}\n({} days ago)".format(user_created, since_created)
        joined_on = "{}\n({} days ago)".format(user_joined, since_joined)

        game = "Chilling in {} status".format(user.status)

        if user.game is None:
            pass
        elif user.game.url is None:
            game = "Playing {}".format(user.game)
        else:
            game = "Streaming: [{}]({})".format(user.game, user.game.url)

        if roles:
            roles = sorted(roles, key=[x.name for x in server.role_hierarchy
                                       if x.name != "@everyone"].index)
            roles = ", ".join(roles)
        else:
            roles = "None"

        data = discord.Embed(description=game, colour=user.colour)
        data.add_field(name="Joined Discord on", value=created_on)
        data.add_field(name="Joined this server on", value=joined_on)
        data.add_field(name="Roles", value=roles, inline=False)
        data.set_footer(text="Member #{} | User ID:{}"
                             "".format(member_number, user.id))

        name = str(user)
        name = " ~ ".join((name, user.nick)) if user.nick else name

        if user.avatar_url:
            data.set_author(name=name, url=user.avatar_url)
            data.set_thumbnail(url=user.avatar_url)
        else:
            data.set_author(name=name)

        try:
            await self.bot.say(embed=data)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission "
                               "to send this")

    @commands.command(pass_context=True, no_pm=True)
    async def serverinfo(self, ctx):
        """Shows server's informations"""
        server = ctx.message.server
        online = len([m.status for m in server.members
                      if m.status == discord.Status.online or
                      m.status == discord.Status.idle])
        total_users = len(server.members)
        text_channels = len([x for x in server.channels
                             if x.type == discord.ChannelType.text])
        voice_channels = len(server.channels) - text_channels
        passed = (ctx.message.timestamp - server.created_at).days
        created_at = ("Since {}. That's over {} days ago!"
                      "".format(server.created_at.strftime("%d %b %Y %H:%M"),
                                passed))

        colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
        colour = int(colour, 16)

        data = discord.Embed(
            description=created_at,
            colour=discord.Colour(value=colour))
        data.add_field(name="Region", value=str(server.region))
        data.add_field(name="Users", value="{}/{}".format(online, total_users))
        data.add_field(name="Text Channels", value=text_channels)
        data.add_field(name="Voice Channels", value=voice_channels)
        data.add_field(name="Roles", value=len(server.roles))
        data.add_field(name="Owner", value=str(server.owner))
        data.set_footer(text="Server ID: " + server.id)

        if server.icon_url:
            data.set_author(name=server.name, url=server.icon_url)
            data.set_thumbnail(url=server.icon_url)
        else:
            data.set_author(name=server.name)

        try:
            await self.bot.say(embed=data)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission "
                               "to send this")

    @commands.command()
    async def urban(self, *, search_terms : str, definition_number : int=1):
        """Urban Dictionary search

        Definition number must be between 1 and 10"""
        def encode(s):
            return quote_plus(s, encoding='utf-8', errors='replace')

        # definition_number is just there to show up in the help
        # all this mess is to avoid forcing double quotes on the user

        search_terms = search_terms.split(" ")
        try:
            if len(search_terms) > 1:
                pos = int(search_terms[-1]) - 1
                search_terms = search_terms[:-1]
            else:
                pos = 0
            if pos not in range(0, 11): # API only provides the
                pos = 0                 # top 10 definitions
        except ValueError:
            pos = 0

        search_terms = "+".join([encode(s) for s in search_terms])
        url = "http://api.urbandictionary.com/v0/define?term=" + search_terms
        try:
            async with aiohttp.get(url) as r:
                result = await r.json()
            if result["list"]:
                definition = result['list'][pos]['definition']
                example = result['list'][pos]['example']
                defs = len(result['list'])
                msg = ("**Definition #{} out of {}:\n**{}\n\n"
                       "**Example:\n**{}".format(pos+1, defs, definition,
                                                 example))
                msg = pagify(msg, ["\n"])
                for page in msg:
                    await self.bot.say(page)
            else:
                await self.bot.say("Your search terms gave no results.")
        except IndexError:
            await self.bot.say("There is no definition #{}".format(pos+1))
        except:
            await self.bot.say("Error.")

    #Goodchat-specific commands start here

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

    @commands.command(pass_context=True, no_pm=True)
    async def showdown(self, ctx):
        """Display livelisten songs two at a time for music showdowns."""
        self.showdown_mode = not self.showdown_mode
        if self.showdown_mode:
            await self.bot.say("Showdown mode enabled.")
        else:
            await self.bot.say("Showdown mode disabled.")

    @commands.command(pass_context=True, no_pm=True)
    async def livelisten(self, ctx, *text):
        """Live-listen to an album. Bot will announce as each song begins."""
        message = ctx.message
        if len(text) == 1:
            if text[0].lower() == "stop":
                await self.endLivelisten(message)
                return
        if not self.getLivelistenByChannel(message):
            l = NewLiveListen(message, " ".join(text), self)
            if l.valid:
                self.livelisten_sessions.append(l)
                await l.start(self.showdown_mode)
            else:
                await self.bot.say("livelisten Artist - Album - Start position")
        else:
            await self.bot.say("A livelisten is already ongoing in this channel.")

    async def endLivelisten(self, message):
        if self.getLivelistenByChannel(message):
            l = self.getLivelistenByChannel(message)
            if l.author == message.author.id: # or isMemberAdmin(message)
                await self.getLivelistenByChannel(message).endlivelisten()
                await self.bot.say("Livelisten ended.")
            else:
                await self.bot.say("Only the author can stop the livelisten.")
        else:
            await self.bot.say("There's no livelisten ongoing in this channel.")

    def getLivelistenByChannel(self, message):
        for l in self.livelisten_sessions:
            if l.channel == message.channel:
                return l
        return False

    @commands.command(pass_context=True, no_pm=True)
    async def poll(self, ctx, *text):
        """Starts/stops a poll

        Usage example:
        poll Is this a poll?;Yes;No;Maybe
        poll stop"""
        message = ctx.message
        if len(text) == 1:
            if text[0].lower() == "stop":
                await self.endpoll(message)
                return
        if not self.getPollByChannel(message):
            check = " ".join(text).lower()
            if "@everyone" in check or "@here" in check:
                await self.bot.say("Nice try.")
                return
            p = NewPoll(message, " ".join(text), self)
            if p.valid:
                self.poll_sessions.append(p)
                await p.start()
            else:
                await self.bot.say("poll question;option1;option2 (...)")
        else:
            await self.bot.say("A poll is already ongoing in this channel.")

    async def endpoll(self, message):
        if self.getPollByChannel(message):
            p = self.getPollByChannel(message)
            if p.author == message.author.id: # or isMemberAdmin(message)
                await self.getPollByChannel(message).endPoll()
            else:
                await self.bot.say("Only the author can stop the poll.")
        else:
            await self.bot.say("There's no poll ongoing in this channel.")

    def getPollByChannel(self, message):
        for poll in self.poll_sessions:
            if poll.channel == message.channel:
                return poll
        return False

    async def check_poll_votes(self, message):
        if message.author.id != self.bot.user.id:
            if self.getPollByChannel(message):
                    self.getPollByChannel(message).checkAnswer(message)

    def fetch_joined_at(self, user, server):
        """Just a special case for someone special :^)"""
        if user.id == "96130341705637888" and server.id == "133049272517001216":
            return datetime.datetime(2016, 1, 10, 6, 8, 4, 443000)
        else:
            return user.joined_at

class NewLiveListen():
    def __init__(self, message, text, main):
        self.API_KEY = '2f31bfef663696243867c29ce86f5a0a'
        self.API_SECRET = '3722c32247e84c986395e84bec587ec5'
        self.network = pylast.LastFMNetwork(api_key=self.API_KEY, api_secret=self.API_SECRET)
        self.channel = message.channel
        self.author = message.author.id
        self.client = main.bot
        self.livelisten_sessions = main.livelisten_sessions
        if 'youtube.com/playlist' in text:
            try:
                msg = [ans.strip() for ans in text.split(" - ")]
                if len(msg) != 1 and len(msg) != 2:
                    self.valid = False
                    return None
                else:
                    self.valid = True
                playlist = pafy.get_playlist(msg[0])
                self.playlist_title = playlist['title']
                self.custom_list = []
                for i in playlist['items']:
                    self.custom_list.append([i['pafy'].title, i['pafy'].length])
                self.valid = True
                if len(msg) == 2:
                    self.start_position = int(msg[1]) - 1
                else:
                    self.start_position = 0
            except ValueError:
                self.valid = False
                return None
        else:
            self.custom_list = None
            msg = [ans.strip() for ans in text.split(" - ")]
            if len(msg) != 2 and len(msg) != 3:
                self.valid = False
                return None
            else:
                self.valid = True
            self.artist_search = msg[0]
            self.album_search = msg[1]
            if len(msg) == 3:
                self.start_position = int(msg[2]) - 1
            else:
                self.start_position = 0

    async def start(self, showdown_mode):
        if self.custom_list is None:
            try:
                album = self.network.get_album(self.artist_search, self.album_search)
                tracks = album.get_tracks()
                check_if_album_has_nonzero_tracks = tracks[1]
                if album.get_cover_image():
                    await self.client.send_message(self.channel, "Listening to: {}\n\n{}".format(str(album), album.get_cover_image()))
                else:
                    await self.client.send_message(self.channel, "Listening to: {}".format(str(album)))
                await asyncio.sleep(1)
                await self.client.send_message(self.channel, "Album starts in: 3")
                await asyncio.sleep(1)
                i = 2
                while i > 0:
                    await self.client.send_message(self.channel, i)
                    i -= 1
                    await asyncio.sleep(1)
                j = self.start_position
                while j < len(tracks) and self.valid:
                    await self.client.send_message(self.channel, "Now playing: {}".format(str(tracks[j])))
                    await asyncio.sleep(tracks[j].get_duration()/1000)
                    j += 1
                if self.valid:
                    await self.client.send_message(self.channel, "It end.")
                    await self.endlivelisten()
            except (pylast.WSError, IndexError) as e:
                await self.endlivelisten()
                await self.client.send_message(self.channel, "Album wasn't found.")
        else:
            try:
                await self.client.send_message(self.channel, "Listening to: {}".format(self.playlist_title))
                await asyncio.sleep(1)
                await self.client.send_message(self.channel, "Playlist starts in: 3")
                await asyncio.sleep(1)
                i = 2
                while i > 0:
                    await self.client.send_message(self.channel, i)
                    i -= 1
                    await asyncio.sleep(1)
                j = self.start_position
                while j < len(self.custom_list) and self.valid:
                    if showdown_mode:
                        if j%2 == 0:
                            await self.client.send_message(self.channel, "Current match: **{}** vs.\n{}".format(self.custom_list[j][0], self.custom_list[j+1][0]))
                        else:
                            await self.client.send_message(self.channel, "Current match: {} vs.\n**{}**".format(self.custom_list[j-1][0], self.custom_list[j][0]))
                    else:
                        await self.client.send_message(self.channel, "Now playing: {}".format(self.custom_list[j][0]))
                    await asyncio.sleep(self.custom_list[j][1])
                    j += 1
                if self.valid:
                    await self.client.send_message(self.channel, "It end.")
                    await self.endlivelisten()
            except () as e:
                await self.client.send_message(self.channel, "Something went wrong?")

    async def endlivelisten(self):
        self.valid = False
        self.livelisten_sessions.remove(self)



class NewPoll():
    def __init__(self, message, text, main):
        self.channel = message.channel
        self.author = message.author.id
        self.client = main.bot
        self.poll_sessions = main.poll_sessions
        msg = [ans.strip() for ans in text.split(";")]
        if len(msg) < 2: # Needs at least one question and 2 choices
            self.valid = False
            return None
        else:
            self.valid = True
        self.already_voted = []
        self.question = msg[0]
        msg.remove(self.question)
        self.answers = {}
        i = 1
        for answer in msg: # {id : {answer, votes}}
            self.answers[i] = {"ANSWER" : answer, "VOTES" : 0}
            i += 1

    async def start(self):
        msg = "**POLL STARTED!**\n\n{}\n\n".format(self.question)
        for id, data in self.answers.items():
            msg += "{}. *{}*\n".format(id, data["ANSWER"])
        msg += "\nType the number to vote!"
        await self.client.send_message(self.channel, msg)
        await asyncio.sleep(settings["POLL_DURATION"])
        if self.valid:
            await self.endPoll()

    async def endPoll(self):
        self.valid = False
        msg = "**POLL ENDED!**\n\n{}\n\n".format(self.question)
        for data in self.answers.values():
            msg += "*{}* - {} votes\n".format(data["ANSWER"], str(data["VOTES"]))
        await self.client.send_message(self.channel, msg)
        self.poll_sessions.remove(self)

    def checkAnswer(self, message):
        try:
            i = int(message.content)
            if i in self.answers.keys():
                if message.author.id not in self.already_voted:
                    data = self.answers[i]
                    data["VOTES"] += 1
                    self.answers[i] = data
                    self.already_voted.append(message.author.id)
        except ValueError:
            pass

def setup(bot):
    n = General(bot)
    bot.add_listener(n.check_poll_votes, "on_message")
    bot.add_cog(n)
