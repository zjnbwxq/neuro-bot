import os
import logging
import asyncpg
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 从环境变量获取数据库连接信息
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# SQLAlchemy 配置
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 全局连接池
pool = None

async def init_pool():
    global pool
    try:
        pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT,
            min_size=2,
            max_size=5
        )
        logger.info("数据库连接池创建成功。")
    except Exception as error:
        logger.error(f"创建连接池时出错: {error}")
        raise

async def close_pool():
    global pool
    if pool:
        await pool.close()
        logger.info("数据库连接池已关闭。")

async def init_db():
    async with pool.acquire() as connection:
        await connection.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            discord_id VARCHAR(20) UNIQUE,
            language VARCHAR(5) DEFAULT 'en',
            coins INTEGER DEFAULT 100,
            experience INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        )
        ''')
        # ... (其他表的创建语句，保持不变)
    logger.info("数据库表创建成功。")

async def drop_all_tables():
    async with pool.acquire() as connection:
        await connection.execute('''
        DROP TABLE IF EXISTS 
            users, farms, crops, planted_crops, 
            animals, owned_animals, regions
        CASCADE
        ''')
    logger.info("所有表格已删除。")

async def init_base_data():
    crops = [
        ("Wheat", 3600, 10, 5, "🌾"),
        ("Corn", 7200, 20, 10, "🌽"),
        ("Tomato", 10800, 30, 15, "🍅"),
        ("Potato", 14400, 40, 20, "🥔"),
        ("Carrot", 5400, 15, 8, "🥕")
    ]
    
    animals = [
        ("Chicken", "Egg", 3600, 5, 50, "🐔"),
        ("Cow", "Milk", 7200, 15, 200, "🐄"),
        ("Sheep", "Wool", 14400, 25, 150, "🐑"),
        ("Pig", "Bacon", 10800, 20, 100, "🐖")
    ]
    
    regions = [
        ("Forest", 1, 10, "🌳"),
        ("Mountain", 5, 30, "⛰️"),
        ("Beach", 10, 50, "🏖️"),
        ("Desert", 15, 70, "🏜️")
    ]

    async with pool.acquire() as connection:
        async with connection.transaction():
            # 插入作物数据
            await connection.executemany('''
            INSERT INTO crops (name, growth_time, sell_price, planting_cost, emoji)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (name) DO UPDATE SET
                growth_time = EXCLUDED.growth_time,
                sell_price = EXCLUDED.sell_price,
                planting_cost = EXCLUDED.planting_cost,
                emoji = EXCLUDED.emoji
            ''', crops)

            # 插入动物数据
            await connection.executemany('''
            INSERT INTO animals (name, product, production_time, sell_price, purchase_cost, emoji)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (name) DO UPDATE SET
                product = EXCLUDED.product,
                production_time = EXCLUDED.production_time,
                sell_price = EXCLUDED.sell_price,
                purchase_cost = EXCLUDED.purchase_cost,
                emoji = EXCLUDED.emoji
            ''', animals)

            # 插入地区数据
            await connection.executemany('''
            INSERT INTO regions (name, required_level, exploration_cost, emoji)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (name) DO UPDATE SET
                required_level = EXCLUDED.required_level,
                exploration_cost = EXCLUDED.exploration_cost,
                emoji = EXCLUDED.emoji
            ''', regions)

    logger.info("基础数据初始化成功。")

async def setup_database():
    try:
        await init_pool()
        await drop_all_tables()
        await init_db()
        await init_base_data()
        logger.info("数据库设置完成。")
    except Exception as e:
        logger.error(f"数据库设置失败: {e}")
        raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 数据库操作函数
async def get_user(discord_id):
    async with pool.acquire() as connection:
        return await connection.fetchrow('SELECT * FROM users WHERE discord_id = $1', discord_id)

async def create_user(discord_id, language='en'):
    async with pool.acquire() as connection:
        return await connection.fetchrow('''
            INSERT INTO users (discord_id, language)
            VALUES ($1, $2)
            RETURNING *
        ''', discord_id, language)

async def update_user_language(user_id, language):
    async with pool.acquire() as connection:
        return await connection.fetchrow('''
            UPDATE users
            SET language = $2
            WHERE user_id = $1
            RETURNING *
        ''', user_id, language)

async def update_user_coins(user_id, coins):
    async with pool.acquire() as connection:
        return await connection.fetchrow('''
            UPDATE users
            SET coins = coins + $2
            WHERE user_id = $1
            RETURNING *
        ''', user_id, coins)

async def update_user_experience(user_id, experience):
    async with pool.acquire() as connection:
        return await connection.fetchrow('''
            UPDATE users
            SET experience = experience + $2
            WHERE user_id = $1
            RETURNING *
        ''', user_id, experience)

# ... (其他数据库操作函数保持不变)

__all__ = [
    'engine', 'Base', 'SessionLocal', 'setup_database', 'get_user', 'create_user', 
    'update_user_language', 'update_user_coins', 'update_user_experience', 'get_farm', 
    'create_farm', 'get_crop', 'plant_crop', 'get_planted_crops', 'harvest_crop',
    'get_animal', 'purchase_animal', 'get_owned_animals', 'collect_animal_product',
    'get_region', 'get_all_regions', 'close_pool', 'get_db', 'init_pool', 'init_db',
    'init_base_data', 'drop_all_tables'
]