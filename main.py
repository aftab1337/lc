import datetime
from datetime import time
import discord
from discord.ext import commands
import asyncio
import json

# Bot prefix and JSON database file
prefix = "."
data_file = "warnings.json"

# Load existing warnings from data file (optional)
try:
    with open(data_file, "r") as f:
        warnings = json.load(f)
except FileNotFoundError:
    warnings = {}

client = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())

@client.event
async def on_ready():
    print(f"Logged in as {client.user}!")

@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000)}ms")

@client.command()
async def mute(ctx, member: discord.Member, duration=None):
    """Mutes a user for a specified duration (optional)."""
    try:
        await member.voice.set_mute(True)
        embed = discord.Embed(
            title="Muted",
            description=f"{member.name} has been muted.",
            color=discord.Color.red(),
        )
        if duration:
            try:
                duration = int(duration)
                await asyncio.sleep(duration)
                await member.voice.set_mute(False)
                embed.description += f" for {duration} seconds."
            except ValueError:
                embed.description += f" Invalid duration provided."
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("I don't have enough permissions to mute that user.")

@client.command()
async def unmute(ctx, member: discord.Member):
    """Unmutes a user."""
    try:
        await member.voice.set_mute(False)
        embed = discord.Embed(
            title="Unmuted",
            description=f"{member.name} has been unmuted.",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("I don't have enough permissions to unmute that user.")

@client.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    """Bans a user with an optional reason."""
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="Banned",
            description=f"{member.name} has been banned.",
            color=discord.Color.red(),
        )
        if reason:
            embed.description += f" Reason: {reason}"
        await ctx.send(embed=embed)
    except discord.Forbidden:
        await ctx.send("I don't have enough permissions to ban that user.")

@client.command()
async def warn(ctx, member: discord.Member, *, reason):
    """Warns a user and logs the warning."""
    user_id = member.id
    timestamp = int(time.time())
    warnings.setdefault(user_id, [])
    warnings[user_id].append({"timestamp": timestamp, "reason": reason})
    with open(data_file, "w") as f:
        json.dump(warnings, f, indent=4)
    embed = discord.Embed(
        title="Warned",
        description=f"{member.name} has been warned.",
        color=discord.Color.orange(),
    )
    embed.add_field("Reason", reason, inline=False)
    await ctx.send(embed=embed)

@client.command()
async def list_warns(ctx, member: discord.Member):
    """Lists the warnings for a user."""
    user_id = member.id
    if user_id not in warnings:
        embed = discord.Embed(
            title="No Warnings",
            description=f"{member.name} has no warnings.",
            color=discord.Color.green(),
        )
        await ctx.send(embed=embed)
        return
    embed = discord.Embed(
        title=f"Warnings for {member.name}",
        color=discord.Color.orange(),
    )
    for warning in warnings[user_id]:
        timestamp = datetime.datetime.fromtimestamp(warning["timestamp"]).strftime("%d/%m/%Y %H:%M:%S")
        embed.add_field(
            name=f"Warned on {timestamp}", value=warning["reason"], inline=False
        )
    await ctx.send(embed=embed)

@client.event
async def on_message_delete(message):
    """Logs deleted messages in a dedicated channel."""
    log_channel = client.get_channel(1053598009818087503)  # Replace with your actual channel ID
    embed = discord.Embed(
        title="Message Deleted",
        description=f"Message deleted in #{message.channel.name} by {message.author.name}",
        color=discord.Color.red(),
    )
    embed.add_field("Content", message.content, inline=False)
    embed.set_footer(text=f"Channel ID: {message.channel.id}")
    await log_channel.send(embed=embed)

@client.event
async def on_message_edit(message, before):
    """Logs edited messages in a dedicated channel."""
    log_channel = client.get_channel(1053598009818087503)  # Replace with your actual channel ID
    if message.content == before.content:
        # No edits made, skip logging
        return
    embed = discord.Embed(
        title="Message Edited",
        description=f"Message edited in #{message.channel.name} by {message.author.name}",
        color=discord.Color.orange(),
    )
    embed.add_field("Original Content", before.content, inline=False)
    embed.add_field("Edited Content", message.content, inline=False)
    embed.set_footer(text=f"Channel ID: {message.channel.id}")
    await log_channel.send(embed=embed)

# Run the bot with your token
client.run("")
