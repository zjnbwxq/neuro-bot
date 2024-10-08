import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from language_manager import lang_manager

load_dotenv()

# 用户语言偏好存储
user_languages = {}

intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

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
    lang_code = user_languages.get(str(interaction.user.id), 'en')
    # 这里应该有查询数据库获取农场信息的逻辑
    farm_status = "Your farm is doing great!"  # 示例状态
    await interaction.response.send_message(lang_manager.get_text('farm_status', lang_code).format(status=farm_status))

@client.tree.command(name="market", description="Visit the flea market")
async def market(interaction: discord.Interaction):
    lang_code = user_languages.get(str(interaction.user.id), 'en')
    # 这里应该有显示市场商品的逻辑
    await interaction.response.send_message(lang_manager.get_text('market_welcome', lang_code))

@client.tree.command(name="fish", description="Go fishing")
async def fish(interaction: discord.Interaction):
    lang_code = user_languages.get(str(interaction.user.id), 'en')
    # 这里应该有钓鱼游戏的逻辑
    catch = "a big tuna"  # 示例捕获
    await interaction.response.send_message(lang_manager.get_text('fishing_result', lang_code).format(catch=catch))

@client.tree.command(name="help", description="Show available commands")
async def help_command(interaction: discord.Interaction):
    lang_code = user_languages.get(str(interaction.user.id), 'en')
    help_text = lang_manager.get_text('help_text', lang_code)
    await interaction.response.send_message(help_text)

# 运行 bot
client.run(os.getenv('DISCORD_TOKEN'))