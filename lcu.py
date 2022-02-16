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

def patch_functions():
    gravity_address = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0xAB8B3D
    pitch_address   = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x288424
    yaw_address     = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x288449
    overlay_address = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x294BEB
    zoom1_address   = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x28BB77
    zoom2_address   = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x28BB80
    zoom3_address   = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x28BB69
    enable_address  = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x244CF1

    pymeow.nop_code(proc, gravity_address,  8)
    pymeow.nop_code(proc, pitch_address,    5)
    pymeow.nop_code(proc, yaw_address,      5)
    pymeow.nop_code(proc, overlay_address,  7)
    pymeow.nop_code(proc, zoom1_address,    8)
    pymeow.nop_code(proc, zoom2_address,    8)
    pymeow.nop_code(proc, zoom3_address,    8)
    pymeow.nop_code(proc, enable_address,   6)


def reload_addrs():
    global proc, pos_base_addr, rot_base_addr, x_addr, y_addr, z_addr, rot_addr, enable_base_addr
    global enable_addr, pitch_addr, yaw_addr, zoom_addr, p_y_base_addr, zoom_base_addr

    proc = pymeow.process_by_name("LEGOLCUR_DX11.exe")

    pos_base_addr       = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x01C77C78
    rot_base_addr       = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x01C74920
    enable_base_addr    = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x0183F6E8
    p_y_base_addr       = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x01AA54B8
    zoom_base_addr      = proc["modules"]["LEGOLCUR_DX11.exe"]["baseaddr"] + 0x01AA54B8

    x_addr      = read_offsets(proc, pos_base_addr      , [0x90])
    y_addr      = read_offsets(proc, pos_base_addr      , [0x94])
    z_addr      = read_offsets(proc, pos_base_addr      , [0x98])
    rot_addr    = read_offsets(proc, rot_base_addr      , [0x218])
    enable_addr = read_offsets(proc, enable_base_addr   , [0x40, 0x28, 0x18, 0x1BC])
    pitch_addr  = read_offsets(proc, p_y_base_addr      , [0x470, 0x430, 0x580, 0x8, 0x258, 0x20])
    yaw_addr    = read_offsets(proc, p_y_base_addr      , [0x470, 0x430, 0x580, 0x8, 0x258, 0x24])
    zoom_addr   = read_offsets(proc, zoom_base_addr     , [0x470, 0x578])

def read_positions():
    return (pymeow.read_float(proc, x_addr), pymeow.read_float(proc, y_addr), pymeow.read_float(proc, z_addr))

def read_rotation():
    return pymeow.read_float(proc, rot_addr)

def write_pos_rot(x,y,z,rot):
    pymeow.write_floats(proc, x_addr, [x,y,z])
    pymeow.write_float(proc, rot_addr, rot)

def enable_cam():
    pymeow.write_int(proc, enable_addr, 257)

def write_cam(pitch,yaw,zoom):
    pymeow.write_floats(proc, pitch_addr, [pitch,yaw])
    pymeow.write_float(proc, zoom_addr, zoom)

with open("config.json", "r") as cfg:
    config = json.load(cfg)
    token = config["token"]
    guild_id = config["guild_id"]
    admin_id = config["admin_id"]
    mon = config["monitor"]


gpad = vg.VX360Gamepad()
proc = pymeow.process_by_name("LEGOLCUR_DX11.exe")

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


@bot.slash_command(name="chase_screenshot", description="Takes a screenshot at the specified coordinates from the regular 3rd person camera!", guild_ids=[guild_id])
async def screenshot(
    ctx: discord.ApplicationContext,
    x: Option(float, description="X Coordinate", min_value=-1000.0, max_value=1000.0),
    y: Option(float, description="Y Coordinate", min_value=0.25, max_value=1000.0),
    z: Option(float, description="Z Coordinate", min_value=-1000.0, max_value=1000.0),
    rot: Option(float, description="Rotation", min_value=-6.3, max_value=6.3)
):
    await ctx.defer()
    pymeow.set_foreground("LEGO City Undercover")

    patch_functions()
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

    if not ("LEGOLCUR_DX11.exe" in (i.name() for i in psutil.process_iter())):
        await ctx.respond("Game has crashed! Terminating bot...\nRemind Node to implement a fix for this!") # apprently this doesn't work - TODO: fix it
        await bot.close()

    with open(filename, "rb") as f:
        file = discord.File(fp=f)
        await ctx.respond(file=file)


@bot.slash_command(name="camera_screenshot", description="Takes a screenshot at the specified coordinates using the communicator camera!", guild_ids=[guild_id])
async def cam_screenshot(
    ctx: discord.ApplicationContext,
    x: Option(float, description="X Coordinate", min_value=-1000.0, max_value=1000.0),
    y: Option(float, description="Y Coordinate", min_value=0.25, max_value=1000.0),
    z: Option(float, description="Z Coordinate", min_value=-1000.0, max_value=1000.0),
    pitch: Option(float, description="Pitch", min_value=-6.3, max_value=6.3),
    yaw: Option(float, description="Yaw", min_value=-6.3, max_value=6.3),
    zoom: Option(float, description="Zoom", min_value=0, max_value=1.37, default=0),

):
    await ctx.defer()
    pymeow.set_foreground("LEGO City Undercover")

    patch_functions()
    reload_addrs()
    enable_cam()

    write_pos_rot(x,y,z,0)
    
    time.sleep(3)

    gpad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
    gpad.update()
    time.sleep(0.1)
    gpad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB)
    gpad.update()

    time.sleep(2)

    gpad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
    gpad.update()
    time.sleep(0.1)
    gpad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
    gpad.update()

    time.sleep(3)

    write_cam(pitch,yaw,zoom)

    time.sleep(0.5)

    with mss() as sct:
        filename = sct.shot(mon=mon, output=f"screenshots\\cam_{x}_{y}_{z}_{pitch}_{yaw}_{zoom}_{random.randint(0,999999)}.png")
        logging.info(f"{ctx.author.name} ({ctx.author.id}) has taken a screenshot ({filename})")

    if not ("LEGOLCUR_DX11.exe" in (i.name() for i in psutil.process_iter())):
        await ctx.respond("Game has crashed! Terminating bot...\nRemind Node to implement a fix for this!") # apprently this doesn't work - TODO: fix it
        await bot.close()

    with open(filename, "rb") as f:
        file = discord.File(fp=f)
        await ctx.respond(file=file)

    gpad.press_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
    gpad.update()
    time.sleep(0.1)
    gpad.release_button(button=vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
    gpad.update()


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
    patch_functions()
    reload_addrs()
    await ctx.respond("Addresses reloaded!")


@bot.slash_command(name="exit", description="This is a special command that you aren't supposed to be able to see!", guild_ids=[guild_id])
@permissions.is_user(admin_id)
async def exit(ctx):
    await ctx.respond("Shutting down bot...\nGoodbye!")
    await bot.close()


bot.run(token)