import sys
from sqlalchemy import create_engine, text
from faker import Faker
import os

fake = Faker()

def get_engine():
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD', 'pass')
    db = os.getenv('POSTGRES_DB', 'mydatabase')
    host = os.getenv('SQL_HOST', 'localhost')
    port = os.getenv('SQL_PORT', '5432')
    return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}", echo=True, connect_args={
        'application_name': 'load_data.py',
    })

def insert_users(engine, n_rows):
    with engine.connect() as connection:
        for _ in range(n_rows):
            query = text("INSERT INTO users (username, password, age) VALUES (:username, :password, :age) RETURNING id")
            result = connection.execute(query, username=fake.unique.user_name(), password=fake.password(length=12), age=fake.random_int(min=18, max=99))
            user_id = result.fetchone()[0]
            print(f"Inserted user with ID: {user_id}")

def insert_urls(engine, n_rows):
    with engine.connect() as connection:
        for _ in range(n_rows):
            query = text("INSERT INTO urls (url) VALUES (:url) RETURNING id")
            result = connection.execute(query, url=fake.unique.url())
            url_id = result.fetchone()[0]
            print(f"Inserted URL with ID: {url_id}")

def get_users_ids(engine):
    with engine.connect() as connection:
        query = text("SELECT id FROM users")
        result = connection.execute(query)
        return [row[0] for row in result]

def get_urls_ids(engine):
    with engine.connect() as connection:
        query = text("SELECT id FROM urls")
        result = connection.execute(query)
        return [row[0] for row in result]

def insert_messages(engine, (10 * n_rows), users_ids, urls_ids):
    with engine.connect() as connection:
        for _ in range(n_rows):
            query = text("INSERT INTO messages (sender_id, message, url_id, created_at) VALUES (:sender_id, :message, :url_id, :created_at)")
            connection.execute(query, sender_id=fake.random_element(elements=users_ids), message=fake.sentence(), url_id=fake.random_element(elements=urls_ids + [None]), created_at=fake.date_time_this_decade())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python load_data.py [number_of_rows]")
        sys.exit(1)

    n_rows = int(sys.argv[1])
    engine = get_engine()

    # Insert data
    insert_users(engine, n_rows)  # Insert n_rows users
    insert_urls(engine, n_rows)  # Insert n_rows URLs

    # Fetch IDs
    users_ids = get_users_ids(engine)
    urls_ids = get_urls_ids(engine)

    # Insert messages
    insert_messages(engine, n_rows, users_ids, urls_ids)
