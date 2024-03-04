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

# this not work
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member):
    
    await user.kick()
    await ctx.send(f"Kicked user {user}")

# this do work
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick2(ctx, user: discord.Member, *, reason: str):
    if reason is None:
        await user.kick()
        await ctx.send(f"**{user}** has been kicked for **no reason**.")
    else:
        await user.kick(reason=reason)
        await ctx.send(f"**{user}** has been kicked for **{reason}**.")

# insert commands here

bot.run('MTIxMjUzNjc1NDIzODc4MzUyOA.GY4SF-.6j-EfrpZTkEWyejBKbm-tNAoJsDG23hAbKpvrE')

