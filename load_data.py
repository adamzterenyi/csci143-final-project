import argparse
import os
import time
import uuid
import sqlalchemy
from faker import Faker
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

# Initialize Faker
fake = Faker()

def create_engine(db_url):
    """Create and return a SQLAlchemy engine."""
    engine = sqlalchemy.create_engine(db_url, echo=False, future=True)
    return engine

def insert_users(session, n_rows):
    current_time = int(time.time())  # Capture current Unix timestamp
    users_data = [{
        'username': f"{fake.user_name()}_{uuid.uuid4().hex[:8]}_{current_time}",  # Append a part of UUID and timestamp
        'password': fake.password(),
        'age': fake.random_int(min=18, max=99)
    } for _ in range(n_rows)]
    session.execute(
        text("INSERT INTO users (username, password, age) VALUES (:username, :password, :age) ON CONFLICT (username) DO NOTHING RETURNING id"),
        users_data
    )
    session.commit()

def insert_urls(session, n_rows):
    current_time = int(time.time())  # Capture current Unix timestamp
    urls_data = [{
        'url': f"{fake.url()}?uid={uuid.uuid4().hex[:8]}&ts={current_time}"  # Append a part of UUID and timestamp to ensure uniqueness
    } for _ in range(n_rows)]
    session.execute(
        text("INSERT INTO urls (url) VALUES (:url) ON CONFLICT (url) DO NOTHING RETURNING id_urls"),
        urls_data
    )
    session.commit()

def insert_messages(session, n_users, n_urls):
    user_ids = [id[0] for id in session.execute(text("SELECT id FROM users"))]
    url_ids = [id[0] for id in session.execute(text("SELECT id_urls FROM urls"))]

    messages_data = [{
        'sender_id': fake.random_element(elements=user_ids),
        'message': fake.sentence(),
        'id_urls': fake.random_element(elements=url_ids),
        'created_at': fake.date_time_this_decade()
    } for _ in range(n_users * 10)]  # Example scale factor, adjust as needed

    session.execute(
        text("INSERT INTO messages (sender_id, message, id_urls, created_at) VALUES (:sender_id, :message, :id_urls, :created_at)"),
        messages_data
    )
    session.commit()
    return len(messages_data)

def main():
    start_time = time.time()
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', required=True, help="Database URL")
    parser.add_argument('--user_rows', type=int, default=100)
    args = parser.parse_args()

    engine = create_engine(args.db)
    with Session(engine) as session:
        insert_users(session, args.user_rows)
        insert_urls(session, args.user_rows)  # Assumes a similar count for URLs
        message_count = insert_messages(session, args.user_rows, args.user_rows)  # Assumes messages are based on user count
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Total execution time: {elapsed_time:.2f} seconds.")
    print(f"Total messages inserted: {message_count}")

if __name__ == "__main__":
    main()
