# Work with Python 3.6
import discord
import time

# 16s from start to hourglass timer (29:44)
# first interval 150s (27:14)
# when HP hits 20% on the second HP bar, interval becomes 125s
# when HP hits 20% on the third HP bar, interval becomes 100s

# client == bot
client = discord.Client()

# responding to an external user message
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith('!start'):
        # joins the vc, speaks to us
        msg = '/tts hilla timer started, 30 seconds between messages'
#        vc = find_user_vc()
#        voice_client = client.join_voice_channel(vc)
#        player = vc.create_ffmpeg_player('start.mp3', after=lambda: print('done'))
#        player.start()
        await asyncio.sleep(16) # wait for 16s after entry, as the announcement is made
        phase = 1
        await client.send_message(message.channel, msg)

    # this should only be used at 2.2 bars left
    if message.content.startswith('!2'):
        phase = 2
        msg = '/tts split interval now 125 seconds'
        await client.send_message(message.channel, msg)

    # this should only be used at 1.2 bars left
    if message.content.startswith('!3'):
        phase = 3
        msg = '/tts split interval now 100 seconds'
        await client.send_message(message.channel, msg)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

def find_user_vc():
    voice_channels = client.voice_clients
    for vc in voice_channels:
        if vc.user == me_user:
            # found vc of Sam, join pls
            return vc

def timer():
    now = time.localtime(time.time())
    return now[5]


    
token_file = open('secret_key.txt', 'r')
TOKEN = token_file.read() # make a file called secret_key.txt and replace with key

voice_channel = find_user_vc()

# user == guy who calls bot, hard coded to me
me_user = discord.User()
me_user.name = "Sam (CodeNox)#6829"
me_user.id = 75954529383743488

# open and load OPUS library for voice chat support and transcoding
#discord.opus.load_opus('libopus.so')

client.run(TOKEN)

# keep track of 15s, 30s, and 60s
phase = 0
while started:
    current_time = timer()
    if phase == 1:
        # boss has started in phase 1
        interval = 150
        last_split_time = current_time
    elif phase == 2:
        # boss has started in phase 2
        interval = 125
    elif phase == 3:
        # boss has started in phase 3
        interval = 100

    # text to speech
    last_split_time = timer()
    if last_split_time - current_time == 60:
        # make it say 60s
        pass
    elif last_split_time - current_time == 30:
        # 30s
        pass
    elif last_split_time - current_time == 15:
        # 15s
        pass
    
