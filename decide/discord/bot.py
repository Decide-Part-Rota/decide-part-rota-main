import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands

#TOKEN = os.environ['DISCORD_TOKEN']
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

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
    if isinstance(error, commands.errors.CommandNotFound):
        await ctx.send('Invalid command used.')
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('Missing required argument.')
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.send('Bad argument.')
    elif isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send('Error in command invocation.')
    elif isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have permission to use this command.')
    else:
        raise error

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.send('Missing required argument.')
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.send('Bad argument.')
    elif isinstance(error, commands.errors.CommandInvokeError):
        await ctx.send('Error in command invocation.')
    else:
        raise error

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
    await message.channel.send(response)

@bot.command(name='roll', help='Rolls a dice')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='get-poll', help='Gets a poll from ID')
async def get_poll(ctx, poll_id: int):
    print(f'poll_id: {poll_id}')
    #queryset = Voting.objects.all()

bot.run(TOKEN)