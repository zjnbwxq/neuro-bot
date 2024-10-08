import discord
from discord import app_commands
import os
from dotenv import load_dotenv
import logging
from language_manager import lang_manager

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('NeuroFarmBot')

# 加载环境变量
load_dotenv()

# 用户语言偏好存储（临时，未来可替换为数据库）
user_languages = {}

# 设置 intents
intents = discord.Intents.default()
intents.message_content = True

class NeuroFarmBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        logger.info("Starting to sync commands globally...")
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s) globally")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

client = NeuroFarmBot()

@client.event
async def on_ready():
    logger.info(f'{client.user} has connected to Discord!')

@client.tree.command(name="hello", description="Say hello to the bot")
async def hello(interaction: discord.Interaction):
    try:
        lang_code = user_languages.get(str(interaction.user.id), 'en')
        message = lang_manager.get_text('hello', lang_code)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in hello command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="language", description="Change the bot language")
@app_commands.choices(choice=[
    app_commands.Choice(name="English", value="en"),
    app_commands.Choice(name="简体中文", value="zh_CN"),
    app_commands.Choice(name="繁體中文", value="zh_TW")
])
async def change_language(interaction: discord.Interaction, choice: app_commands.Choice[str]):
    try:
        user_languages[str(interaction.user.id)] = choice.value
        message = lang_manager.get_text('language_changed', choice.value)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in change_language command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="farm", description="Show your farm status")
async def farm(interaction: discord.Interaction):
    try:
        lang_code = user_languages.get(str(interaction.user.id), 'en')
        # 这里应该有查询数据库获取农场信息的逻辑
        farm_status = "Your farm is doing great!"  # 示例状态
        message = lang_manager.get_text('farm_status', lang_code).format(status=farm_status)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in farm command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="market", description="Visit the flea market")
async def market(interaction: discord.Interaction):
    try:
        lang_code = user_languages.get(str(interaction.user.id), 'en')
        message = lang_manager.get_text('market_welcome', lang_code)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in market command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="fish", description="Go fishing")
async def fish(interaction: discord.Interaction):
    try:
        lang_code = user_languages.get(str(interaction.user.id), 'en')
        catch = "a big tuna"  # 示例捕获
        message = lang_manager.get_text('fishing_result', lang_code).format(catch=catch)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in fish command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="help", description="Show available commands")
async def help_command(interaction: discord.Interaction):
    try:
        lang_code = user_languages.get(str(interaction.user.id), 'en')
        help_text = lang_manager.get_text('help_text', lang_code)
        await interaction.response.send_message(help_text)
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="sync", description="Manually sync commands (Admin only)")
@app_commands.checks.has_permissions(administrator=True)
async def sync(interaction: discord.Interaction):
    try:
        await client.tree.sync()
        await interaction.response.send_message("Commands synced!")
        logger.info(f"Commands manually synced by {interaction.user.name}")
    except Exception as e:
        logger.error(f"Error in manual sync: {e}")
        await interaction.response.send_message("Failed to sync commands. Check logs for details.")

@sync.error
async def sync_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("You need to be an administrator to use this command.", ephemeral=True)
    else:
        logger.error(f"Unexpected error in sync command: {error}")
        await interaction.response.send_message("An unexpected error occurred.", ephemeral=True)

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("No Discord token found. Make sure DISCORD_TOKEN is set in your .env file.")
    else:
        client.run(token)