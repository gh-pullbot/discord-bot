# Inspired by ThiefGMS and his insight/mp3 files into the Verus Hilla fight
# Special Thanks to MapleStory.gg and catboy on Discord for their contributions and initial hosting!
#
# Boss Timer Mechanics:
#     16s from start to hourglass timer (29:44)
#     First interval 150s (27:14, etc.)
#     When HP hits 25% on the second HP bar, interval becomes 125s
#     When HP hits 20% on the third HP bar, interval becomes 100s
#
# Possible Future Features:
# - Allow input of current clock time for soul split
#    - This is especially helpful after a phase change
#
# NOTE:
# This bot may not always be 100% accurate to the real fight due to unresolvable latency issues
# with both the Nexon and Discord servers. There may be a variance of 0-5s from actual game.

# Work with Python 3.6
import discord
import time
import datetime
import asyncio
from ctypes.util import find_library
import pyttsx3
import os

# client being run on the Discord servers for guilds (colloquially "servers") to connect to
client = discord.Client()

# then try finding the secret_key.txt file for the key (for local deployments)
with open('secret_key.txt', 'r') as token_file:
    TOKEN = token_file.read()
    TOKEN = TOKEN.rstrip()

# open and load OPUS library for voice chat support and transcoding
opuslib = find_library('opus')  # Linux-based function
discord.opus.load_opus(opuslib)

# Concurrent Server Data Structures
# global dicts w/ information for each bot instance in each server/guild (Discord's term for server)
# keys are: vc.server.id (unique per server)
# audio currently playing, prevents overlapping audio (see bot_speak)
ffmpeg_players = {}
phases = {}  # boss timer phases (150s, 125s, 100s)
# voice channels the bot is currently in, derived from client.voice_clients (see find_bot_voice_client)
vcs = {}


@client.event
async def on_ready():
    '''
    Is run when program is run, to connect bot with Discord server specified in Developer's Portal API
    Bot needs to be authorized properly and initialized on the Dev Portal.
    Once completed, servers/guilds can begin connecting to the bot.
    '''
    log('Logged in as:')
    log(client.user.name)
    log(client.user.id)
    log('------')


async def timer(vc, interval, boss_time):
    global phases
    while True:
        # boss_time first starts at 1784 seconds, or 29:44
        log('Timer has started at boss time: {} in the {} channel in {} server.'
            .format(short_minutes_and_seconds(boss_time + interval), vc.channel, vc.server))

        # text to speech
        # 60s warning
        log('Starting {}s timer on the {} channel in {} server.'
            .format(interval, vc.channel, vc.server))
        await asyncio.sleep(interval - 60)
        if phases[vc.server.id] == 0:
            # if bot disconnected while sleeping, stop the thread
            break

        bot_speak(vc, 'audio/a60seconds.ogg')

        # 30s warning
        await asyncio.sleep(30)
        if phases[vc.server.id] == 0:
            # if bot disconnected while sleeping, stop the thread
            break

        bot_speak(vc, 'audio/a30seconds.ogg')

        # 15s warning
        await asyncio.sleep(15)
        if phases[vc.server.id] == 0:
            # if bot disconnected while sleeping, stop the thread
            break

        bot_speak(vc, 'audio/a15seconds.ogg')

        # 5s warning
        await asyncio.sleep(10)
        if phases[vc.server.id] == 0:
            # if bot disconnected while sleeping, stop the thread
            break

        bot_speak(vc, 'audio/a5seconds.ogg')

        # 0s soul split announcement
        await asyncio.sleep(5)
        if phases[vc.server.id] == 0:
            # if bot disconnected while sleeping, stop the thread
            break

        # update internal representation of boss clock
        mins_and_secs = minutes_and_seconds(boss_time)

        # generate an ogg vorbis file generate wav file to say "soul split at xx:xx"
        generate_next_split_audio(vc, mins_and_secs.split(' '))
        bot_speak(vc, "./tmp/output_{}.ogg".format(vc.server.id))

        # if phase changed, start timer again with less time
        if phases[vc.server.id] == 1:
            await timer(vc, 150, boss_time - 150)
            break
        if phases[vc.server.id] == 2:
            await timer(vc, 125, boss_time - 125)
            break  # so previous thread of timer stops and returns
        elif phases[vc.server.id] == 3:
            await timer(vc, 100, boss_time - 100)
            break

# responding to an external user message
@client.event
async def on_message(message):
    # so the dicts can always be accessed, even by async calls
    global phases
    global vcs

    # message sender's parameters
    author = message.author  # or sender
    channel = message.channel
    server = message.server
    call = author.voice.voice_channel  # author's current voice channel

    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!help'):
        # !help command, including usage tips
        msg = '\nCommands include:'
        msg += '\n     !start makes bot join voice chat (use upon entering)'
        msg += '\n     !2 for phase 2 (use after 1.75 HP bars have depleted)'
        msg += '\n     !3 for phase 3 (use after 2.75 HP bars have depleted)'
        msg += '\n     !stop to disconnect the bot.'
        await client.send_message(message.channel, msg)

    if message.content.startswith('!start') or message.content.startswith('!join') or message.content.startswith('!fight'):
        # Joins the voice chat of the person who used the command
        if not client.is_voice_connected(server):
            # if the bot is not in a voice channel yet
            if call != None:
                # if sender is in a voice channel, join the vc
                try:
                    vc = await client.join_voice_channel(call)

                    # tell the party the timer has begun in the chat
                    msg = 'Verus Hilla timer has started in the {} channel.'.format(
                        vc.channel)
                    await client.send_message(message.channel, msg)

                    # (re-)initialize the phase/vc for that server
                    phases[vc.server.id] = 1
                    vcs[vc.server.id] = vc

                    # play the start.ogg file, which says "hilla fight starting, good luck"
                    bot_speak(vc, 'audio/start.ogg')

                    # wait for 16s after entry to skip opening cutscene, as the announcement is being made
                    await asyncio.sleep(16)

                    if phases[vc.server.id] != 0:
                        # if bot did not disconnect during sleep
                        # tell the party the fight has started in chat
                        # Bot may send this message multiple times if it is restarted before 16s sleep is over
                        # Does not influence timer or voice chat, they're just ghost threads that will die
                        # once !stop is calling again.
                        msg = 'Fight has started. Starting first 150s timer.'
                        msg += '\nIf you see this message multiple times, ignore it.'
                        await client.send_message(message.channel, msg)

                        await timer(vc, 150, 1634)  # start timer 150s at 29:4
                except asyncio.TimeoutError:
                    msg = 'Cannot connect to voice channel, request timed out. Try checking your channel/bot permissions.'
                    await client.send_message(message.channel, msg)
            else:
                # if sender is not in VC, don't join and ask the sender to please join
                msg = 'Please join a voice channel first and re-use the command for bot to join.'
                await client.send_message(message.channel, msg)
        else:
            msg = 'Verus Hilla Bot is already in a voice channel.'
            await client.send_message(message.channel, msg)

        log('!start called by {} on {} server has finished executing'.format(
            author, server))

    # this should only be used at 2.2 bars left
    if message.content.startswith('!2'):
        if client.is_voice_connected(server):
            # if bot is in a vc, find it
            vc = find_bot_voice_client(server.id)

            if author.server_permissions.administrator or author_in_vc(author, vc):
                # if the author is an admin or is in the vc with the bot
                # set the phase for sender's server
                phases[vc.server.id] = 2
                # say interval is now 125s
                bot_speak(vc, 'audio/hourglass_updated_125.ogg')
                msg = 'Split interval now 125 seconds. Will start after next soul split.'
            else:
                msg = 'You are not in the voice chat or an administrator.'
        else:
            # bot is not in a VC
            msg = 'Bot is not currently in a voice chat'

        await client.send_message(message.channel, msg)
        log('!2 called by {} on {} server has finished.'.format(author, server))

    # this should only be used at 1.2 bars left
    if message.content.startswith('!3'):
        if client.is_voice_connected(server):     # if bot is in a vc
            vc = find_bot_voice_client(server.id)  # find the vc

            if author.server_permissions.administrator or author_in_vc(author, vc):
                # if the author is an admin or is in the vc with the bot
                # set the phase for sender's server
                phases[vc.server.id] = 3
                # say interval is now 100s
                bot_speak(vc, 'audio/hourglass_updated_100.ogg')
                msg = 'Split interval now 100 seconds. Will start after next soul split.'
            else:
                msg = 'You are not in the voice chat or an administrator.'
        else:
            # if bot is not in a vc
            msg = 'Bot is not in a voice chat'

        # respond to the sender
        await client.send_message(message.channel, msg)
        log('!3 called by {} on {} server has finished.'.format(author, server))

    # disconnect from server
    if message.content.startswith('!stop') or message.content.startswith('!leave'):
        # find the voice chat corresponding to the message and disconnect
        if client.is_voice_connected(server):     # if bot is in a vc
            vc = find_bot_voice_client(server.id)  # find the vc

#            if author.server_permissions.administrator or author_in_vc(author, vc):
            if author_in_vc(author, vc):
                # if the author is an admin or is in the vc with the bot
                await vc.disconnect()                 # disconnect from voice channel
                phases[vc.server.id] = 0
                # delete the voice channel from dict
                del vcs[vc.server.id]
                msg = 'Disconnected from {}.'.format(vc.channel)
            else:
                msg = 'You are not in the voice chat or an administrator.'
        else:
            msg = 'Bot is not in a voice chat.'

        # respond to the sender
        await client.send_message(message.channel, msg)
        log('!stop called by {} on {} server has finished.'.format(author, server))


def author_in_vc(author, vc):
    '''
    Is the author in the vc?

    Inputs: String author
    Returns: True/False
    '''
    for member in vc.server.members:
        #        log('{} is in the {} server. The bot is in the {} server.'.format(member, member.server, vc.channel))
        try:
            # need to compare ids and not just channel names because names are not unique
            # (e.g. two channels can have the same name)
            if member.voice.voice_channel.id == vc.channel.id:
                return True
        except AttributeError:  # NoneType object has no attribute 'id'
            # this will happen if someone outside of the vc tries to use the command
            continue

    return False


def find_bot_voice_client(server_id):
    '''
    Updates the voice chats (vcs) list with current voice connections
    and returns the voice chat in the server with server_id.

    Inputs: Unique id of Discord server/guild (vc.server.id or message.server.id)
    Returns: the voice chat object corresponding to the bot's server
    '''
    global vcs  # so the dict can always be accessed, even by async calls
    # update vcs dict with current vc connections iterable
    for vc in client.voice_clients:
        # add vc to vcs dict if not already there
        if vc.server.id not in vcs.keys():
            vcs[vc.server.id] = vc

    return vcs[server_id]


def minutes_and_seconds(seconds):
    '''
    Converts seconds to minutes and seconds (xx minutes xx seconds)

    Inputs: String seconds
    Returns: String representation with minutes and seconds
    '''
    mins = int(seconds / 60)
    secs = seconds % 60
    mins_and_secs = str(mins) + " minutes " + str(secs) + " seconds"
    return mins_and_secs


def short_minutes_and_seconds(seconds):
    '''
    Converts seconds to minutes and seconds (xx:xx format)

    This is mostly used for convenient logging.

    Inputs: String seconds
    Returns: String representation with minutes and seconds
    '''
    mins = int(seconds / 60)
    secs = seconds % 60
    mins_and_secs = str(mins) + ":" + str(secs)
    return mins_and_secs


def log(line):
    '''
    Logs date and time to the console along with input.

    Input: String line
    Output: Datetime and line printed
    '''
    date_str = datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    print('[{}] {}'.format(date_str, line))


def generate_next_split_audio(vc, time_list):
    '''
    Generate an ogg vorbis audio file containing concatenated text.
    '''
    the_rest_of_the_files = "|".join(
        ['audio/' + filename + '.ogg' for filename in time_list])
    # The concat takes the format 'concat:file1.ogg|file2.ogg|file3.ogg'
    # If file1.ogg contains 'Soul split at'
    # and file2.ogg contains '2'
    # and file3.ogg contains 'minutes'
    # .. you get the drill
    CONCAT_CMD = 'ffmpeg -y  -use_wallclock_as_timestamps 1 -i "concat:audio/soul_split_at.ogg|{}" -c copy ./tmp/output_{}.ogg'.format(
        the_rest_of_the_files, vc.server.id)
    os.system(CONCAT_CMD)


def bot_speak(vc, filename):
    '''
    Allows the bot to play audio, or speak, into the voice channel.

    Retains a mappiung of voice sessions to players.
    If a session has a voice line in progress, terminate it before playing the next one.

    Input: String filename
    Output: MP3 file played by bot in the corresponding voice channel
    '''
    global ffmpeg_players  # so the dict can always be accessed, even by async calls

    if not vc.is_connected:
        return

    # for the respective concurrent server, stop the current audio player
    if vc.server.id in ffmpeg_players:
        log('stopped {}'.format(vc.server))
        ffmpeg_players[vc.server.id].stop()
        ffmpeg_players.pop(vc.server.id, None)

    # start a new audio player for the new audio and save in the global ffmpeg_players dict for concurrency
    log('playing {} in {}'.format(filename, vc.server))
    ffmpeg_players[vc.server.id] = vc.create_ffmpeg_player(filename,
                                                           after=lambda: log('speech is done in the {} channel of {}.'.format(vc.channel, vc.server)))
    ffmpeg_players[vc.server.id].start()


# run the client and connect to Discord's servers
# this needs to run before servers/guilds can connect successfully
client.run(TOKEN)
