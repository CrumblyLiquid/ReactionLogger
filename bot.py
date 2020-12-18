import discord
from discord.ext import commands

import logging
import json
from datetime import datetime
from pathlib import Path

# Load config
# token (str) - the bots token
# channel_id (int) - channel id where the logs will be pasted
# ignore_bot_messages (bool) -  ignore reactions on messages posted by bots
# ignore_bot_messages (bool) - ignore reactions by bots
class Config:
    def __init__(self, path=None):
        if path is None:
            path = Path(__file__).parent.absolute()/'./config.json'
        self.path = path
        self.load()

    def load(self):
        with open(self.path, 'r') as file:
            config = json.load(file)
            self.token = config['token']
            self.channel_id = config['channel_id']
            self.ignore_bot_messages = config['ignore_bot_messages']
            self.ignore_bot_reactions = config['ignore_bot_reactions']

config = Config()

# Logging | Logs discords internal stuff
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Embed creating function
# For stuff in the future
def get_embed(title: str, description: str, colour: discord.Colour):
    embed = discord.Embed(title=title, description=description, colour=colour)
    embed.set_footer(text='Made by Jaro#5648')
    return embed

# Creates complete reaction embed from payload
async def get_reaction_embed(payload: discord.RawReactionActionEvent):
        # guild = bot.get_guild(payload.guild_id)
        # if guild is None:
        #     guild = await bot.fetch_guild(payload.guild_id)
        
        channel = bot.get_channel(payload.channel_id)
        if channel is None:
            channel = await bot.fetch_channel(payload.channel_id)
            
        message = await channel.fetch_message(payload.message_id)
        
        if payload.member is not None:
            user = payload.member
        else:
            user = bot.get_user(payload.user_id)
            if user is None:
                user = await bot.fetch_user(payload.user_id)
            
        if payload.event_type == 'REACTION_ADD':
            colour = discord.Colour.green()
            event_type = 'Added'
        elif payload.event_type == 'REACTION_REMOVE':
            colour = discord.Colour.red()
            event_type = 'Removed'
            
        description = f'**{event_type} {payload.emoji}**\nAuthor: {user.mention}\nChannel: {channel.mention} ({channel.id})\nMessage ID: {payload.message_id}'
        embed = get_embed(title=message.content, description=description, colour=colour)
        return embed

# Determines if it should send the log message and sends it if needed
async def send_reaction_log(payload: discord.RawReactionActionEvent):
    if bot.intents.reactions and payload.guild_id != None:
        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if config.ignore_bot_messages and message.author.bot:
            return
         
        if payload.member is not None:
            user = payload.member
        else:
            user = bot.get_user(payload.user_id)
            if user is None:
                user = await bot.fetch_user(payload.user_id)
        if config.ignore_bot_reactions and user.bot:
            return
        embed = await get_reaction_embed(payload)
        await bot.get_channel(config.channel_id).send(embed=embed)

# We define bot instance
# There are buch of arguments we could pass in here - for more information read docs
bot = commands.Bot(command_prefix='?')

# Event is called when the bots internals are ready to handle commands, etc.
@bot.event
async def on_ready():
    print('[OK] Bots ready event called')

# Event is called whenever someone adds a reaction
# It passes payload which contains bunch of information which we can then parse and log
@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    await send_reaction_log(payload)

# Event is called whenever someone remove a reaction
# It passes payload which contains bunch of information which we can then parse and log
# The payload is the same type as payload in on_raw_reaction_add
@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    await send_reaction_log(payload)

# Runs the bot (any code after this point won't be executed)
bot.run(config.token)