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
        print("Database connection pool created successfully.")
    except Exception as error:
        print("Error creating connection pool:", error)

async def close_pool():
    global pool
    if pool:
        await pool.close()
        print("Database connection pool closed.")

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
                planting_cost INTEGER
            )
            ''')

            # 检查并添加 planting_cost 列
            await connection.execute('''
            ALTER TABLE crops ADD COLUMN IF NOT EXISTS planting_cost INTEGER
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
                purchase_cost INTEGER
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
                exploration_cost INTEGER
            )
            ''')

    print("Database tables created successfully.")

async def get_user(discord_id):
    async with pool.acquire() as connection:
        row = await connection.fetchrow('SELECT * FROM users WHERE discord_id = $1', discord_id)
        return row

async def create_user(discord_id, language='en'):
    async with pool.acquire() as connection:
        await connection.execute('INSERT INTO users (discord_id, language) VALUES ($1, $2)', discord_id, language)

async def update_user_language(discord_id, language):
    async with pool.acquire() as connection:
        await connection.execute('UPDATE users SET language = $1 WHERE discord_id = $2', language, discord_id)

async def get_farm(user_id):
    async with pool.acquire() as connection:
        row = await connection.fetchrow('SELECT * FROM farms WHERE user_id = $1', user_id)
        return row

async def create_farm(user_id, name):
    async with pool.acquire() as connection:
        await connection.execute('INSERT INTO farms (user_id, name) VALUES ($1, $2)', user_id, name)

# 添加更多的数据库操作函数...

async def init_base_data():
    crops = [
        ("Wheat", 3600, 10, 5),  # 名称, 生长时间(秒), 售价, 种植成本
        ("Corn", 7200, 20, 10),
        ("Tomato", 10800, 30, 15),
        ("Potato", 14400, 40, 20),
        ("Carrot", 5400, 15, 8)
    ]
    
    animals = [
        ("Chicken", "Egg", 3600, 5, 50),  # 名称, 产品, 生产时间(秒), 产品售价, 购买成本
        ("Cow", "Milk", 7200, 15, 200),
        ("Sheep", "Wool", 14400, 25, 150),
        ("Pig", "Bacon", 10800, 20, 100)
    ]
    
    regions = [
        ("Forest", 1, 10),  # 名称, 所需等级, 探索成本
        ("Mountain", 5, 30),
        ("Beach", 10, 50),
        ("Desert", 15, 70)
    ]

    async with pool.acquire() as connection:
        async with connection.transaction():
            # 插入作物数据
            for crop in crops:
                await connection.execute('''
                INSERT INTO crops (name, growth_time, sell_price, planting_cost)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (name) DO UPDATE SET
                    growth_time = EXCLUDED.growth_time,
                    sell_price = EXCLUDED.sell_price,
                    planting_cost = EXCLUDED.planting_cost
                ''', *crop)

            # 插入动物数据
            for animal in animals:
                await connection.execute('''
                INSERT INTO animals (name, product, production_time, sell_price, purchase_cost)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (name) DO NOTHING
                ''', *animal)

            # 插入地区数据
            for region in regions:
                await connection.execute('''
                INSERT INTO regions (name, required_level, exploration_cost)
                VALUES ($1, $2, $3)
                ON CONFLICT (name) DO NOTHING
                ''', *region)

    print("Base data initialized successfully.")

async def setup_database():
    await init_pool()
    await init_db()
    await init_base_data()  # 添加这一行

# 更新 __all__ 列表以包含所有新函数
__all__ = [
    'setup_database', 'get_user', 'create_user', 'update_user_language',
    'update_user_coins', 'update_user_experience', 'get_farm', 'create_farm',
    'get_crop', 'plant_crop', 'get_planted_crops', 'harvest_crop',
    'get_animal', 'purchase_animal', 'get_owned_animals', 'collect_animal_product',
    'get_region', 'get_all_regions', 'close_pool'
]