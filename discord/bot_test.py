import os
import random
import discord
import requests
import asyncio

from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
from typing import Union

### --- REST api Initialization --- ###

base_url = "http://127.0.0.1:8000/"

### --- Bot Initialization --- ###

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN_TESTER')
DEV_MODE = True

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

### --- Functions --- ###

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_error(event, *args, **kwargs):
    with open('err.log', 'a') as f:
        if event == 'on_message':
            f.write(f'Unhandled message: {args[0]}\n')
        else:
            raise

@bot.event
async def on_command_error(ctx, error):
    message = ""
    if isinstance(error, commands.errors.CommandNotFound):
        message += 'Invalid command used.'
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        message += 'Missing required argument.'
    elif isinstance(error, commands.errors.BadArgument):
        message += 'Bad argument.'
    elif isinstance(error, commands.errors.CommandInvokeError):
        message += 'Error in command invocation.'
    elif isinstance(error, commands.errors.CheckFailure):
        message += 'You do not have permission to use this command.'
    else:
        raise error

    if DEV_MODE:
        message += f'\n{error}'

    await ctx.send(message)

### --- Commands --- ###

os.system('bot.py')
bot.run(TOKEN)