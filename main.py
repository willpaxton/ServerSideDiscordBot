import json
import datetime
import discord

from discord.ext import commands, tasks
#added json and datetime imports
import sqlite3
from dotenv import dotenv_values


secrets = dotenv_values(".env")

import asyncio

con = sqlite3.connect("db.db")
cur = con.cursor()

filtered_words = []


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
async def kick(ctx, user: discord.Member, *, reason: str = None):
    print(reason)
    if reason is None:
        await user.kick(reason="No reason specified")
    else:
        await user.kick(reason=reason)
    await ctx.send(f"Kicked user {user}")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.Member, reason: str):
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
@commands.has_permissions(manage_messages=True)
async def add_filter_word(ctx, arg):
    filtered_words.append(arg)
    await ctx.send(f"Added the word or phrase {arg} to the filter list")
    
@bot.command()
@commands.has_permissions(manage_messages=True)
async def check_filter_word(ctx):
    # filtered_words.add(arg)
    filteredwords = ""


    for x in filtered_words:
        filteredwords += f"{x}\n"

    await ctx.send(filteredwords)

@bot.command()
@commands.has_permissions(manage_roles=True)
async def create_reaction_role_message(ctx, arg1, arg2):
    # arg1 should be a "title"

    message = await ctx.send(f"[{arg1}] {arg2}")
    # ctx.guild.id
    # ctx.channel.id
    # ctx.message.id

    cur.execute(f"""
    INSERT INTO REGISTERED_MESSAGES (GuildID, ChannelID, MessageID, Title) VALUES (
        {int(ctx.guild.id)},{int(ctx.channel.id)},{int(message.id)},"{arg1}"
    )""")
    con.commit()

@bot.command()
@commands.has_permissions(manage_roles=True)
async def register_reaction_role(ctx, arg1, arg2, arg3):
    # arg1 is message to register
    # arg2 is emoji
    # arg3 is role
    res = cur.execute(f"""SELECT MessageID FROM REGISTERED_MESSAGES WHERE
        (GuildID = {int(ctx.guild.id)} AND ChannelID = {int(ctx.channel.id)} AND Title='{arg1}');""")
    results = res.fetchall()
    message_id = int(results[0][0])

    channel_obj = bot.get_channel(ctx.channel.id)

    original = await channel_obj.fetch_message(message_id)

    await original.add_reaction(str(arg2))



    cur.execute(f"""
    INSERT INTO REGISTERED_REACTIONS (Reaction, RoleID, GuildID, ChannelID, Title) VALUES (
        '{str(arg2)}',{int(arg3.replace("<", "").replace(">", "").replace("@", "").replace("&", ""))},{int(ctx.guild.id)},{int(ctx.channel.id)},'{arg1}'
    )""")
    con.commit()

    await ctx.send(f"Associated {arg2} with {arg1}" )

# purges every message in a channel that is not a registered role message
@bot.command()
@commands.has_permissions(administrator=True)
async def role_channel_purge(ctx):
    messages = [message async for message in ctx.channel.history()]
    res = cur.execute(f"SELECT MessageID FROM REGISTERED_MESSAGES")
    results = res.fetchall()

    safe_messages = []
    for x in results:
        safe_messages.append(x[0])

    for y in messages:
        delete = True
        for z in safe_messages:
            if y.id == z:
                delete = False
        if delete:
            await asyncio.sleep(1)
            await y.delete()




# this is a very bandaid solution
@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"An error occured: {str(error)}")
# insert commands here
    


##################################  event storer ####################################


# event storage
events_file = 'events.json'

# load existing events
try:
    with open(events_file, 'r') as file:
        events = json.load(file)
except FileNotFoundError:
    events = []


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    daily_reminder.start()

daily_reminder_enabled = True

#will send event list to whichever channel
@tasks.loop(hours=24)  #works with minutes=1, can be set to anything i think
async def daily_reminder():
    if daily_reminder_enabled:
        # send a message to the server with all events
        if events:
            channel_id = 1214443284131217508
            channel = bot.get_channel(channel_id)
            await channel.send("All Events:\n" + ', '.join([f"{event['description']} on {event['date']}" for event in events]))
        else:
            print("No events available.")
    else:
        print("Daily reminder is currently disabled.")


# use !toggledailyreminder to set daily reminder on or off
@bot.command(name='toggledailyreminder')
async def toggle_daily_reminder(ctx):
    global daily_reminder_enabled
    daily_reminder_enabled = not daily_reminder_enabled
    await ctx.send(f"Daily reminder is {'enabled' if daily_reminder_enabled else 'disabled'}.")


#add event, needs to follow the format to work
@bot.command(name='addevent')
async def add_event(ctx, date, event_description):
    global events

    #        "!addevent <date> <event_description>",  use underscores for desc
    new_event = {'date': date, 'description': event_description}
    events.append(new_event)

    # Save events to the file
    with open(events_file, 'w') as file:
        json.dump(events, file, indent=2)

    await ctx.send(f'Event added: {date} - {event_description}')

#select and display an event based on it's index
@bot.command(name='eventselect')
async def announce_event(ctx, index: int):
    global events

    try:
        event = events[index]
        await ctx.send(f'Announcing Event: {event["date"]} - {event["description"]}')
    except IndexError:
        await ctx.send('Invalid event index. Use !listevents to see available events.')

#returns all stored events
@bot.command(name='listevents')
async def list_events(ctx):
    global events

    if not events:
        await ctx.send('No events found.')
        return

    events_list = '\n'.join([f'{index}. {event["date"]} - {event["description"]}' for index, event in enumerate(events)])
    await ctx.send(f'**Events:**\n{events_list}')




###################################### LFG maker ##########################################
    

@bot.command(name='createlfg')
async def create_lfg_channel(ctx, *, status=None):
    guild = ctx.guild

    # check if an LFG channel already exists
    lfg_channel = discord.utils.get(guild.voice_channels, name='LFG')
    if lfg_channel:
        await ctx.send("An LFG voice channel already exists.")
    else:
        # Make a new voice channel
        category = discord.utils.get(guild.categories, name='LFG Channels')
        if not category:
            category = await guild.create_category('LFG Channels')

        # discord keeps rejecting the status as not allowed, but still creates the channel
            #tried with words like 'life' and 'stuff' but it still flags, research inconclusive 
        if status:
            lfg_channel = await category.create_voice_channel(name='LFG', user_limit=0, bitrate=64000)
            await lfg_channel.edit(topic=status)
            await ctx.send(f"New LFG voice channel created with status: {status}")
        else:
            lfg_channel = await category.create_voice_channel(name='LFG', user_limit=0, bitrate=64000)
            await ctx.send("New LFG voice channel created.")



@bot.command(name='deletelfg')
async def delete_lfg_channel(ctx):
    guild = ctx.guild

    # Check if an LFG channel exists
    lfg_channel = discord.utils.get(guild.voice_channels, name='LFG')
    if lfg_channel:
        await lfg_channel.delete()
        await ctx.send("LFG voice channel deleted.")
    else:
        await ctx.send("No LFG voice channel found.")

#this is redundant since users can just click to join the channel, couldn't get this one working
@bot.command(name='joinlfg')
async def join_lfg_channel(ctx):
    guild = ctx.guild
    lfg_channel = discord.utils.get(guild.voice_channels, name='LFG')

    if lfg_channel:
        await ctx.author.move_to(lfg_channel)
        await ctx.send(f"You have joined the LFG channel: {lfg_channel.mention}")
    else:
        await ctx.send("No LFG voice channel found.")


#same for this, but the cmd still works 
@bot.command(name='leavelfg')
async def leave_lfg_channel(ctx):
    current_channel = ctx.author.voice.channel

    if current_channel:
        await ctx.author.move_to(None)
        await ctx.send("You have left the current voice channel.")
    else:
        await ctx.send("You are not in a voice channel.")




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
        
        await message.channel.purge(limit = 1)
        await message.channel.send(msg)
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    print(payload)
    res = cur.execute(f"""SELECT Title FROM REGISTERED_MESSAGES WHERE
        (GuildID = {int(payload.guild_id)} AND ChannelID = {int(payload.channel_id)} AND MessageID = {int(payload.message_id)});""")
    results = res.fetchall()
    
    try:
        title = results[0][0]
        res = cur.execute(f"""SELECT RoleID FROM REGISTERED_REACTIONS WHERE
        (GuildID = {int(payload.guild_id)} AND ChannelID = {int(payload.channel_id)} AND Title = '{title}');""")
        results = res.fetchall()
        try:
            roleID = results[0][0]
            current_guild = bot.get_guild(int(payload.guild_id))
            await payload.member.add_roles(current_guild.get_role(roleID))
        except:
            print("no role associated")
        # if payload.emoji.name == "🔴":
        #     print(payload)
        #     current_guild = bot.get_guild(int(payload.guild_id))
        #     await payload.member.add_roles(current_guild.get_role(1121295903886676028))
    except Exception as e:
        print(f"no roles found {e}")

    


@bot.event
async def on_raw_reaction_remove(payload):
    print(payload)
    res = cur.execute(f"""SELECT Title FROM REGISTERED_MESSAGES WHERE
        (GuildID = {int(payload.guild_id)} AND ChannelID = {int(payload.channel_id)} AND MessageID = {int(payload.message_id)});""")
    results = res.fetchall()
    
    try:
        title = results[0][0]
        res = cur.execute(f"""SELECT RoleID FROM REGISTERED_REACTIONS WHERE
        (GuildID = {int(payload.guild_id)} AND ChannelID = {int(payload.channel_id)} AND Title = '{title}');""")
        results = res.fetchall()
        try:
            roleID = results[0][0]
            current_guild = bot.get_guild(int(payload.guild_id))
            current_member = current_guild.get_member(int(payload.user_id))
            await current_member.remove_roles(current_guild.get_role(roleID))
        except Exception as e:
            print(f"no role associated {e}")
        # if payload.emoji.name == "🔴":
        #     print(payload)
        #     current_guild = bot.get_guild(int(payload.guild_id))
        #     await payload.member.add_roles(current_guild.get_role(1121295903886676028))
    except Exception as e:
        print(f"no roles found {e}")


# emoji: payload.emoji.name
# user_id: payload.user_id
# message_id: payload.message_id
# member object: payload.member
# 1118237685069393981 | 1118237685069393981


bot.run(secrets["API_KEY"])

