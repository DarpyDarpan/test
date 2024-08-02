import discord
from discord import app_commands
from discord.ext import commands
import requests

# Setup bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Store config in memory
config_data = {
    "category_id": None,
    "view_role_id": None,
    "type_role_id": None,
}

@bot.event
async def on_ready():
    await bot.tree.sync()  # Sync slash commands
    print(f"Logged in as {bot.user}")

@bot.tree.command(name="config")
async def config_command(interaction: discord.Interaction, category_id: str, view_role_id: str, type_role_id: str):
    try:
        # Convert inputs to integers
        category_id = int(category_id)
        view_role_id = int(view_role_id)
        type_role_id = int(type_role_id)

        # Update config
        config_data["category_id"] = category_id
        config_data["view_role_id"] = view_role_id
        config_data["type_role_id"] = type_role_id

        await interaction.response.send_message("Configuration updated!")
    except ValueError:
        await interaction.response.send_message("Invalid ID provided. Please ensure you enter valid integer IDs.")

@bot.tree.command(name="list")
async def list_command(interaction: discord.Interaction, hypixel_username: str, price: str, extra_info: str = None, ping_role: bool = False):
    # Fetch player data from SkyCrypt API
    try:
        url = f"https://sky.shiiyu.moe/api/v2/profile/{hypixel_username}"
        response = requests.get(url)
        data = response.json()

        # Check if the user exists and has a SkyBlock profile
        profiles = data.get('profiles')
        if not profiles:
            await interaction.response.send_message(f"No SkyBlock profile found for {hypixel_username}.")
            return

        # Use the first profile for simplicity
        profile_data = list(profiles.values())[0]
        stats = profile_data.get('data', {}).get('stats', {})

        # Example stats (you may adjust these according to SkyCrypt's API)
        skyblock_level = stats.get('level', 'N/A')
        skill_average = stats.get('average_skill_level', 'N/A')

    except Exception as e:
        await interaction.response.send_message(f"Failed to retrieve data: {str(e)}")
        return

    # Create channel
    category = bot.get_channel(config_data["category_id"])
    channel = await category.create_text_channel(f"{hypixel_username}-{price}")

    # Set permissions
    view_role = interaction.guild.get_role(config_data["view_role_id"])
    type_role = interaction.guild.get_role(config_data["type_role_id"])

    await channel.set_permissions(view_role, read_messages=True)
    await channel.set_permissions(type_role, send_messages=True)

    # Create the embed message with stats and emojis
    embed = discord.Embed(title=f"Hypixel Skyblock Information", color=discord.Color.blue())
    embed.add_field(name="🌌 Skyblock Level", value=skyblock_level, inline=True)
    embed.add_field(name="⚔️ Skill Average", value=skill_average, inline=True)
    embed.add_field(name="💰 Net Worth", value=f"Total: {price}", inline=True)
    embed.add_field(name="🧾 Details", value=f"Owner: {interaction.user.mention}\nPayment Methods: None Provided", inline=True)

    if extra_info:
        embed.add_field(name="✍️ Extra Info", value=extra_info, inline=False)

    if ping_role:
        await channel.send(view_role.mention)

    await channel.send(embed=embed)
    await interaction.response.send_message(f"Channel created: {channel.mention}")

# Run the bot with your token
bot.run('YOUR_BOT_TOKEN')
