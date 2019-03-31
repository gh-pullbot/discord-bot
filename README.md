[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

[![contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/dwyl/esta/issues)
[![Requirements Status](https://requires.io/github/CodeSammich/discord-bot/requirements.svg?branch=master)](https://requires.io/github/CodeSammich/discord-bot/requirements/?branch=master)
[![HitCount](http://hits.dwyl.io/codesammich/discord-bot.svg)](http://hits.dwyl.io/codesammich/discord-bot)

# discord-bot
Discord Bot for Time Keeping in MapleStory

This bot's timer is tuned for the Verus/True Hilla boss fight.

It can be deployed on up to as many servers per host as Discord allows per application in the [Discord Developer Portal](https://discordapp.com/developers/applications/).

**Special Thanks:**
- **[ThiefGMS](https://www.youtube.com/channel/UCzCehIR4x1NHz67pOLsODmw)** for his mp3 files and insight into the Verus Hilla fight, as well as the inspiration for this project!
- **[MapleStory.gg](https://maplestory.gg/)** for being the first to test and work with me
- **catboy#7193** for cracking the concurrency and scalability problems

**Boss Timer Mechanics:**
- 16s from start to hourglass timer (29:44)
- First interval 150s (27:14, etc.)
- When HP hits 25% on the second HP bar, interval becomes 125s  (requires !2 input from the player)
- When HP hits 20% on the third HP bar, interval becomes 100s   (requires !3 input from the player)

**NOTE:**
This bot may not always be 100% accurate to the real fight due to unresolvable latency issues with both the Nexon and Discord servers. There may be a variance of 0-5s from actual game.

# Usage
**Commands include:**

`!start` to start timer and allow bot to enter user's voice channel

`!2` for phase 2 (use after 1.75 HP bars have depleted)

`!3` for phase 3 (use after 2.75 HP bars have depleted)

`!stop` to disconnect the bot.

# Installation / Deployment
[Unfortunately, Discord Voice Chat does not work with free web servers like Heroku](https://stackoverflow.com/questions/53074580/discord-py-opus-heroku-issues) 

You must either deploy **locally** or on a **paid cloud server** (e.g. AWS, DigitalOcean).

## For Local Windows Use
You must install Ubuntu 18.04 via the Windows Store. Once installed, run, and you will be asked to enter a new UNIX username and password. Make sure to type accurately and carefully. You will not be able to see your password when typing it.

Continue onto the following section once you are done.

## Deployment for Ubuntu 18.04
**Strongly suggested to use Python 3.6.7.**

Currently, the only tested platform is **Ubuntu 18.04**. Other Linux distributions may work as well.

To install, run the following commands. You will be asked for your password many times:

**NOTE:** For Linux beginners: `Do you want to continue? [Y/n]`, just type `y` and press `ENTER`.

**1) Update apt:**

> sudo add-apt-repository universe

> sudo apt update

**2) Install Python 3.6.7, Pip3, [Espeak](http://espeak.sourceforge.net/), and [FFMPEG](https://linuxize.com/post/how-to-install-ffmpeg-on-ubuntu-18-04/):**

> sudo apt install python3-pip

> sudo apt install espeak

> sudo apt install ffmpeg

**3) Clone this repository and install required Pip packages:**

> git clone https://github.com/CodeSammich/discord-bot

> cd discord-bot

> pip3 install -r `requirements.txt`

**4) [Install libopus](http://ubuntuhandbook.org/index.php/2017/06/install-opus-1-2-audio-library-in-ubuntu-16-04-14-04/):**
> sudo add-apt-repository ppa:jonathonf/ffmpeg-3

> sudo apt update

> sudo apt install libopus0 opus-tools

**5) Create a file for the Discord bot secret key:**

> touch secret_key.txt

**6) Go to the [Discord Developer Portal](https://discordapp.com/developers/applications/) and create a project.**
**Under the `Bot` section, create a bot and copy the Token by clicking `Copy`.**

**Then, right click on the Ubuntu window to paste into the command line (where "key" is, no "" quotes):**
  
> echo "key" >> secret_key.txt

**MAKE SURE THE KEY IS CORRECT, OTHERWISE THE BOT WILL NOT RECOGNIZE YOUR DISCORD SERVER.**

**7) Before running the bot, please make sure to follow this link and approve the bot's entry to your Discord server. Replace CID with your [client id located here](http://prntscr.com/n4z8ts)**

https://discordapp.com/api/oauth2/authorize?client_id=CID&permissions=36707584&scope=bot

**8) Finally, to run the bot:**

> python3 app.py

**You should see a message [like this](http://prntscr.com/n4yrzt)**

NOTE: From what I understand, the bot needs to be properly approved via the OAuth2 link BEFORE running on the server. I am not sure about this. 

# Known Bugs
Multiple initial starting messages may appear if !start is used after !stop in under 16 seconds. This is due to `asyncio.sleep(16)` in `!start`. This is not a critical bug and does not affect the performance of the timer. 

# To Do
## Possible Future Features:
 - Allow input of current clock time for soul split
    - Helpful in the event of player error, especially during a phase change
    
## Resolved 3/30/19:
**Concurrency Application and Scalability Limitations**
Find ways to lessen the number of "Applications" under Discord Dev Portal and use fewer number of keys. Current implementation is one application/key per server, and the OAuth2 permission toggling is unclear.

Possible research directions on how to further scale bot: Pink Bean, NightBot, MEE6, Carl-bot

https://discordapp.com/developers/docs/topics/oauth2#bots

## Resolved 3/30/19:
**LibOpus Crash**
Using a command, which triggers another OPUS MP3 playback, when bot is already speaking will crash the bot

This is due to libopus, most likely happening in bot_speak() with the ffmpeg player.

The create_ffmpeg_player is in a new thread every time it is called to play an mp3 track, so I cannot figure out
how to make the previous thread's ffmpeg player stop if a new audio request is started.

In other words, if the bot is already speaking and is asked to speak something else, it will crash.

["Creates a stream player for ffmpeg that launches in a separate thread to play audio."](https://discordpy.readthedocs.io/en/latest/api.html#discord.VoiceClient.create_ffmpeg_player)
