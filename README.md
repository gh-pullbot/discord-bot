# discord-bot
Discord Bot for Time Keeping in MapleStory

# Installation / Deployment
NOTE: [Unfortunately, Discord Voice Chat does not work with free web servers like Heroku](https://stackoverflow.com/questions/53074580/discord-py-opus-heroku-issues)

## Non-Heroku Deployment for Ubuntu 18.04
Strongly suggested to use python 3.6.7.

Install packages in `requirements.txt`.

Then [install libopus](http://ubuntuhandbook.org/index.php/2017/06/install-opus-1-2-audio-library-in-ubuntu-16-04-14-04/) using:
> sudo add-apt-repository ppa:jonathonf/ffmpeg-3

> sudo apt-get update

> sudo apt-get install libopus0 opus-tools

Currently, the only tested platform is Ubuntu 18.04. Other Linux distributions may work as well.

> touch secret_key.txt

Go to the [Discord Developer Portal](https://discordapp.com/developers/applications/) and create a project.
Under the `Bot` section, create a bot and copy the Token.
Input the copied token into `secret_key.txt`.

**MAKE SURE THE KEY IS CORRECT, OTHERWISE THE BOT WILL NOT RECOGNIZE YOUR DISCORD SERVER.**

To run:
> python3 app.py

# Usage
NOTE: Please do not use a command while the bot is speaking. It will crash due to OPUS limitations with Discord.

Commands include:
!start to start timer and allow bot to enter user's voice channel
!2 for phase 2 (use after 1.75 HP bars have depleted)
!3 for phase 3 (use after 2.75 HP bars have depleted)
!stop to disconnect the bot.

# Known Bugs
## LibOpus Crash
Using a command, which triggers another OPUS MP3 playback, when bot is already speaking will crash the bot

This is due to libopus, most likely happening in bot_speak() with the ffmpeg player.

The create_ffmpeg_player is in a new thread every time it is called to play an mp3 track, so I cannot figure out
how to make the previous thread's ffmpeg player stop if a new audio request is started.

In other words, if the bot is already speaking and is asked to speak something else, it will crash.

https://discordpy.readthedocs.io/en/latest/api.html#discord.VoiceClient.create_ffmpeg_player
"Creates a stream player for ffmpeg that launches in a separate thread to play audio."
