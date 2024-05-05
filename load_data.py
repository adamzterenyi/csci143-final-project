import sys
import psycopg2
from psycopg2.extras import execute_batch
from faker import Faker

fake = Faker()

def connect_db():
    try:
        return psycopg2.connect(
            dbname=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
            host=os.getenv('SQL_HOST'),
            port=os.getenv('SQL_PORT'))
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        sys.exit(1)

def insert_users(conn, n_rows):
    with conn.cursor() as cur:
        data = [(fake.unique.user_name(), fake.password(length=12), fake.random_int(min=18, max=99)) for _ in range(n_rows)]
        query = "INSERT INTO users (username, password, age) VALUES (:u, :p, :a);"
        execute_batch(cur, query, data)
    conn.commit()

def insert_urls(conn, n_rows):
    with conn.cursor() as cur:
        data = [(fake.unique.url(),) for _ in range(n_rows)]
        query = "INSERT INTO urls (url) VALUES (:u);"
        execute_batch(cur, query, data)
    conn.commit()

def insert_messages(conn, n_rows, users_ids, urls_ids):
    with conn.cursor() as cur:
        data = [(fake.random_element(elements=users_ids), fake.sentence(), fake.random_element(elements=urls_ids + [None]), fake.date_time_this_decade()) for _ in range(n_rows)]
        query = "INSERT INTO messages (sender_id, message, id_urls, created_at) VALUES (:s, :m, :iu, :c);"
        execute_batch(cur, query, data)
    conn.commit()

def get_ids(conn, table_name, column_name):
    with conn.cursor() as cur:
        query = f"SELECT {column_name} FROM {table_name};"
        cur.execute(query)
        return [row[0] for row in cur.fetchall()]

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python load_data.py [number_of_rows]")
        sys.exit(1)

    n_rows = int(sys.argv[1])
    conn = connect_db()

    # Insert into users table
    insert_users(conn, max(n_rows, 1000))  # Ensure at least some users

    # Get users ids
    users_ids = get_ids(conn, 'users', 'id')

    # Insert into urls table
    insert_urls(conn, max(int(n_rows * 0.1), 100))  # URLs are less than messages

    # Get urls ids
    urls_ids = get_ids(conn, 'urls', 'id_urls')

    # Insert into messages table
    insert_messages(conn, max((10 * n_rows), 10000), users_ids, urls_ids)  # Target for high volume

    conn.close()
    print("Data loading completed.")
]]>
