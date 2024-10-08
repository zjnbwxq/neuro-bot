import discord
from discord import app_commands
import os
from dotenv import load_dotenv
from language_manager import lang_manager

load_dotenv()

user_languages = {}

intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("Commands synced!")

client = MyClient()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

@client.tree.command(name="hello", description="Say hello to the bot")
async def hello(interaction: discord.Interaction):
    lang_code = user_languages.get(str(interaction.user.id), 'en')
    await interaction.response.send_message(lang_manager.get_text('hello', lang_code))

@client.tree.command(name="language", description="Change the bot language")
@app_commands.choices(choice=[
    app_commands.Choice(name="English", value="en"),
    app_commands.Choice(name="简体中文", value="zh_CN"),
    app_commands.Choice(name="繁體中文", value="zh_TW")
])
async def change_language(interaction: discord.Interaction, choice: app_commands.Choice[str]):
    user_languages[str(interaction.user.id)] = choice.value
    await interaction.response.send_message(lang_manager.get_text('language_changed', choice.value))

@client.tree.command(name="farm", description="Show your farm status")
async def farm(interaction: discord.Interaction):
    await interaction.response.send_message("Farm status placeholder")

@client.tree.command(name="market", description="Visit the flea market")
async def market(interaction: discord.Interaction):
    await interaction.response.send_message("Market placeholder")

@client.tree.command(name="fish", description="Go fishing")
async def fish(interaction: discord.Interaction):
    await interaction.response.send_message("Fishing placeholder")

@client.tree.command(name="help", description="Show available commands")
async def help_command(interaction: discord.Interaction):
    await interaction.response.send_message("Help placeholder")

@client.tree.command(name="sync", description="Sync commands (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def sync(interaction: discord.Interaction):
    await client.tree.sync()
    await interaction.response.send_message("Commands synced!")

client.run(os.getenv('DISCORD_TOKEN'))