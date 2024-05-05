import argparse
import sqlalchemy
from sqlalchemy import text
from faker import Faker
from sqlalchemy.exc import SQLAlchemyError

# Initialize Faker
fake = Faker()

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('--db', required=True)
parser.add_argument('--user_rows', type=int, default=100)
args = parser.parse_args()

# Create database engine
engine = sqlalchemy.create_engine(args.db, connect_args={'application_name': 'load_data.py'})

def insert_users(connection, n_rows):
    inserted_ids = []
    try:
        with connection.begin() as transaction:
            for _ in range(n_rows):
                username = fake.user_name()
                password = fake.password()
                age = fake.random_int(min=18, max=99)
                query = text("INSERT INTO users (username, password, age) VALUES (:username, :password, :age) RETURNING id")
                result = connection.execute(query, username=username, password=password, age=age)
                inserted_ids.append(result.fetchone()[0])
    except SQLAlchemyError as e:
        print(f"An error occurred while inserting users: {e}")
        transaction.rollback()
    return inserted_ids

def insert_urls(connection, n_rows):
    inserted_ids = []
    try:
        with connection.begin() as transaction:
            for _ in range(n_rows):
                url = fake.url()
                query = text("INSERT INTO urls (url) VALUES (:url) ON CONFLICT (url) DO UPDATE SET url=EXCLUDED.url RETURNING id_urls")
                result = connection.execute(query, url=url)
                inserted_ids.append(result.fetchone()[0])
    except SQLAlchemyError as e:
        print(f"An error occurred while inserting URLs: {e}")
        transaction.rollback()
    return inserted_ids

def insert_messages(connection, n_rows, user_ids, url_ids):
    try:
        with connection.begin() as transaction:
            for _ in range(n_rows * 10):  # Insert 10 times the amount of specified user rows
                sender_id = fake.random_element(elements=user_ids)
                url_id = fake.random_element(elements=url_ids)
                message = fake.sentence()
                query = text("INSERT INTO messages (sender_id, message, id_urls, created_at) VALUES (:sender_id, :message, :id_urls, :created_at)")
                connection.execute(query, sender_id=sender_id, message=message, id_urls=url_id, created_at=fake.date_time_this_decade())
    except SQLAlchemyError as e:
        print(f"An error occurred while inserting messages: {e}")
        transaction.rollback()

def main():
    with engine.connect() as connection:
        user_ids = insert_users(connection, args.user_rows)
        url_ids = insert_urls(connection, 50)  # Example: Insert 50 URLs
        insert_messages(connection, args.user_rows, user_ids, url_ids)
        print(f"Inserted {args.user_rows} users, 50 URLs, and {args.user_rows * 10} messages.")

if __name__ == "__main__":
    main()
