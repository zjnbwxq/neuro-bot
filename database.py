import cx_Oracle
import os
from dotenv import load_dotenv

load_dotenv()

# 加载环境变量
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_dsn = os.getenv('DB_DSN')
wallet_location = os.getenv('WALLET_LOCATION')

# 初始化连接池
pool = None

def init_pool():
    global pool
    try:
        pool = cx_Oracle.SessionPool(
            user=db_user,
            password=db_password,
            dsn=db_dsn,
            min=2,
            max=5,
            increment=1,
            encoding="UTF-8",
            nencoding="UTF-8",
            threaded=True,
            events=True,
            wallet_location=wallet_location
        )
        print("Database connection pool created successfully.")
    except cx_Oracle.Error as error:
        print("Error creating connection pool:", error)

def get_connection():
    return pool.acquire()

def release_connection(connection):
    pool.release(connection)

async def init_db():
    with get_connection() as connection:
        cursor = connection.cursor()
        
        # 创建用户表
        cursor.execute('''
        CREATE TABLE users (
            user_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            discord_id VARCHAR2(20) UNIQUE,
            language VARCHAR2(5) DEFAULT 'en',
            coins NUMBER DEFAULT 100,
            experience NUMBER DEFAULT 0
        )
        ''')

        # 创建农场表
        cursor.execute('''
        CREATE TABLE farms (
            farm_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            user_id NUMBER,
            name VARCHAR2(100),
            level NUMBER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')

        # 创建作物表
        cursor.execute('''
        CREATE TABLE crops (
            crop_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name VARCHAR2(50) UNIQUE,
            growth_time NUMBER,
            sell_price NUMBER
        )
        ''')

        # 创建已种植作物表
        cursor.execute('''
        CREATE TABLE planted_crops (
            planted_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            farm_id NUMBER,
            crop_id NUMBER,
            planted_time NUMBER,
            FOREIGN KEY (farm_id) REFERENCES farms (farm_id),
            FOREIGN KEY (crop_id) REFERENCES crops (crop_id)
        )
        ''')

        # 创建动物表
        cursor.execute('''
        CREATE TABLE animals (
            animal_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name VARCHAR2(50) UNIQUE,
            product VARCHAR2(50),
            production_time NUMBER,
            sell_price NUMBER
        )
        ''')

        # 创建已拥有动物表
        cursor.execute('''
        CREATE TABLE owned_animals (
            owned_id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            farm_id NUMBER,
            animal_id NUMBER,
            last_collected_time NUMBER,
            FOREIGN KEY (farm_id) REFERENCES farms (farm_id),
            FOREIGN KEY (animal_id) REFERENCES animals (animal_id)
        )
        ''')

        connection.commit()

async def get_user(discord_id):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM users WHERE discord_id = :id', id=discord_id)
        return cursor.fetchone()

async def create_user(discord_id, language='en'):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO users (discord_id, language) VALUES (:id, :lang)', id=discord_id, lang=language)
        connection.commit()

async def update_user_language(discord_id, language):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('UPDATE users SET language = :lang WHERE discord_id = :id', lang=language, id=discord_id)
        connection.commit()

async def get_farm(user_id):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM farms WHERE user_id = :id', id=user_id)
        return cursor.fetchone()

async def create_farm(user_id, name):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO farms (user_id, name) VALUES (:user_id, :name)', user_id=user_id, name=name)
        connection.commit()

# 添加更多的数据库操作函数...

async def init_base_data():
    crops = [
        ("Wheat", 3600, 10),
        ("Corn", 7200, 20),
        ("Tomato", 10800, 30)
    ]
    animals = [
        ("Chicken", "Egg", 3600, 5),
        ("Cow", "Milk", 7200, 15),
        ("Sheep", "Wool", 14400, 25)
    ]

    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.executemany('INSERT INTO crops (name, growth_time, sell_price) VALUES (:1, :2, :3)', crops)
        cursor.executemany('INSERT INTO animals (name, product, production_time, sell_price) VALUES (:1, :2, :3, :4)', animals)
        connection.commit()

async def setup_database():
    init_pool()
    await init_db()
    await init_base_data()

if __name__ == "__main__":
    import asyncio
    asyncio.run(setup_database())