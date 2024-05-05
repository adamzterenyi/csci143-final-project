import argparse
import logging
import os
import sqlalchemy
from faker import Faker
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()

def create_engine(db_url):
    """
    Create and return a SQLAlchemy engine.
    """
    try:
        engine = sqlalchemy.create_engine(db_url, echo=True, future=True)
        logger.info("Database engine created successfully.")
        return engine
    except SQLAlchemyError as e:
        logger.error(f"Error creating database engine: {e}")
        raise

def insert_users(connection, n_rows):
    inserted_ids = []
    for _ in range(n_rows):
        username = fake.user_name()
        password = fake.password()
        age = fake.random_int(min=18, max=99)
        query = text("INSERT INTO users (username, password, age) VALUES (:username, :password, :age) RETURNING id")
        try:
            result = connection.execute(query, username=username, password=password, age=age)
            inserted_ids.append(result.fetchone()[0])
            logger.info("User inserted successfully.")
        except SQLAlchemyError as e:
            logger.error(f"An error occurred while inserting users: {e}")
    return inserted_ids

def insert_urls(connection, n_rows):
    inserted_ids = []
    for _ in range(n_rows):
        url = fake.url()
        query = text("INSERT INTO urls (url) VALUES (:url) ON CONFLICT (url) DO UPDATE SET url=EXCLUDED.url RETURNING id_urls")
        try:
            result = connection.execute(query, url=url)
            inserted_ids.append(result.fetchone()[0])
            logger.info("URL inserted successfully.")
        except SQLAlchemyError as e:
            logger.error(f"An error occurred while inserting URLs: {e}")
    return inserted_ids

def insert_messages(connection, n_rows, user_ids, url_ids):
    for _ in range(n_rows * 10):  # Insert 10 times the amount of specified user rows
        sender_id = fake.random_element(elements=user_ids)
        url_id = fake.random_element(elements=url_ids)
        message = fake.sentence()
        query = text("INSERT INTO messages (sender_id, message, id_urls, created_at) VALUES (:sender_id, :message, :id_urls, :created_at)")
        try:
            connection.execute(query, sender_id=sender_id, message=message, id_urls=url_id, created_at=fake.date_time_this_decade())
            logger.info("Message inserted successfully.")
        except SQLAlchemyError as e:
            logger.error(f"An error occurred while inserting messages: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', required=False, help="Database URL", default=os.getenv("DATABASE_URL"))
    parser.add_argument('--user_rows', type=int, default=100)
    args = parser.parse_args()

    engine = create_engine(args.db)
    with engine.connect() as connection:
        user_ids = insert_users(connection, args.user_rows)
        url_ids = insert_urls(connection, 50)  # Assume you want to insert 50 URLs
        insert_messages(connection, args.user_rows, user_ids, url_ids)
        logger.info(f"Inserted {args.user_rows} users, 50 URLs, and approximately {args.user_rows * 10} messages.")

if __name__ == "__main__":
    main()
