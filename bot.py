import discord
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv
import logging
from language_manager import lang_manager
from database import setup_database, get_user, create_user, update_user_language, get_farm, create_farm, close_pool

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('NeuroFarmBot')

# 加载环境变量
load_dotenv()

db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_dsn = os.getenv('DB_DSN')

# 设置 intents
intents = discord.Intents.default()
intents.message_content = True

class NeuroFarmBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.db_ready = asyncio.Event()

    async def setup_hook(self):
        logger.info("Starting to setup database...")
        await setup_database()
        self.db_ready.set()
        logger.info("Database setup complete.")

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
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user[2] if user else 'en'
        message = lang_manager.get_text('hello', lang_code)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in hello command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="help", description="Show available commands")
async def help_command(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user[2] if user else 'en'
        help_text = lang_manager.get_text('help_text', lang_code)
        await interaction.response.send_message(help_text)
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="plant", description="Plant crops in your farm")
async def plant(interaction: discord.Interaction, crop: str):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user[2] if user else 'en'
        # 实现种植逻辑
        message = lang_manager.get_text('plant_success', lang_code).format(crop=crop)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in plant command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="breed", description="Breed animals in your farm")
async def breed(interaction: discord.Interaction, animal: str):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user[2] if user else 'en'
        # 实现养殖逻辑
        message = lang_manager.get_text('breed_success', lang_code).format(animal=animal)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in breed command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="explore", description="Explore different regions")
async def explore(interaction: discord.Interaction, region: str):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user[2] if user else 'en'
        # 实现探索逻辑
        message = lang_manager.get_text('explore_result', lang_code).format(region=region)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in explore command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="market", description="Visit the flea market")
async def market(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user[2] if user else 'en'
        # 实现跳蚤市场逻辑
        message = lang_manager.get_text('market_welcome', lang_code)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in market command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="shop", description="Visit the shop")
async def shop(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user[2] if user else 'en'
        # 实现商店逻辑
        message = lang_manager.get_text('shop_welcome', lang_code)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in shop command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="fish", description="Go fishing")
async def fish(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user[2] if user else 'en'
        # 实现钓鱼逻辑
        catch = "a big tuna"  # 示例捕获
        message = lang_manager.get_text('fishing_result', lang_code).format(catch=catch)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in fish command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="mahjong", description="Play mahjong")
async def mahjong(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user[2] if user else 'en'
        # 实现打麻将逻辑
        message = lang_manager.get_text('mahjong_start', lang_code)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in mahjong command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="quest", description="Start a quest")
async def quest(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user[2] if user else 'en'
        # 实现任务系统逻辑
        message = lang_manager.get_text('quest_start', lang_code)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in quest command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="open_chest", description="Open a treasure chest")
async def open_chest(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user[2] if user else 'en'
        # 实现开保险箱逻辑
        message = lang_manager.get_text('chest_opened', lang_code)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in open_chest command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="boss_fight", description="Start a boss fight")
async def boss_fight(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user[2] if user else 'en'
        # 实现boss战逻辑
        message = lang_manager.get_text('boss_fight_start', lang_code)
        await interaction.response.send_message(message)
    except Exception as e:
        logger.error(f"Error in boss_fight command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("No Discord token found. Make sure DISCORD_TOKEN is set in your .env file.")
    else:
        try:
            client.run(token)
        finally:
            asyncio.run(close_pool())