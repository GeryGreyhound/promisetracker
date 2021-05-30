import os
import psycopg2
from dotenv import load_dotenv

# TODO
# This file uses plain sql commands to generate data for development.
# As soon as we have models and/or factories, we need to start using them

load_dotenv()

connection = psycopg2.connect(
    dbname=os.getenv('DB_DATABASE'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'))
connection.autocommit = True
cursor = connection.cursor()

cursor.execute("TRUNCATE TABLE politicians")
cursor.execute("""
    INSERT INTO 
        politicians
        (id, name, location, position, last_elected, program_name, elected)
    VALUES
        ('shrekszilard', 'Shrek Szilárd', 'Mucsaröcsöge-alsó', 'mocsármester', 'TODO', 'Pacal program', '2020-01-01')
""")

cursor.execute("TRUNCATE TABLE promise_categories")
cursor.execute("""
    INSERT INTO
        promise_categories
        (politician_id, category_id, category_name)
    VALUES 
        ('shrekszilard', 1, 'Pacal program')
""")

cursor.execute("TRUNCATE TABLE promises")
cursor.execute("""
    INSERT INTO
        promises
        (id, politician_id, category_id, name) 
    VALUES
        (1, 'shrekszilard', 1, 'zsírral'),
        (2, 'shrekszilard', 1, 'csülökkel')
""")

cursor.execute("TRUNCATE TABLE news_articles")
cursor.execute("""
    INSERT INTO
        news_articles
        (article_date, url, source_name, article_title, politician_id, promise_id, promise_status) 
    VALUES
        ('2020-03-04', 'https://example.com/shrek-zsirral', 'Example', 'Zsírral főzött Shrek', 'shrekszilard', 1, 'pending')
""")

cursor.execute("TRUNCATE TABLE subitems")
cursor.execute("""
    INSERT INTO
        subitems
        (politician_id, parent_id, sub_id, title)
    VALUES 
        ('shrekszilard', 2, 'a', 'füstölve'),
        ('shrekszilard', 2, 'b', 'pácolva')
""")

cursor.execute("TRUNCATE TABLE users")
cursor.execute("""
    INSERT INTO
        users
        (id, email, password, permissions, display_name)
    VALUES
        (1, 'admin@example.com', 'LetMeIn', 'full', 'Admin Aladár'),
        (2, 'editor@example.com', 'LetMeIn', 'limited', 'Editor Elemér')
""")

cursor.execute("TRUNCATE TABLE user_permissions")
cursor.execute("""
    INSERT INTO
        user_permissions
        (user_id, politician_id) 
    VALUES 
        (2, 'shrekszilard')
""")
