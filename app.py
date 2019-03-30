# Work with Python 3.6
import discord
import time
import datetime
import asyncio
from ctypes.util import find_library
import pyttsx3
import os

# Inspired by ThiefGMS and his insight/mp3 files into the Verus Hilla fight
# 16s from start to hourglass timer (29:44)
# first interval 150s (27:14)
# when HP hits 20% on the second HP bar, interval becomes 125s
# when HP hits 20% on the third HP bar, interval becomes 100s
# Additional feature to be added:
# - Add a input of current clock time for soul split
#    - This is especially helpful after a phase change

'''
Current bugs: 
If a command (that calls bot_speak) is used while the bot is currently talking, the bot will crash with segfault.
This is due to libopus, most likely happening in bot_speak() with the ffmpeg player.

The create_ffmpeg_player is in a new thread every time it is called to play an mp3 track, so I cannot figure out
how to make the previous thread's ffmpeg player stop if a new audio request is started.

In other words, if the bot is already speaking and is asked to speak something else, it will crash.

https://discordpy.readthedocs.io/en/latest/api.html#discord.VoiceClient.create_ffmpeg_player
"Creates a stream player for ffmpeg that launches in a separate thread to play audio."
'''

# client == bot
client = discord.Client()

# then try finding the secret_key.txt file for the key (for local deployments)
token_file = open('secret_key.txt', 'r')
TOKEN = token_file.read() # make a file called secret_key.txt and replace with key
TOKEN = TOKEN.rstrip()

# open and load OPUS library for voice chat support and transcoding
opuslib = find_library('opus') # Linux-based function
discord.opus.load_opus(opuslib)

# free TTS engine for Python e-Speak (on Linux) for "soul split at xx:xx"
engine = pyttsx3.init()
engine.setProperty('rate', 100)
engine.setProperty('volume', 1)

# keep track of 15s, 30s, and 60s
phase = 0

# dicts holding various information, key is vc.server.id (unique to each server)
ffmpeg_players = {}
phases = {}
vcs = {}

@client.event
async def on_ready():
    '''
    Is run when program is run, to connect bot with Discord server specified in Developer's Portal API
    Bot needs to be authorized properly and initialized
    '''
    log('Logged in as')
    log(client.user.name)
    log(client.user.id)
    log('------')

async def timer(vc, interval, boss_time):
    global phases
    while True:
        # boss_time first starts at 1784 seconds, or 29:44
        log('timer has started at boss time: ' + str(seconds_to_minutes_and_seconds(boss_time)))
        
        # text to speech
        # 60s
        log('Starting {} timer on {} server.'.format(interval, vc.server.id))
        await asyncio.sleep(interval - 60)
        bot_speak(vc, 'a60seconds.mp3')
        
        # 30s
        await asyncio.sleep(30)
        bot_speak(vc, 'a30seconds.mp3')
        
        # 15s    
        await asyncio.sleep(15)
        bot_speak(vc, 'a15seconds.mp3')
        
        # 5s
        await asyncio.sleep(10)
        bot_speak(vc, 'a5seconds.mp3')
        
        # 0s
        await asyncio.sleep(5)
        
        # update internal representation of boss clock
        boss_time -= interval
        mins_and_secs = seconds_to_minutes_and_seconds(boss_time)
        
        # generate wav file to say "soul split at xx:xx"
        # unfortunately, this uses a really creepy low voice, but I really can't find
        # anything better for free. Google TTS is amazing, but requires real $$$
        soul_split_at_xx_xx = '\"soul. split. at. ' + mins_and_secs + '"'
        generate_speech_wav(soul_split_at_xx_xx)
        bot_speak(vc, 'soulsplit.wav')
        
        # if phase changed, start timer again with less time
        if phases[vc.server.id] == 2:
            await timer(vc, 125, boss_time)
            break # so previous thread of timer stops and returns
        elif phases[vc.server.id] == 3:
            await timer(vc, 100, boss_time)
            break

# responding to an external user message
@client.event
async def on_message(message):
    global phases
    # message sender's parameters
    author = message.author
    channel = message.channel
    server = message.server
    call = author.voice.voice_channel # author's current voice channel

    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

#    if message.content.startswith('!hello'):
#        msg = 'Hello {0.author.mention}'.format(message)
#        await client.send_message(message.channel, msg)

    if message.content.startswith('!help'):
        msg = 'Please do not use a command while the bot is speaking. It will crash.'
        msg += '\nCommands include:'
        msg += '\n     !2 for phase 2 (use after 1.75 HP bars have depleted)'
        msg += '\n     !3 for phase 3 (use after 2.75 HP bars have depleted)'
        msg += '\n     !stop to disconnect the bot.'
        await client.send_message(message.channel, msg)
        
    if message.content.startswith('!start'):
        # Joins the voice chat of the person who used the command
        if not client.is_voice_connected(server):
            # if the bot is not already in a channel
            if call != None:
                # if author is in a VC, join and send ACK
                vc = await client.join_voice_channel(call)
                msg = 'Verus Hilla timer started. Bot has joined VC'
#                msg += '\nPlease do not use a command while the bot is speaking. It will crash.'
                msg += '\nCommands include:'
                msg += '\n     !2 for phase 2 (use after 1.75 HP bars have depleted)'
                msg += '\n     !3 for phase 3 (use after 2.75 HP bars have depleted)'
                msg += '\n     !stop to disconnect the bot.'
                await client.send_message(message.channel, msg)

                # play the start.mp3 file, which says "hilla fight starting, good luck"
                bot_speak(vc, 'start.mp3')
                
                # wait for 16s after entry to skip opening cutscene, as the announcement is being made
                await asyncio.sleep(16)
                msg = 'Fight has started. Starting first hourglass timer for 150s.'
                await client.send_message(message.channel, msg)
                
                phases[vc.server.id] = 1
                await timer(vc, 150, 1634) # start timer at 29:44 in boss
            else:
                # if author is not in VC, don't join and ask author to please join
                msg = 'Please join a voice channel first and re-use the command for bot to join.'
                await client.send_message(message.channel, msg)
        else:
            msg = 'Verus Hilla Bot is already in a voice channel.'
            await client.send_message(message.channel, msg)

        log('!start called by ' + str(author) + ' has finished executing')

    # this should only be used at 2.2 bars left
    if message.content.startswith('!2'):
        if client.is_voice_connected(server):
            # bot's currently voice channel
            vc = find_bot_voice_client(server.id)
            phases[vc.server.id] = 2
            bot_speak(vc, '125.mp3') # say interval is now 125s
            msg = 'Split interval now 125 seconds. Will start after next soul split.'
        else:
            # bot is not in a VC
            msg = 'Bot is not currently in a voice chat'

        await client.send_message(message.channel, msg)
        log('!2 called by ' + str(author) + ' has finished executing')

    # this should only be used at 1.2 bars left
    if message.content.startswith('!3'):
        if client.is_voice_connected(server):
            # bot's currently voice channel
            vc = find_bot_voice_client(server.id)
            phases[vc.server.id] = 3
            bot_speak(vc, '100.mp3') # say interval is now 125s
            msg = 'Split interval now 100 seconds. Will start after next soul split.'
        else:
            # bot is not in a VC
            msg = 'Bot is not currently in a voice chat'

        await client.send_message(message.channel, msg)
        log('!3 called by ' + str(author) + ' has finished executing')

    # disconnect from server
    if message.content.startswith('!stop'):
        vc = find_bot_voice_client(server.id)
        await vc.disconnect()
        msg = 'Disconnected from {} server'.format(vc.server)
        await client.send_message(message.channel, msg)

def find_bot_voice_client(server_id):
    # updates the vcs list w/ current voice connections
    # returns the vc corresponding to the bot's server
    
    # update vcs dict with current vc connections iterable
    for vc in client.voice_clients:
        # add vc to vcs dict if not already there
        if vc.server.id not in vcs.keys():
            vcs[vc.server.id] = vc
            
    return vcs[server_id]
    
def seconds_to_minutes_and_seconds(seconds):
    mins = int(seconds / 60)
    secs = seconds % 60
    mins_and_secs = str(mins) + " minutes " + str(secs) + " seconds"
    return mins_and_secs

def generate_speech_wav(text):
    espeak_command = 'espeak -m ' + text
    espeak_command += ' -v mb-en1 --stdout > soulsplit.wav'
    log(espeak_command)
    os.system(espeak_command) # generates soulsplit.wav
    log("TTS generation of soulsplit.wav is successful")
    
def bot_speak(vc, mp3_name):
    player = vc.create_ffmpeg_player(mp3_name, after=lambda: log('speech is done'))
    player.start()

def log(line):
    dateStr = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    print('[' + dateStr + '] ' + line)

def bot_speak(vc, mp3_name):
    # retain a mapping of voice sessions to players
    # if a session has a voice line in progress, stop and terminate it before playing the next one
    global ffmpeg_players # so dictionaries can always be accessed, even by async calls

    if not vc.is_connected:
        return

    if vc.server.id in ffmpeg_players:
        log('stopped {}'.format(vc.server.id))
        ffmpeg_players[vc.server.id].stop()
        ffmpeg_players.pop(vc.server.id, None)

    log('playing {} in {}'.format(mp3_name, vc.server.id))
    ffmpeg_players[vc.server.id] = vc.create_ffmpeg_player(mp3_name, after=lambda: log('speech is done'))
    ffmpeg_players[vc.server.id].start()
    
client.run(TOKEN)
