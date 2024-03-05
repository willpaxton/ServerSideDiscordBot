import discord
from discord.ext import commands

filtered_words = []

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
async def kick(ctx, user: discord.Member, *, reason: str):
    print(reason)
    await user.kick(reason=reason)
    await ctx.send(f"Kicked user {user}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def ban(ctx, user: discord.Member, *, reason: str):
    try:
        print(reason)
        if reason == ".":
            await user.ban(reason="No reason specified")
        else:
            await user.ban(reason=reason)
        await ctx.send(f"Kicked user {user}")
    except:
        await ctx.send("Please provide a reason.")


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



@bot.command()
async def add_filter_word(ctx, arg):
    filtered_words.append(arg)
    await ctx.send(f"Added the word or phrase {arg} to the filter list")
    
@bot.command()
async def check_filter_word(ctx):
    # filtered_words.add(arg)
    filteredwords = ""


    for x in filtered_words:
        filteredwords += f"{x}\n"

    await ctx.send(filteredwords)


# this is a very bandaid solution
@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"An error occured: {str(error)}")
# insert commands here

# ctx is <discord.ext.commands.context.Context object at 0x00000257BFB1D780>

# @bot.event
# async def on_message(ctx):
#     print(ctx.content)
#     await discord.message.channel.send("lol")
    



@bot.event  
async def on_message(message):
    # iterate over list of "banned" words here

    print(f"{message.content}, {message.author}")
    message_words = str(message.content).split()
    for x in filtered_words:
        if x in message_words:
            admin = False
            for y in message.author.roles:
                if y.name == "Generic Bo<T>":
                    admin = True
            if not admin:
                await message.delete()
            
        # delete message here
        

    await bot.process_commands(message)


bot.run('MTIxMjUzNjc1NDIzODc4MzUyOA.GY4SF-.6j-EfrpZTkEWyejBKbm-tNAoJsDG23hAbKpvrE')

