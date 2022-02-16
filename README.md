# LCU Screenshot Discord Bot
This bot is designed to take in coordinates from users on Discord then return a screenshot of LEGO City Undercover at those coordinates.

It works by having the game running on the same machine as the bot and writing over the area in memory that contains Player 1's position.

## Dependencies
This bot was written in Python 3.10, though earlier versions of Python 3 should work (at least as far back as 3.8).
The following modules should be installed in order to run this script:

 - Pycord
 - mss
 - vgamepad
 - psutil
 - pymeow

## Usage
Before running the bot, you must fill in some details in a file called `config.json`
You can see an example of this file in `example_config.json`

 - `token`: the token of the bot you wish to use (create one at https://discord.com/developers/applications)
 - `guild_id`: the ID of the server you wish to run the bot in.
 - `admin_id`: the ID of the user account that will be maintaining/hosting the bot (gives access to certain commands for managing the bot)
 - `monitor`: the monitor that the game is running on. Make sure to select the correct one, otherwise screenshots of things other than the game may appear.

Detailed instructions on how to actually use the bot will be provided at a later time, as it's likely that major changes will occur to it between me writing this and you trying to use it.

The simple version is that you need to run `/setup_vgamepad` while the game is running and you're on the title screen. This will spam A on a virtual controller used by the bot and hopefully load a save. Make sure that you are on the "Press any key" screen rather than the menu with options like "New Game", "Load Game", "Options", etc.

Once the bot is running, you can use `/take_screenshot` to, well, take a screenshot.
You should provide an X, Y, and Z coordinate, along with a rotation.
X and Z are capped at +/- 1000 units, and Y has a minimum of 0.25 to prevent people from murdering Chase in the ocean. Rotation should be a value between 6 and -6. Numbers too great or small will cause Chase to spin around like crazy.

## Notes

 - This bot does not provide a way to hide the HUD. This can be achieved via custom scripts, and I will likely release one that can be used for this purpose.

## Examples
Here are some examples of how the bot looks when it works:

 - https://www.youtube.com/watch?v=ntEcIB6yJnU
 - https://imgur.com/a/e956cAR
