import discord

from discord import app_commands

from discord.ext import commands

import requests

# Setup bot

intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=intents)

# Set your Hypixel API key

hypixel_api_key = '0a530763-b210-414f-89a2-13950044ef40'

# Store config in memory

config = {

    "category_id": None,

    "view_role_id": None,

    "type_role_id": None,

}

@bot.event

async def on_ready():

    await bot.tree.sync()  # Sync slash commands

    print(f"Logged in as {bot.user}")

@bot.tree.command(name="config")

async def config(interaction: discord.Interaction, category_id: str, view_role_id: str, type_role_id: str):

    try:

        # Convert inputs to integers

        category_id = int(category_id)

        view_role_id = int(view_role_id)

        type_role_id = int(type_role_id)

        # Update config

        config["category_id"] = category_id

        config["view_role_id"] = view_role_id

        config["type_role_id"] = type_role_id

        await interaction.response.send_message("Configuration updated!")

    except ValueError:

        await interaction.response.send_message("Invalid ID provided. Please ensure you enter valid integer IDs.")



@bot.tree.command(name="list")

async def list(interaction: discord.Interaction, hypixel_username: str, price: str, extra_info: str = None, ping_role: bool = False):

    # Fetch player data from Hypixel API

    try:

        url = f"https://api.hypixel.net/player?key={hypixel_api_key}&name={hypixel_username}"

        response = requests.get(url)

        data = response.json()

        if not data['success']:

            await interaction.response.send_message(f"Error fetching data: {data.get('cause', 'Unknown error')}")

            return

        player_data = data['player']

    except Exception as e:

        await interaction.response.send_message(f"Failed to retrieve data: {str(e)}")

        return

    # Create channel

    category = bot.get_channel(config["category_id"])

    channel = await category.create_text_channel(f"{hypixel_username}-{price}")

    # Set permissions

    view_role = interaction.guild.get_role(config["view_role_id"])

    type_role = interaction.guild.get_role(config["type_role_id"])

    await channel.set_permissions(view_role, read_messages=True)

    await channel.set_permissions(type_role, send_messages=True)

    # Create the embed message with stats and emojis

    embed = discord.Embed(title=f"Hypixel Skyblock Information", color=discord.Color.blue())

    embed.add_field(name="🌌 Skyblock Level", value=player_data.get('achievements', {}).get('skyblock_level', 'N/A'), inline=True)

    embed.add_field(name="⚔️ Skill Average", value=player_data.get('achievements', {}).get('skill_average', 'N/A'), inline=True)

    # Add other fields here based on available data from API

    embed.add_field(name="💰 Net Worth", value=f"Total: {price}", inline=True)

    embed.add_field(name="🧾 Details", value=f"Owner: {interaction.user.mention}\nPayment Methods: None Provided", inline=True)

    if extra_info:

        embed.add_field(name="✍️ Extra Info", value=extra_info, inline=False)

    if ping_role:

        await channel.send(view_role.mention)

    await channel.send(embed=embed)

    await interaction.response.send_message(f"Channel created: {channel.mention}")

# Run the bot with your token

bot.run('MTI1MDQxOTE3ODU0MDYzMDA1Ng.G-2r4B.IvCvejfaXGJ9NGTssDyplo3Pc_ObLdtYnGPWlc')

