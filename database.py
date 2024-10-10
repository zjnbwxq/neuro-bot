import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

# 从环境变量加载数据库连接信息
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')  # 例如："your-db-hostname"
db_port = os.getenv('DB_PORT', 5432)  # PostgreSQL 默认端口为 5432
db_name = os.getenv('DB_NAME')

# 初始化连接池
pool = None

async def init_pool():
    global pool
    try:
        pool = await asyncpg.create_pool(
            user=db_user,
            password=db_password,
            database=db_name,
            host=db_host,
            port=db_port,
            min_size=2,
            max_size=5
        )
        print("数据库连接池创建成功。")
    except Exception as error:
        print("创建连接池时出错:", error)

async def close_pool():
    global pool
    if pool:
        await pool.close()
        print("数据库连接池已关闭。")

async def init_db():
    async with pool.acquire() as connection:
        async with connection.transaction():
            # 创建用户表
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

            # 创建农场表
            await connection.execute('''
            CREATE TABLE IF NOT EXISTS farms (
                farm_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                name VARCHAR(100),
                level INTEGER DEFAULT 1
            )
            ''')

            # 创建作物表
            await connection.execute('''
            CREATE TABLE IF NOT EXISTS crops (
                crop_id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE,
                growth_time INTEGER,
                sell_price INTEGER,
                planting_cost INTEGER,
                emoji VARCHAR(5)
            )
            ''')

            # 创建已种植作物表
            await connection.execute('''
            CREATE TABLE IF NOT EXISTS planted_crops (
                planted_id SERIAL PRIMARY KEY,
                farm_id INTEGER REFERENCES farms(farm_id),
                crop_id INTEGER REFERENCES crops(crop_id),
                planted_time TIMESTAMP,
                is_harvested BOOLEAN DEFAULT FALSE
            )
            ''')

            # 创建动物表
            await connection.execute('''
            CREATE TABLE IF NOT EXISTS animals (
                animal_id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE,
                product VARCHAR(50),
                production_time INTEGER,
                sell_price INTEGER,
                purchase_cost INTEGER,
                emoji VARCHAR(5)
            )
            ''')

            # 创建已拥有动物表
            await connection.execute('''
            CREATE TABLE IF NOT EXISTS owned_animals (
                owned_id SERIAL PRIMARY KEY,
                farm_id INTEGER REFERENCES farms(farm_id),
                animal_id INTEGER REFERENCES animals(animal_id),
                last_collected_time TIMESTAMP
            )
            ''')

            # 创建地区表
            await connection.execute('''
            CREATE TABLE IF NOT EXISTS regions (
                region_id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE,
                required_level INTEGER,
                exploration_cost INTEGER,
                emoji VARCHAR(5)
            )
            ''')

    print("数据库表创建成功。")

async def get_user(discord_id):
    async with pool.acquire() as connection:
        return await connection.fetchrow('SELECT * FROM users WHERE discord_id = $1', discord_id)

async def create_user(discord_id, language='en'):
    async with pool.acquire() as connection:
        return await connection.fetchrow(
            'INSERT INTO users (discord_id, language) VALUES ($1, $2) RETURNING *',
            discord_id, language
        )

async def update_user_language(discord_id, language):
    async with pool.acquire() as connection:
        return await connection.fetchrow(
            'UPDATE users SET language = $2 WHERE discord_id = $1 RETURNING *',
            discord_id, language
        )

async def update_user_coins(user_id, amount):
    async with pool.acquire() as connection:
        return await connection.fetchrow('''
            UPDATE users 
            SET coins = coins + $2 
            WHERE user_id = $1 
            RETURNING *
        ''', user_id, amount)

async def update_user_experience(user_id, amount):
    async with pool.acquire() as connection:
        return await connection.fetchrow('''
            UPDATE users 
            SET experience = experience + $2 
            WHERE user_id = $1 
            RETURNING *
        ''', user_id, amount)

async def get_farm(user_id):
    async with pool.acquire() as connection:
        return await connection.fetchrow('SELECT * FROM farms WHERE user_id = $1', user_id)

async def create_farm(user_id, name):
    async with pool.acquire() as connection:
        return await connection.fetchrow(
            'INSERT INTO farms (user_id, name) VALUES ($1, $2) RETURNING *',
            user_id, name
        )

async def get_crop(crop_name):
    async with pool.acquire() as connection:
        return await connection.fetchrow('SELECT * FROM crops WHERE name = $1', crop_name)

async def plant_crop(farm_id, crop_id, planted_time):
    async with pool.acquire() as connection:
        return await connection.fetchrow('''
            INSERT INTO planted_crops (farm_id, crop_id, planted_time)
            VALUES ($1, $2, $3)
            RETURNING *
        ''', farm_id, crop_id, planted_time)

async def get_planted_crops(farm_id):
    async with pool.acquire() as connection:
        return await connection.fetch('''
            SELECT pc.*, c.name, c.growth_time, c.sell_price
            FROM planted_crops pc
            JOIN crops c ON pc.crop_id = c.crop_id
            WHERE pc.farm_id = $1
        ''', farm_id)

async def harvest_crop(planted_crop_id):
    async with pool.acquire() as connection:
        return await connection.fetchrow('''
            DELETE FROM planted_crops
            WHERE planted_crop_id = $1
            RETURNING *
        ''', planted_crop_id)

async def get_animal(animal_name):
    async with pool.acquire() as connection:
        return await connection.fetchrow('SELECT * FROM animals WHERE name = $1', animal_name)

async def purchase_animal(farm_id, animal_id, purchased_time):
    async with pool.acquire() as connection:
        return await connection.fetchrow('''
            INSERT INTO owned_animals (farm_id, animal_id, purchased_time)
            VALUES ($1, $2, $3)
            RETURNING *
        ''', farm_id, animal_id, purchased_time)

async def get_owned_animals(farm_id):
    async with pool.acquire() as connection:
        return await connection.fetch('''
            SELECT oa.*, a.name, a.product, a.production_time, a.sell_price
            FROM owned_animals oa
            JOIN animals a ON oa.animal_id = a.animal_id
            WHERE oa.farm_id = $1
        ''', farm_id)

async def collect_animal_product(owned_animal_id):
    async with pool.acquire() as connection:
        return await connection.fetchrow('''
            UPDATE owned_animals
            SET last_collected = CURRENT_TIMESTAMP
            WHERE owned_animal_id = $1
            RETURNING *
        ''', owned_animal_id)

async def get_region(region_name):
    async with pool.acquire() as connection:
        return await connection.fetchrow('SELECT * FROM regions WHERE name = $1', region_name)

async def get_all_regions():
    async with pool.acquire() as connection:
        return await connection.fetch('SELECT * FROM regions ORDER BY required_level')

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
            for crop in crops:
                await connection.execute('''
                INSERT INTO crops (name, growth_time, sell_price, planting_cost, emoji)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (name) DO UPDATE SET
                    growth_time = EXCLUDED.growth_time,
                    sell_price = EXCLUDED.sell_price,
                    planting_cost = EXCLUDED.planting_cost,
                    emoji = EXCLUDED.emoji
                ''', *crop)

            # 插入动物数据
            for animal in animals:
                await connection.execute('''
                INSERT INTO animals (name, product, production_time, sell_price, purchase_cost, emoji)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (name) DO UPDATE SET
                    product = EXCLUDED.product,
                    production_time = EXCLUDED.production_time,
                    sell_price = EXCLUDED.sell_price,
                    purchase_cost = EXCLUDED.purchase_cost,
                    emoji = EXCLUDED.emoji
                ''', *animal)

            # 插入地区数据
            for region in regions:
                await connection.execute('''
                INSERT INTO regions (name, required_level, exploration_cost, emoji)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (name) DO UPDATE SET
                    required_level = EXCLUDED.required_level,
                    exploration_cost = EXCLUDED.exploration_cost,
                    emoji = EXCLUDED.emoji
                ''', *region)

    print("Base data initialized successfully.")

async def setup_database():
    await init_pool()
    await drop_all_tables()
    await init_db()
    await init_base_data()
    print("数据库设置完成。")

# 更新 __all__ 列表以包含所有新函数
__all__ = [
    'setup_database', 'get_user', 'create_user', 'update_user_language',
    'update_user_coins', 'update_user_experience', 'get_farm', 'create_farm',
    'get_crop', 'plant_crop', 'get_planted_crops', 'harvest_crop',
    'get_animal', 'purchase_animal', 'get_owned_animals', 'collect_animal_product',
    'get_region', 'get_all_regions', 'close_pool'
]

async def drop_all_tables():
    async with pool.acquire() as connection:
        await connection.execute('''
        DROP TABLE IF EXISTS 
            users, farms, crops, planted_crops, 
            animals, owned_animals, regions
        CASCADE
        ''')
    print("所有表格已删除。")