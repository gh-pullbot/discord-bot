# discord-bot
Discord Bot for Time Keeping in MapleStory

# Installation / Deployment
NOTE: [Unfortunately, Discord Voice Chat does not work with free web servers like Heroku](https://stackoverflow.com/questions/53074580/discord-py-opus-heroku-issues)

### For Local Windows Use
You must install Ubuntu 18.04 via the Windows Store. Once installed, run, and you will be asked to enter a new UNIX username and password. Make sure to type accurately and carefully. You will not be able to see your password when typing it.

Continue onto the following section once you are done.

### Deployment for Ubuntu 18.04
Currently, the only tested platform is Ubuntu 18.04. Other Linux distributions may work as well.

Strongly suggested to use Python 3.6.7.

NOTE: For Linux beginners, "Do you want to continue? [Y/n]", just type y and press ENTER.

Run the following commands. You will be asked for your password many times:
Update apt

> sudo add-apt-repository universe

> sudo apt update

Install Python 3.6.7, Pip3, and [Espeak](http://espeak.sourceforge.net/):

> sudo apt install python3-pip

> sudo apt install espeak

Clone this repository and install required Pip packages:

> git clone https://github.com/CodeSammich/discord-bot

> cd discord-bot

> pip3 install -r `requirements.txt`

[Install libopus](http://ubuntuhandbook.org/index.php/2017/06/install-opus-1-2-audio-library-in-ubuntu-16-04-14-04/):
> sudo add-apt-repository ppa:jonathonf/ffmpeg-3

> sudo apt update

> sudo apt install libopus0 opus-tools

Create a file for the Discord bot secret key

> touch secret_key.txt

Go to the [Discord Developer Portal](https://discordapp.com/developers/applications/) and create a project.
Under the `Bot` section, create a bot and copy the Token by clicking `Copy`.

Then, right click on the Ubuntu window to paste into the command line (where "key" is, no "" quotes).
  
> echo "key" >> secret_key.txt

**MAKE SURE THE KEY IS CORRECT, OTHERWISE THE BOT WILL NOT RECOGNIZE YOUR DISCORD SERVER.**

Finally, to run the bot:

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

["Creates a stream player for ffmpeg that launches in a separate thread to play audio."](https://discordpy.readthedocs.io/en/latest/api.html#discord.VoiceClient.create_ffmpeg_player)

