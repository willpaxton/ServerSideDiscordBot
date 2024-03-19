import json
import datetime
import discord
from discord.ext import commands, tasks
#added json and datetime imports

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




bot.run(#insert here)

