from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from .utils.chat_formatting import pagify, box
from random import choice
import os
import re


class CustomCommands:
    """Custom commands

    Creates commands used to display text"""

    def __init__(self, bot):
        self.bot = bot
        self.file_path = "data/customcom/commands.json"
        self.c_commands = dataIO.load_json(self.file_path)

#    @commands.group(aliases=["cc"], pass_context=True, no_pm=True)
#    async def customcom(self, ctx):
#        """Custom commands management"""
#        if ctx.invoked_subcommand is None:
#            await self.bot.send_cmd_help(ctx)

    @commands.command(name="learn", pass_context=True)
    #@checks.mod_or_permissions(administrator=True)
    async def cc_add(self, ctx, command : str, *, text):
        """Adds a custom command. If your command is more than one word long, make sure to use quotes!

        Example:
        [p]learn "your command" Text you want
        """
        server = ctx.message.server
        command = command.lower()
        if command in self.bot.commands:
            await self.bot.say("That command is already a standard command.")
            return
        if server.id not in self.c_commands:
            self.c_commands[server.id] = {}
        cmdlist = self.c_commands[server.id]
        if command not in cmdlist:
            cmdlist[command] = [text]
            self.c_commands[server.id] = cmdlist
        else:
            if text not in cmdlist[command]:
                command_list = list(cmdlist[command])
                command_list.append(text)
                cmdlist[command] = list(command_list)
            else:
                await self.bot.say("I already know that!")
                return
        self.c_commands[server.id] = cmdlist
        dataIO.save_json(self.file_path, self.c_commands)
        await self.bot.say("I learned that!")


#    @customcom.command(name="edit", pass_context=True)
#    @checks.mod_or_permissions(administrator=True)
#    async def cc_edit(self, ctx, command : str, *, text):
#        """Edits a custom command
#
#        Example:
#        [p]customcom edit yourcommand Text you want
#        """
#        server = ctx.message.server
#        command = command.lower()
#        if server.id in self.c_commands:
#            cmdlist = self.c_commands[server.id]
#            if command in cmdlist:
#                cmdlist[command] = text
#                self.c_commands[server.id] = cmdlist
#                dataIO.save_json(self.file_path, self.c_commands)
#                await self.bot.say("Custom command successfully edited.")
#            else:
#                await self.bot.say("That command doesn't exist. Use "
#                                   "`{}customcom add` to add it."
#                                   "".format(ctx.prefix))
#        else:
#            await self.bot.say("There are no custom commands in this server."
#                               " Use `{}customcom add` to start adding some."
#                               "".format(ctx.prefix))

    @commands.command(name="forget", pass_context=True)
    #@checks.mod_or_permissions(administrator=True)
    async def cc_delete(self, ctx, command : str, *, text):
        """Deletes a response from a custom command

        Example:
        [p]forget yourcommand response"""
        server = ctx.message.server
        command = command.lower()
        try:
            number = int(text)-1
            if server.id in self.c_commands:
                cmdlist = self.c_commands[server.id]
                if command in cmdlist:
                    command_list = list(cmdlist[command])
                    if number > len(command_list):
                        await self.bot.say("Can't forget that if I didn't know it in the first place!")
                    command_list.pop(number)
                    if len(command_list) > 0:
                        cmdlist[command] = list(command_list)
                    else:
                        cmdlist.pop(command, None)
                    self.c_commands[server.id] = cmdlist
                    dataIO.save_json(self.file_path, self.c_commands)
                    await self.bot.say("I forgot that!")
                else:
                    await self.bot.say("That command doesn't exist.")
            else:
                await self.bot.say("There are no custom commands in this server."
                                   " Use `{}customcom add` to start adding some."
                                   "".format(ctx.prefix))
        except:
            if server.id in self.c_commands:
                cmdlist = self.c_commands[server.id]
                if command in cmdlist:
                    command_list = list(cmdlist[command])
                    try:
                        command_list.remove(text)
                        if len(command_list) > 0:
                            cmdlist[command] = list(command_list)
                        else:
                            cmdlist.pop(command, None)
                        self.c_commands[server.id] = cmdlist
                        dataIO.save_json(self.file_path, self.c_commands)
                        await self.bot.say("I forgot that!")
                    except ValueError:
                        await self.bot.say("Can't forget that if I didn't know it in the first place!")
                else:
                    await self.bot.say("That command doesn't exist.")
            else:
                await self.bot.say("There are no custom commands in this server."
                                   " Use `{}customcom add` to start adding some."
                                   "".format(ctx.prefix))

    @commands.command(name="list", pass_context=True)
    async def cc_list(self, ctx):
        """Shows custom commands list"""
        server = ctx.message.server
        commands = self.c_commands.get(server.id, {})

        if not commands:
            await self.bot.say("There are no custom commands in this server."
                               " Use `{}customcom add` to start adding some."
                               "".format(ctx.prefix))
            return

        commands = "\n".join([c for c in sorted(commands)])

        if len(commands) < 1500:
            await self.bot.say(box(commands))
        else:
            for page in pagify(commands, delims=[" ", "\n"]):
                await self.bot.whisper(box(page))

    @commands.command(name="remember", pass_context=True)
    async def cc_remember(self, ctx, command : str = None, *, number: int = None):
        """Remembers response n for a certain command. If your command is more than one word, remember to use double quotes...

        Example:
        [p]remember "my command" 1"""
        server = ctx.message.server
        channel = ctx.message.channel
        if command == None and number == None:
            commands = self.c_commands.get(server.id, {})

            if not commands:
                await self.bot.say("There are no custom commands in this server."
                                   " Use `{}customcom add` to start adding some."
                                   "".format(ctx.prefix))
                return

            commands = "\n".join([c for c in sorted(commands)])

            if len(commands) < 1500:
                await self.bot.say(box(commands))
            else:
                for page in pagify(commands, delims=[" ", "\n"]):
                    await self.bot.whisper(box(page))
            return
        command = command.lower()
        if number == None:
            if server.id in self.c_commands:
                cmdlist = self.c_commands[server.id]
                if command in cmdlist:
                    command_list = list(cmdlist[command])
                    result = '```I remember ' if len(command_list) < 20 else 'I remember '
                    result += str(len(command_list))
                    result += ' things about '
                    result += command
                    result += ": \n"
                    if len(command_list) < 20:
                        for e in command_list:
                            result += str(command_list.index(e)+1)
                            result += '. '
                            result += str(e)
                            result += '\n'
                        result += '```'
                        await self.bot.send_message(channel, result)
                    else:
                        result += 'Argh. Go here instead: https://github.com/peyrin/Red-DiscordBot/blob/develop/data/customcom/commands.json'
                        await self.bot.send_message(channel, result)
                else:
                    await self.bot.say("That command doesn't exist.")
            else:
                await self.bot.say("There are no custom commands in this server."
                                   " Use `{}customcom add` to start adding some."
                                   "".format(ctx.prefix))
        elif number < 1:
            await self.bot.say("Numbering starts at 1!")
            return
        elif number != None:
            number = number - 1
            if server.id in self.c_commands:
                cmdlist = self.c_commands[server.id]
                if command in cmdlist:
                    command_list = list(cmdlist[command])
                    try:
                        result = command_list[number]
                    except IndexError:
                        await self.bot.say("I don't remember that many things!")
                        return
                    result = self.format_cc(result, command)
                    await self.bot.send_message(channel, result)
                else:
                    await self.bot.say("That command doesn't exist.")
            else:
                await self.bot.say("There are no custom commands in this server."
                                   " Use `{}customcom add` to start adding some."
                                   "".format(ctx.prefix))


    async def on_message(self, message):
        if len(message.content) < 2 or message.channel.is_private:
            return

        server = message.server
        prefix = self.get_prefix(message)

        if not prefix:
            return

        if server.id in self.c_commands and self.bot.user_allowed(message):
            cmdlist = self.c_commands[server.id]
            cmd = message.content[len(prefix):]
            if cmd in cmdlist:
                command_list = list(cmdlist[cmd])
                result = choice(command_list)
                result = self.format_cc(result, message)
                await self.bot.send_message(message.channel, result)
            elif cmd.lower() in cmdlist:
                command_list = list(cmdlist[cmd.lower()])
                result = choice(command_list)
                result = self.format_cc(result, message)
                await self.bot.send_message(message.channel, result)

    def get_prefix(self, message):
        for p in self.bot.settings.get_prefixes(message.server):
            if message.content.startswith(p):
                return p
        return False

    def format_cc(self, command, message):
        results = re.findall("\{([^}]+)\}", command)
        for result in results:
            param = self.transform_parameter(result, message)
            command = command.replace("{" + result + "}", param)
        return command

    def transform_parameter(self, result, message):
        """
        For security reasons only specific objects are allowed
        Internals are ignored
        """
        raw_result = "{" + result + "}"
        objects = {
            "message" : message,
            "author"  : message.author,
            "channel" : message.channel,
            "server"  : message.server
        }
        if result in objects:
            return str(objects[result])
        try:
            first, second = result.split(".")
        except ValueError:
            return raw_result
        if first in objects and not second.startswith("_"):
            first = objects[first]
        else:
            return raw_result
        return str(getattr(first, second, raw_result))


def check_folders():
    if not os.path.exists("data/customcom"):
        print("Creating data/customcom folder...")
        os.makedirs("data/customcom")


def check_files():
    f = "data/customcom/commands.json"
    if not dataIO.is_valid_json(f):
        print("Creating empty commands.json...")
        dataIO.save_json(f, {})


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(CustomCommands(bot))
