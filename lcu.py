import discord
from discord.commands import Option
from discord.commands import permissions
from mss import mss
import vgamepad as vg
import random
import logging
import time
import json
import psutil
import pymeow

def read_offsets(proc, base_address, offsets):
    basepoint = pymeow.read_int64(proc, base_address)

    current_pointer = basepoint

    for i in offsets[:-1]:
        current_pointer = pymeow.read_int64(proc, current_pointer+i)
    
    return current_pointer + offsets[-1]

def reload_addrs():
    global proc, pos_base_addr, rot_base_addr, x_addr, y_addr, z_addr, rot_addr

    proc = pymeow.process_by_name("LEGOLCUR_DX11.exe")
    pos_base_addr = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x01C77C78
    rot_base_addr = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x01C74920

    gravity_address = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0xAB8B3D
    pymeow.nop_code(proc, gravity_address, 8)

    x_addr = read_offsets(proc, pos_base_addr, [0x90])
    y_addr = read_offsets(proc, pos_base_addr, [0x94])
    z_addr = read_offsets(proc, pos_base_addr, [0x98])
    rot_addr = read_offsets(proc, rot_base_addr, [0x218])

def read_positions():
    return (pymeow.read_float(proc, x_addr), pymeow.read_float(proc, y_addr), pymeow.read_float(proc, z_addr))

def read_rotation():
    return pymeow.read_float(proc, rot_addr)

def write_pos_rot(x,y,z,rot):
    pymeow.write_floats(proc, x_addr, [x,y,z])
    pymeow.write_float(proc, rot_addr, rot)

with open("config.json", "r") as cfg:
    config = json.load(cfg)
    token = config["token"]
    guild_id = config["guild_id"]
    admin_id = config["admin_id"]
    mon = config["monitor"]


gpad = vg.VX360Gamepad()

proc = pymeow.process_by_name("LEGOLCUR_DX11.exe")
pos_base_addr = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x01C77C78
rot_base_addr = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x01C74920

x_addr = read_offsets(proc, pos_base_addr, [0x90])
y_addr = read_offsets(proc, pos_base_addr, [0x94])
z_addr = read_offsets(proc, pos_base_addr, [0x98])
rot_addr = read_offsets(proc, rot_base_addr, [0x218])

intents = discord.Intents(
    guilds=True,
    members=True,
    messages=True,
)

logging.basicConfig(level=logging.INFO)
bot = discord.Bot(description="A bot that can take screenshots in LEGO City Undercover", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as '{bot.user}' (ID: '{bot.user.id}')\n")


@bot.slash_command(name="take_screenshot", description="Takes a screenshot at the specified coordinates!", guild_ids=[guild_id])
async def screenshot(
    ctx: discord.ApplicationContext,
    x: Option(float, description="X Coordinate", min_value=-1000.0, max_value=1000.0),
    y: Option(float, description="Y Coordinate", min_value=0.25, max_value=1000.0),
    z: Option(float, description="Z Coordinate", min_value=-1000.0, max_value=1000.0),
    rot: Option(float, description="Rotation", min_value=-6.3, max_value=6.3)
):
    await ctx.defer()
    pymeow.set_foreground("LEGO City Undercover")

    reload_addrs()
    write_pos_rot(x,y,z,rot)
    
    time.sleep(5)

    gpad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
    gpad.update()
    time.sleep(0.1)
    gpad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
    gpad.update()

    time.sleep(2)
    with mss() as sct:
        filename = sct.shot(mon=mon, output=f"screenshots\\{x}_{y}_{z}_{rot}_{random.randint(0,999999)}.png")
        logging.info(f"{ctx.author.name} ({ctx.author.id}) has taken a screenshot ({filename})")

    if not "LEGOLCUR_DX11.exe" in (i.name() for i in psutil.process_iter()):
        await ctx.respond("Game has crashed! Terminating bot...\nRemind Node to implement a fix for this!")
        await bot.close()

    with open(filename, "rb") as f:
        file = discord.File(fp=f)
        await ctx.respond(file=file)


@bot.slash_command(name="get_chase_info", description="Returns information as to where Chase currently is in the game", guild_ids=[guild_id])
async def info(ctx: discord.ApplicationContext):
    await ctx.respond(f"XYZ: {read_positions()}\nRotation: {read_rotation()}")


@bot.slash_command(name="setup_vgamepad", description="This is a special command that you aren't supposed to be able to see!", guild_ids=[guild_id])
@permissions.is_user(admin_id)
async def setup_gamepad(ctx):
    await ctx.defer()
    pymeow.set_foreground("LEGO City Undercover")

    for i in range(20):
        gpad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gpad.update()
        time.sleep(0.1)
        gpad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
        gpad.update()
        time.sleep(1)

    with mss() as sct:
        filename = sct.shot(mon=mon, output=f"screenshots\\loading.png")

    with open(filename, "rb") as f:
        file = discord.File(fp=f)
        await ctx.respond(content="Game should be loading with vgamepad now!\n(consider reloading addrs now)", file=file)


@bot.slash_command(name="reload_addrs", description="This is a special command that you aren't supposed to be able to see!", guild_ids=[guild_id])
@permissions.is_user(admin_id)
async def reload_addresses(ctx):
    reload_addrs()
    await ctx.respond("Addresses reloaded!")


@bot.slash_command(name="exit", description="This is a special command that you aren't supposed to be able to see!", guild_ids=[guild_id])
@permissions.is_user(admin_id)
async def exit(ctx):
    await ctx.respond("Shutting down bot...\nGoodbye!")
    await bot.close()


bot.run(token)