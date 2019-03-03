# Work with Python 3.6
import discord
import time
import asyncio
from ctypes.util import find_library

# Inspired by ThiefGMS and his insight/mp3 files into the Verus Hilla fight
# 16s from start to hourglass timer (29:44)
# first interval 150s (27:14)
# when HP hits 20% on the second HP bar, interval becomes 125s
# when HP hits 20% on the third HP bar, interval becomes 100s

# client == bot
client = discord.Client()

token_file = open('secret_key.txt', 'r')
TOKEN = token_file.read() # make a file called secret_key.txt and replace with key

# user == guy who calls bot, hard coded to me
me_user = discord.User()
me_user.name = "Sam (CodeNox)#6829"
me_user.id = 75954529383743488

# open and load OPUS library for voice chat support and transcoding
opuslib = find_library('opus')
discord.opus.load_opus(opuslib)

# keep track of 15s, 30s, and 60s
phase = 0
started = False

async def timer(vc, interval):
    while True:
        # text to speech
        # 60s
        print("wait for 90 seconds")
        await asyncio.sleep(interval - 60)
        bot_speak(vc, 'a60seconds.mp3')
        
        # 30s
        await asyncio.sleep(30)
        bot_speak(vc, 'a30seconds.mp3')
        
        # 15s    
        await asyncio.sleep(15)
        bot_speak(vc, 'a15seconds.mp3')
        
        # await asyncio.sleep(1)

# responding to an external user message
@client.event
async def on_message(message):
    # message sender's parameters
    author = message.author
    channel = message.channel
    server = message.server
    call = author.voice.voice_channel # author's current voice channel

    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith('!start'):
        # joins the vc, speaks to us
        print("started")
        msg = 'hilla timer started, 30 seconds between messages, joined vc'
        if not client.is_voice_connected(server):
            # if the bot is not already in a channel, join one
            vc = await client.join_voice_channel(call)

        # play the start.mp3 file, which says "hilla fight starting, good luck"
        bot_speak(vc, 'start.mp3')

        # wait for 16s after entry, as the announcement is made
        await asyncio.sleep(16)

        phase = 1
        started = True
        await client.send_message(message.channel, msg)
        await timer(vc, 150)
        print ("main is done")

    # this should only be used at 2.2 bars left
    if message.content.startswith('!2'):
        phase = 2
        if client.is_voice_connected(server):
            # bot's currently voice channel
            vc = client.user.voice.voice_channel
            msg = 'split interval now 125 seconds'
        else:
            # bot is not in a VC
            msg = 'bot is not currently in a voice chat'

        await timer(vc, 125)
        bot_speak(vc, '125.mp3') # say interval is now 125s
        await client.send_message(message.channel, msg)

    # this should only be used at 1.2 bars left
    if message.content.startswith('!3'):
        phase = 3
        if client.is_voice_connected(server):
            # bot's currently voice channel
            vc = client.user.voice.voice_channel
            msg = 'split interval now 100 seconds'
        else:
            # bot is not in a VC
            msg = 'bot is not currently in a voice chat'

        await timer(vc, 100)
        bot_speak(vc, '100.mp3') # say interval is now 100s
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

def find_user_vc():
    voice_channels = client.voice_clients
    print("voice channels: ", voice_channels)
    for vc in voice_channels:
        if vc.user == me_user:
            # found vc of Sam, join pls
            return vc

def bot_speak(vc, mp3_name):
    player = vc.create_ffmpeg_player(mp3_name, after=lambda: print('done'))
    player.start()
    

client.run(TOKEN)
