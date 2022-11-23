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
TOKEN = os.getenv('DISCORD_TOKEN')
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

@bot.event
async def on_member_join(member):
    await member.create_dm()
    # Important how to dm users
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

@bot.command(name='hello', help='Hello user!')
async def hello(ctx):
    response = 'Hello!'
    await ctx.channel.send(response)

@bot.command(name='roll', help='Rolls a dice')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='list-votings', help='Lists all votings')
async def list_votings(ctx):
    response = requests.get(base_url + "voting/")
    votings = response.json()

    embed = discord.Embed(title='Votings', color=discord.Color.random())

    for voting in votings:
        # ! TODO add public check
        embed.add_field(name=f'{voting["id"]}: {voting["name"]}', value=voting["question"]["desc"], inline=False)

    await ctx.send(embed=embed)

# Reaction lookup table
emotes = ["0️⃣","1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

@bot.command(name='get-voting', help='Gets a voting from ID')
async def get_voting(ctx, voting_id: int):
    response = requests.get(base_url + "voting/")
    votings = response.json()

    def check(r: discord.Reaction, u: Union[discord.Member, discord.User]):  # r = discord.Reaction, u = discord.Member or discord.User.
        return u.id == ctx.author.id and r.message.channel.id == ctx.channel.id and \
               str(r.emoji) in emotes

    # Extract the voting, send the message and add reactions
    for voting in votings:
        # ! TODO add public check
        if voting["id"] == voting_id:
            # Creating question message
            embed = discord.Embed(title=f'{voting["name"]}', color=discord.Color.random())

            # Adding options
            for option in voting["question"]["options"]:
                embed.add_field(name=emotes[int(option["number"])], 
                        value=f'{option["option"]}', 
                        inline=True)
            
            # Sending message
            msg = await ctx.send(embed=embed)

            # Adding reactions
            for i in range(len(voting["question"]["options"])):
                await msg.add_reaction(emotes[i+1])

            # Waiting for reaction
            try:
                reaction, user = await bot.wait_for('reaction_add', check = check, timeout = 60.0)
            except asyncio.TimeoutError:
                # at this point, the check didn't become True.
                await ctx.send(f"**{ctx.author}**, you didnt react correctly with within 60 seconds.")
                return
            else:
                # at this point, the check has become True and the wait_for has done its work, now we can do ours.
                # here we are sending some text based on the reaction we detected.
                return await ctx.send(f"{ctx.author} reacted with a {str(reaction.emoji)}")

bot.run(TOKEN)