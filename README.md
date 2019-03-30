# discord-bot
Discord Bot for Time Keeping in MapleStory

# Installation
### Currently experimenting with Heroku deployment
Standard Heroku deployment procedures apply.

Go to the [Discord Developer Portal](https://discordapp.com/developers/applications/) and create a project.
Under the `Bot` section, create a bot and copy the Token.

In addition, under project Settings -> Config Vars, put SECRET_KEY on the left and the copied Token on the right, then save.

To install the necessary OPUS package (for mp3 creation), run:
`heroku buildpacks:set hitsounds/libopus`

NOTE: If the installation fails, find [another libopus package here](https://elements.heroku.com/search/buildpacks?q=libopus). `opus` may also work here.

Then, assuming your heroku is properly setup, run using:
`git push heroku`

### Non-Heroku Deployment for Ubuntu 18.04
Install all necessary and relevant packages on Linux server (see `requirements.txt`). 
Currently, the only tested platform is Ubuntu 18.04. Other Linux distributions may work as well.

> $touch secret_key.txt

Go to the [Discord Developer Portal](https://discordapp.com/developers/applications/) and create a project.
Under the `Bot` section, create a bot and copy the Token.
Input the copied token into `secret_key.txt`.

**MAKE SURE THE KEY IS CORRECT, OTHERWISE THE BOT WILL NOT RECOGNIZE YOUR DISCORD SERVER.**

To run:
`$python3 app.py`

# Usage
NOTE: Please do not use a command while the bot is speaking. It will crash due to OPUS limitations with Discord.

Commands include:
!start to start timer and allow bot to enter user's voice channel
!2 for phase 2 (use after 1.75 HP bars have depleted)
!3 for phase 3 (use after 2.75 HP bars have depleted)
!stop to disconnect the bot.

# Known Bugs
- Using a command, which triggers another OPUS MP3 playback, when bot is already speaking will crash the bot
