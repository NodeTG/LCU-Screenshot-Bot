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

To use the bot, you first need to open the game, then run the bot in the background. Once the game is on the "Press any key" screen (ensure you aren't on the "New Game", "Load Game", etc. screen), you can then run the `/setup_vgamepad` command. This will spam A on the virtual gamepad in order to load a save file. This is needed in order to center the camera and open/close the communicator camera.

After around 20 A presses, the bot will upload a screenshot of the game and say that it should be loading (or have already loaded). From here, you can start taking screenshots.

`/chase_screenshot` will take a screenshot using the regular third person camera.
To use it, you must provide the X, Y and Z coordinates (by default, X and Z are limited to +/- 1000 units and Y has a minimum of 0.25 to stop Chase from drowning).
You must also provide a rotation value between -6 and 6 (any higher or lower will cause Chase to spin around like crazy).

`/camera_screenshot` will take a screenshot using the first person camera accesible via Chase's communicator.
To use it, you must provide the X, Y and Z coordinates (by default, X and Z are limited to +/- 1000 units and Y has a minimum of 0.25 to stop Chase from drowning).
You must also provide a pitch and yaw value. I'm not 100% sure on the exact range for pitch, but yaw should be between -6 and 6. Note that these values can be quite sensitive, so small differences in values can make large jumps, especially in terms of pitch.
There is also an optional zoom parameter which takes in a value from 0 to 1.37 (max theoretical zoom is 1.3636363636...). 0 is no zoom, 1 is the maximum normally available in game.

## Other Commands
There are a few other commands that exist, mainly for managing the bot.

- `/get_chase_info`: this can be used by anyone, and provides information on Chase's current XYZ and rotation.
- `/reload_addrs`: this is redundant now that it is called every time a screenshot is taken, but it ensures that functions are NOP'd properly and pointers are pointing to the correct location.
- `/exit`: self-explanatory, but it shuts down the bot (does not shutdown the game).

## Notes

 - This bot does not provide a way to hide the HUD. This can be achieved via custom scripts. You can use  `UI_ShowHUD(false);` and `UI_ShowPlayerHUD(false);` for this.

## Examples
Here are some examples of how the bot looks when it works (these were made before `/camera_screenshot` was implemented):

 - https://www.youtube.com/watch?v=ntEcIB6yJnU
 - https://imgur.com/a/e956cAR

