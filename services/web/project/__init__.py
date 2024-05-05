import os
import datetime
import bleach
import sqlalchemy
from werkzeug.utils import secure_filename
from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    render_template,
    make_response,
    redirect
)

app = Flask(__name__)

# engine = sqlalchemy.create_engine('postgresql://postgres:pass@localhost:5432/postgres_db', connect_args={'application_name': '__init__py'})
engine = sqlalchemy.create_engine(os.getenv('DATABASE_URL'), connect_args={'application_name': '__init__py'})
connection = engine.connect()

# flask_env = os.getenv('FLASK_ENV', 'development')

# if flask_env == 'production':
#    database_url = os.getenv('DATABASE_URL', 'default_production_database_url')
# else:
#    database_url = os.getenv('DATABASE_URL', 'default_development_database_url')

# engine = sqlalchemy.create_engine(database_url, connect_args={'applicat    ion_name': '__init__py'})
# connection = engine.connect()


def print_debug_info():
    # GET method
    print('request.args.get("username")=', request.args.get("username"))
    print('request.args.get("password")=', request.args.get("password"))
    # POST method
    print('request.form.get("username")=', request.form.get("username"))
    print('request.form.get("password")=', request.form.get("password"))
    # Cookies method
    print('request.cookies.get("username")=', request.cookies.get("username"))
    print('request.cookies.get("password")=', request.cookies.get("password"))


def are_credentials_good(username, password):
    sql = sqlalchemy.sql.text("""
            SELECT id FROM users WHERE username = :username AND password = :password;""")

    res = connection.execute(sql, {
        'username': username,
        'password': password
    })

    if res.fetchone() is None:
        return False
    else:
        return True


# create a cookie that contains the username/password info
def make_cookie(username, password):
    response = make_response(redirect('/'))
    response.set_cookie('username', username)
    response.set_cookie('password', password)
    return response


def get_messages(a):
    messages = []
    sql = sqlalchemy.sql.text("""
        SELECT sender_id,
        message,
        created_at,
        id
        FROM messages ORDER BY created_at DESC LIMIT 20 OFFSET :offset * 20;""")
    res = connection.execute(sql, {'offset': (a - 1)})
    for row_messages in res.fetchall():
        sql = sqlalchemy.sql.text("""
                SELECT id,
                username,
                password,
                age
                FROM users WHERE id=:id;""")
        user_res = connection.execute(sql, {'id': row_messages[0]})
        row_users = user_res.fetchone()
        message = row_messages[1]
        cleaned_message = bleach.clean(message)
        linked_message = bleach.linkify(cleaned_message)
        messages.append({
            'id': row_messages[3],
            'message': linked_message,
            'username': row_users[1],
            'age': row_users[3],
            'created_at': row_messages[2]})
    return messages


def query_messages(query, a):
    sql = sqlalchemy.sql.text("""
    SELECT sender_id,
    ts_headline(
        message, plainto_tsquery(:query),
        'StartSel="<mark><b>", StopSel="</b></mark>"')
    AS highlighted_message,
    created_at,
    messages.id,
    username,
    age
    FROM messages JOIN users ON (messages.sender_id = users.id)
    WHERE to_tsvector('english', message) @@ plainto_tsquery(:query)
    ORDER BY ts_rank_cd(to_tsvector('english', message), plainto_tsquery(:query)) DESC,
    created_at DESC LIMIT 20 OFFSET :offset;""")

    res = connection.execute(sql, {
        'offset': (a - 1) * 20,
        'query': ' & '.join(query.split())
    })

    messages = []
    for row_messages in res.fetchall():
        message = row_messages[1]
        cleaned_message = bleach.clean(message, tags=['b', 'mark'])
        linked_message = bleach.linkify(cleaned_message)
        messages.append({
            'id': row_messages[3],
            'message': linked_message,
            'username': row_messages[4],
            'age': row_messages[5],
            'created_at': row_messages[2]})
    return messages


# anything starting with an '@' sign is called a "decorator" in python
# decorators generally modify the functions that follow them
@app.route('/')
def root():
    print_debug_info()
    # construct messages,
    # which is a list of dictionaries,
    # where each dictionary contains the information about a message
    # check if logged in correctly
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    try:
        page_number = int(request.args.get('page', 1))
    except TypeError:
        page_number = 1

    messages = get_messages(page_number)

    # Increment for "Next" page, ensure it's not less than 1 for "Previous"
    next_page = page_number + 1
    prev_page = max(1, page_number - 1)  # Prevent going below page 1

    return render_template('root.html', messages=messages, logged_in=good_credentials, username=username, page_number=page_number, next_page=next_page, prev_page=prev_page)


@app.route('/login', methods=['GET', 'POST'])
def login():
    print_debug_info()

    username = request.cookies.get('username')
    password = request.cookies.get('password')

    good_credentials = are_credentials_good(username, password)
    print('good_credentials', good_credentials)
    if good_credentials:
        return redirect('/')

    username = request.form.get('username')
    password = request.form.get('password')

    good_credentials = are_credentials_good(username, password)
    print('good_credentials', good_credentials)

    if password is None and username is None:
        return render_template('login.html')

    # the first time we've visited, no form submission
    if username is None:
        return render_template('login.html', bad_credentials=False)
    # they submitted the form, we're now onto POST method
    else:
        if not good_credentials:
            return render_template('login.html', bad_credentials=True)
        else:
            # if we get here, we're logged in
            # return 'login successful'
            return make_cookie(username, password)


# scheme://hostname/path
# the @app.route defines the path
# the hostname and scheme are given to you in the output of the triangle button
# for settings, the url is http://127.0.01:5000/logout to get this route
@app.route('/logout')
def logout():
    response = make_response(redirect('/'))
    response.delete_cookie('username')
    response.delete_cookie('password')
    return response


@app.route('/create_message', methods=['GET', 'POST'])
def create_message():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)
    if not good_credentials:
        return redirect('/')

    sql = sqlalchemy.sql.text('''SELECT id FROM users
                                 WHERE username = :username AND password = :password''')

    res = connection.execute(sql, {
        'username': username,
        'password': password})

    for row in res.fetchall():
        sender_id = row[0]

    message = request.form.get('message')

    if message is None:
        return render_template('create_message.html', logged_in=good_credentials)
    elif not message:
        return render_template('create_message.html', invalid_message=True, logged_in=good_credentials)
    else:
        created_at = str(datetime.datetime.now()).split('.')[0]
        sql = sqlalchemy.sql.text("""
        INSERT INTO messages (sender_id,message,created_at) VALUES (:sender_id, :message, :created_at);
        """)
        connection.execute(sql, {
            'sender_id': sender_id,
            'message': message,
            'created_at': created_at})

        return render_template('create_message.html', logged_in=good_credentials, message_posted=True)


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    print_debug_info()

    username = request.cookies.get('username')
    password = request.cookies.get('password')

    good_credentials = are_credentials_good(username, password)
    print("good_credentials", good_credentials)

    if good_credentials:
        return redirect('/')

    username_new = request.form.get('username_new')
    password_new = request.form.get('password_new')
    password_retyped = request.form.get('password_retyped')
    age_new = request.form.get('age_new', '')

    if username_new is None:
        return render_template('create_user.html')
    elif not username_new or not password_new:
        return render_template('create_user.html', no_username=True)
    elif not age_new.isnumeric():
        return render_template('create_user.html', invalid_age=True)
    else:
        if password_new != password_retyped:
            return render_template('create_user.html', password_mismatch=True)
        else:
            try:
                sql = sqlalchemy.sql.text('''INSERT into users (username, password, age) values(:username, :password, :age);''')

                res = connection.execute(sql, {
                    'username': username_new,
                    'password': password_new,
                    'age': age_new})

                print(res)

                return make_cookie(username_new, password_new)
            except sqlalchemy.exc.IntegrityError:
                return render_template('create_user.html', existing_user=True)


@app.route('/search', methods=['GET', 'POST'])
def search():

    print('confirm search')

    print_debug_info()

    username = request.cookies.get('username')
    password = request.cookies.get('password')
    good_credentials = are_credentials_good(username, password)

    try:
        page_number = int(request.args.get('page', 1))
    except TypeError:
        page_number = 1

    # Increment for "Next" page, ensure it's not less than 1 for "Previous"
    next_page = page_number + 1
    prev_page = max(1, page_number - 1)  # Prevent going below page 1

    if request.form.get('query'):
        query = request.form.get('query')
    else:
        query = request.args.get('query', '')

    if query:
        messages = query_messages(query, page_number)
    else:
        messages = get_messages(page_number)

    response = make_response(render_template('search.html', messages=messages, logged_in=good_credentials, username=username, page_number=page_number, next_page=next_page, prev_page=prev_page, query=query))

    if query:
        response.set_cookie('query', query)

    return response

# Code used in db_create.py to make 240 users and 205 messages for each user


"""
for user_number in range(240):
    con=sqlite3.connect('twitter_clone.db')
    cur=con.cursor()
    username='Family Guy 100'+str(user_number)
    password='Family Guy 100'+str(user_number)
    password = hashlib.sha256(password.encode("utf-16")).hexdigest()
    age = str(user_number)
    sql="INSERT into users (username,password,age) VALUES (?,?,?);"
    con.execute(sql,[username,password,age])
    con.commit()
    # print('created_user=', username)
    for message_number in range(205):
        sender_id = user_number
        message = generate_comment()
        sql="INSERT into messages (sender_id,message,created_at) VALUES (?,?,?);"
        cur.execute(sql,[sender_id,message,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        con.commit()
        # print('created_message_number=', user_number, message_number)
"""
