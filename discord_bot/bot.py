import discord
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv
import logging
from discord_bot.language_manager import lang_manager
from backend.database import (
       setup_database, get_user, create_user, update_user_language,
       update_user_coins, update_user_experience, get_farm, create_farm,
       get_crop, plant_crop, get_planted_crops, harvest_crop,
       get_animal, purchase_animal, get_owned_animals, collect_animal_product,
       get_region, get_all_regions, close_pool
   )
import random
from datetime import datetime, timedelta

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('NeuroFarmBot')

# 加载环境变量
load_dotenv()

# 设置 intents
intents = discord.Intents.default()
intents.message_content = True

class NeuroFarmBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.db_ready = asyncio.Event()

    async def setup_hook(self):
        logger.info("开始设置数据库...")
        await setup_database()
        self.db_ready.set()
        logger.info("数据库设置完成。")

        logger.info("开始全局同步命令...")
        try:
            synced = await self.tree.sync()
            logger.info(f"全局同步了 {len(synced)} 个命令")
        except Exception as e:
            logger.error(f"同步命令失败: {e}")

client = NeuroFarmBot()

@client.event
async def on_ready():
    logger.info(f'{client.user} has connected to Discord!')

@client.tree.command(name="hello", description="Say hello to the bot")
async def hello(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        if not user:
            user = await create_user(str(interaction.user.id))
        lang_code = user['language']
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
        lang_code = user['language'] if user else 'en'
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
        if not user:
            user = await create_user(str(interaction.user.id))
        
        farm = await get_farm(user['user_id'])
        if not farm:
            farm = await create_farm(user['user_id'], f"{interaction.user.name}'s Farm")
        
        crop_info = await get_crop(crop)
        if not crop_info:
            await interaction.response.send_message(lang_manager.get_text('crop_not_found', user['language']).format(crop=crop))
            return
        
        if user['coins'] < crop_info['planting_cost']:
            await interaction.response.send_message(lang_manager.get_text('not_enough_coins', user['language']))
            return
        
        planted_crop = await plant_crop(farm['farm_id'], crop_info['crop_id'], datetime.now())
        await update_user_coins(user['user_id'], user['coins'] - crop_info['planting_cost'])
        
        plant_success_msg = lang_manager.get_text('plant_success', user['language']).format(crop=crop)
        harvest_time = planted_crop['planted_time'] + timedelta(seconds=crop_info['growth_time'])
        harvest_time_msg = lang_manager.get_text('harvest_time', user['language']).format(time=harvest_time)
        
        await interaction.response.send_message(f"{plant_success_msg}\n{harvest_time_msg}")
    except Exception as e:
        logger.error(f"Error in plant command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="breed", description="Breed animals in your farm")
async def breed(interaction: discord.Interaction, animal: str):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        if not user:
            user = await create_user(str(interaction.user.id))
        
        farm = await get_farm(user['user_id'])
        if not farm:
            farm = await create_farm(user['user_id'], f"{interaction.user.name}'s Farm")
        
        animal_info = await get_animal(animal)
        if not animal_info:
            await interaction.response.send_message(f"Sorry, {animal} is not available for breeding.")
            return
        
        if user['coins'] < animal_info['purchase_cost']:
            await interaction.response.send_message("You don't have enough coins to purchase this animal.")
            return
        
        purchased_animal = await purchase_animal(farm['farm_id'], animal_info['animal_id'], datetime.now())
        await update_user_coins(user['user_id'], user['coins'] - animal_info['purchase_cost'])
        
        breed_success_msg = lang_manager.get_text('breed_success', user['language']).format(animal=animal)
        await interaction.response.send_message(breed_success_msg)
    except Exception as e:
        logger.error(f"Error in breed command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="explore", description="Explore regions")
async def explore(interaction: discord.Interaction, region: str):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        if not user:
            user = await create_user(str(interaction.user.id))
        
        region_info = await get_region(region)
        if not region_info:
            await interaction.response.send_message(f"Sorry, {region} is not available for exploration.")
            return
        
        if user['level'] < region_info['required_level']:
            await interaction.response.send_message(f"You need to be level {region_info['required_level']} to explore {region}.")
            return
        
        if user['coins'] < region_info['exploration_cost']:
            await interaction.response.send_message("You don't have enough coins to explore this region.")
            return
        
        await update_user_coins(user['user_id'], user['coins'] - region_info['exploration_cost'])
        await update_user_experience(user['user_id'], user['experience'] + random.randint(10, 50))
        
        explore_result_msg = lang_manager.get_text('explore_result', user['language']).format(region=region)
        await interaction.response.send_message(explore_result_msg)
    except Exception as e:
        logger.error(f"Error in explore command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="market", description="Visit the flea market")
async def market(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user['language'] if user else 'en'
        market_welcome_msg = lang_manager.get_text('market_welcome', lang_code)
        await interaction.response.send_message(market_welcome_msg)
    except Exception as e:
        logger.error(f"Error in market command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="shop", description="Visit the shop")
async def shop(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user['language'] if user else 'en'
        shop_welcome_msg = lang_manager.get_text('shop_welcome', lang_code)
        await interaction.response.send_message(shop_welcome_msg)
    except Exception as e:
        logger.error(f"Error in shop command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="fish", description="Go fishing")
async def fish(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        if not user:
            user = await create_user(str(interaction.user.id))
        
        catches = ["a small fish", "a big fish", "a boot", "seaweed", "a treasure chest"]
        catch = random.choice(catches)
        
        await update_user_experience(user['user_id'], user['experience'] + random.randint(5, 20))
        
        fishing_result_msg = lang_manager.get_text('fishing_result', user['language']).format(catch=catch)
        await interaction.response.send_message(fishing_result_msg)
    except Exception as e:
        logger.error(f"Error in fish command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="mahjong", description="Play mahjong")
async def mahjong(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user['language'] if user else 'en'
        mahjong_start_msg = lang_manager.get_text('mahjong_start', lang_code)
        await interaction.response.send_message(mahjong_start_msg)
    except Exception as e:
        logger.error(f"Error in mahjong command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="quest", description="Start a quest")
async def quest(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user['language'] if user else 'en'
        quest_start_msg = lang_manager.get_text('quest_start', lang_code)
        await interaction.response.send_message(quest_start_msg)
    except Exception as e:
        logger.error(f"Error in quest command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="open_chest", description="Open a treasure chest")
async def open_chest(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        if not user:
            user = await create_user(str(interaction.user.id))
        
        coins_found = random.randint(10, 100)
        await update_user_coins(user['user_id'], user['coins'] + coins_found)
        await update_user_experience(user['user_id'], user['experience'] + random.randint(5, 20))
        
        chest_opened_msg = lang_manager.get_text('chest_opened', user['language'])
        await interaction.response.send_message(f"{chest_opened_msg} You found {coins_found} coins!")
    except Exception as e:
        logger.error(f"Error in open_chest command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="boss_fight", description="Start a boss fight")
async def boss_fight(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        user = await get_user(str(interaction.user.id))
        lang_code = user['language'] if user else 'en'
        boss_fight_start_msg = lang_manager.get_text('boss_fight_start', lang_code)
        await interaction.response.send_message(boss_fight_start_msg)
    except Exception as e:
        logger.error(f"Error in boss_fight command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="change_language", description="Change the language")
@app_commands.choices(language=[
    app_commands.Choice(name="简体中文", value="zh_CN"),
    app_commands.Choice(name="繁體中文", value="zh_TW"),
    app_commands.Choice(name="English", value="en")
])
async def change_language(interaction: discord.Interaction, language: app_commands.Choice[str]):
    await client.db_ready.wait()
    try:
        await update_user_language(str(interaction.user.id), language.value)
        await interaction.response.send_message(f"Language changed to {language.name}!")
    except Exception as e:
        logger.error(f"Error in change_language command: {e}")
        await interaction.response.send_message("An error occurred. Please try again later.")

@client.tree.command(name="sync", description="Sync bot commands")
@app_commands.checks.has_permissions(administrator=True)
async def sync(interaction: discord.Interaction):
    await client.db_ready.wait()
    try:
        logger.info("Manually syncing commands...")
        synced = await client.tree.sync()
        await interaction.response.send_message(f"同步了 {len(synced)} 个命令！")
        logger.info(f"Manually synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")
        await interaction.response.send_message("同步命令时发生错误。请稍后再试。")

async def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("No Discord token found. Make sure DISCORD_TOKEN is set in your .env file.")
        return
    try:
        await client.start(token)
    finally:
        await close_pool()

if __name__ == "__main__":
    asyncio.run(main())