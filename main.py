import discord
from discord.ext import commands

intents = discord.Intents.default()
# Add intents here if you need them
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

client = discord.Client(intents=intents)

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command()
async def helloworld(ctx):
    await ctx.send("Hello, World! :D")

@bot.command()
async def ping(ctx):
    await ctx.send("pong")    

# insert commands here
########################################### WELCOME DISPLAY ##############################################
# Ready an event for when the bot joins
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Runs the welcome event, once the user joins the server
@bot.event
async def on_member_join(member):
    # Send a welcome
    await member.send(f'Welcome to the server, {member.name}!')
    
# The following code basically checks to see if the bot has the send messages bot permission in order to send the welcome display
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    # Checks out the bots permissions
    await check_permissions()

async def check_permissions():
    # Get the bot's own member object from a server
    guild = bot.get_guild(SERVER_ID) # Will need to replace SERVER_ID with our actual discord server ID (PLACEHOLDER)
    bot_member = guild.get_member(bot.user.id)

    # Check if the bot has permission to send messages
    if bot_member.guild_permissions.send_messages:
        print("Bot has permission to send messages.")
    else:
        print("Bot does not have permission to send messages.")


bot.run('MTIxMjUzNjc1NDIzODc4MzUyOA.GY4SF-.6j-EfrpZTkEWyejBKbm-tNAoJsDG23hAbKpvrE')

