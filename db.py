import psycopg2
from config import *

connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name
)

connection.autocommit = True


def create_table_users():
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users(
                id serial,
                first_name varchar(50) NOT NULL,
                last_name varchar(50) NOT NULL,
                vk_id varchar(20) NOT NULL PRIMARY KEY,
                vk_link varchar(100));"""
        )
    print('таблица Users создана.')

def create_table_seen_users():
    with connection.cursor() as cursor:
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS seen_users(
                id serial,
                vk_id varchar(50) PRIMARY KEY
            );"""
        )
    print('таблица просмотренных пользователей создана.')

def insert_data_users(first_name, last_name, vk_id, vk_link):
    with connection.cursor() as cursor:
        cursor.execute(
            f"""INSERT INTO users(
                first_name,
                last_name,
                vk_id,
                vk_link)
                VALUES(
                    '{first_name}',
                    '{last_name}',
                    '{vk_id}',
                    '{vk_link}');"""
        )

def insert_data_seen_users(vk_id, offset):
    with connection.cursor() as cursor: 
        cursor.execute(
            f"""INSERT INTO seen_users (vk_id)
            VALUES (%s);
            """, (vk_id,)
        )
        

def drop_users():
    with connection.cursor() as cursor:
        cursor.execute(
            """DROP TABLE IF EXISTS users CASCADE;"""
        )
        print('Таблица users удалена')

def drop_seen_users():
    with connection.cursor() as cursor:
        cursor.execute(
            """DROP TABLE IF EXISTS seen_users CASCADE;"""
        )
        print('Таблица seen_users удалена')

def creating_database():
    drop_users()
    create_table_users()
    create_table_seen_users()   

def select(offset):
    with connection.cursor() as cursor:
        cursor.execute(
            f"""SELECT u.first_name,
                        u.last_name,
                        u.vk_id,
                        u.vk_link,
                        su.vk_id
                        FROM users AS u
                        LEFT JOIN seen_users AS su 
                        ON u.vk_id = su.vk_id
                        WHERE su.vk_id IS NULL
                        OFFSET '{offset}';"""
        )
        return cursor.fetchone()
