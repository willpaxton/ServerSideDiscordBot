import discord
from discord.ext import commands

intents = discord.Intents.default()
# Add intents here if you need them
intents.message_content = True
intents.reactions = True
intents.members = True


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
    msg = message.content
    # iterate over list of "banned" words here
    print(f"{message.content}, {message.author}")
    if "hi" in message.content:
        # delete message here
        await message.channel.purge(limit = 1)
        await message.channel.send(msg)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.emoji.name == "🔴":
        print(payload)
        current_guild = bot.get_guild(int(payload.guild_id))
        await payload.member.add_roles(current_guild.get_role(1121295903886676028))

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.emoji.name == "🔴":
        print(payload)
        current_guild = bot.get_guild(int(payload.guild_id))
        current_member = current_guild.get_member(int(payload.user_id))
        await current_member.remove_roles(current_guild.get_role(1121295903886676028))

# emoji: payload.emoji.name
# user_id: payload.user_id
# message_id: payload.message_id
# member object: payload.member
# 1118237685069393981 | 1118237685069393981


bot.run('MTIxMjUzNjc1NDIzODc4MzUyOA.GY4SF-.6j-EfrpZTkEWyejBKbm-tNAoJsDG23hAbKpvrE')

