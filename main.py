# This example requires the 'message_content' intent.

import discord
from discord.ext import commands

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')


    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def test(ctx, arg):
    await ctx.send(arg)

@bot.command()
async def helloworld(ctx):
    await ctx.send("Hello, World! :D")

@bot.command()
async def ping(ctx):
    await ctx.send("pong")    

client = MyClient(intents=intents)

bot.run('MTIxMjUzNjc1NDIzODc4MzUyOA.GY4SF-.6j-EfrpZTkEWyejBKbm-tNAoJsDG23hAbKpvrE')

