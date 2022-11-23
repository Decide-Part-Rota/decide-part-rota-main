import os
import random
import discord
from dotenv import load_dotenv
from discord.ext import commands

#TOKEN = os.environ['DISCORD_TOKEN']
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
    await message.channel.send(response)

@bot.command(name='roll', help='Rolls a dice')
async def roll(ctx, number_of_dice: int, number_of_sides: int):
    dice = [
        str(random.choice(range(1, number_of_sides + 1)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

# Voting
# - Name
# - Description
# - Question
#   - Description
#   - Options
#     - Number
#     - Option
# - Start and end date

test_voting = {
    "name": "this is a test vote",
    "desc": "this is a test description for a test vote",
    "question": {
        "desc": "this is a test description for a test question",
        "options": {
            "option0": {
                "number": 1,
                "option": "this is a test option"
            },
            "option1": {
                "number": 2,
                "option": "this is another test option"
            },
            "option2": {
                "number": 3,
                "option": "this is a third test option"
            },
            "option3": {
                "number": 4,
                "option": "this is a fourth test option"
            }
        }
    },
    "start_date": "2021-01-01",
    "end_date": "2021-01-02"
}

@bot.command(name='get-poll', help='Gets a poll from ID')
async def get_poll(ctx, poll_id: int):
    print(f'poll_id: {poll_id}')
    #queryset = Voting.objects.all()
    embed = discord.Embed(title=f'{test_voting["name"]}', 
        description=f'{test_voting["desc"]}', color=discord.Color.random())

    embed.add_field(name=f'{test_voting["question"]["desc"]}', value="᲼᲼", inline=False)

    for option in test_voting["question"]["options"]:
        embed.add_field(name=f'{test_voting["question"]["options"][option]["number"]}', 
                        value=f'{test_voting["question"]["options"][option]["option"]}', 
                        inline=False)


    await ctx.send(embed=embed)
    

bot.run(TOKEN)