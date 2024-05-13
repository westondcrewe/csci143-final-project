import os

from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    render_template,
    make_response,
    redirect
)
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
import psycopg2
from werkzeug.utils import secure_filename
import bleach
import datetime

app = Flask(__name__)
engine = sqlalchemy.create_engine(os.getenv('DATABASE_URL'), connect_args={'application_name': '__init__py'})
connection = engine.connect()


def print_debug_info():
    # GET method
    print('request.args.get("username")=', request.args.get("username"))
    print('request.args.get("password")=', request.args.get("password"))

    # POST method
    print('request.form.get("username")=', request.form.get("username"))
    print('request.form.get("password")=', request.form.get("password"))

    # cookies
    print('request.cookies.get("username")=', request.cookies.get("username"))
    print('request.cookies.get("password")=', request.cookies.get("password"))


def are_credentials_good(username, password):
    sql = sqlalchemy.sql.text("""
            SELECT id_user
            FROM users
            WHERE username = :username
              AND password = :password;
    """)
    res = connection.execute(sql, {
        'username': username,
        'password': password})
    if res.fetchone() is None:
        return False
    else:
        return True


def get_tweets(page_num=1, tweets_per_page=20):
    tweets = []
    page_offset = (page_num - 1) * tweets_per_page
    sql_tweet = sqlalchemy.sql.text("""
        SELECT id_user, text, created_at, id_tweet
        FROM tweets
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    res_tweet = connection.execute(sql_tweet, {
        'limit': tweets_per_page,
        'offset': page_offset})
    for tweet in res_tweet.fetchall():
        # get username by id_user of this tweet
        sql_user = sqlalchemy.sql.text("""
            SELECT id_user, username
            FROM users
            WHERE id_user=:id_user
        """)
        res_user = connection.execute(sql_user, {
            'id_user': tweet[0]})
        user = res_user.fetchone()
        username = user[1]
        # get text and created_at of this tweet
        text = tweet[1]
        clean_text = bleach.clean(text)
        linkify_text = bleach.linkify(clean_text)
        created_at = tweet[2]
        tweets.append({
            'username': username,
            'text': linkify_text,
            'created_at': created_at})
    return tweets


def search_tweets(query, page_num):
    sql = sqlalchemy.sql.text("""
    SELECT ts_headline(
        text, plainto_tsquery(:query),
        'Start="<mark><b>", Stop="</b></mark>"')
    AS highlight,
    created_at,
    username
    FROM tweets
    JOIN users ON (tweets.id_user = users.id_user)
    WHERE to_tsvector('english', text) @@ plainto_tsquery(:query)
    ORDER BY ts_rank_cd(to_tsvector('english', text), plainto_tsquery(:query)) DESC, created_at DESC
    LIMIT 20 OFFSET :offset;""")
    res = connection.execute(sql, {
        'offset': (page_num - 1) * 20,
        'query': ' & '.join(query.split())
    })
    tweets = []
    for row_tweet in res.fetchall():
        text = row_tweet[0]
        cleaned_text = bleach.clean(text, tags=['b', 'mark'])
        linkify_text = bleach.linkify(cleaned_text)
        created_at = row_tweet[1]
        username = row_tweet[2]
        tweets.append({
            'text': linkify_text,
            'username': username,
            'created_at': created_at})
    return tweets


@app.route("/")
def root():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    credentials = are_credentials_good(username, password)
    tweets = get_tweets()
    page_num = int(request.args.get('page', 1))
    tweets = get_tweets(page_num)
    next_page = page_num + 1
    prev_page = 1 if page_num == 0 else page_num - 1
    return render_template('root.html', tweets=tweets, logged_in=credentials, username=username, page_num=page_num, next_page=next_page, prev_page=prev_page)


@app.route("/login", methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    print('username=', username)
    print('password=', password)

    good_credentials = are_credentials_good(username, password)
    print('good_credentials=', good_credentials)

    # the first time we've visited, no form submission
    if username is None:
        return render_template('login.html', bad_credentials=False)

    # they submitted a form; we're on the POST method
    else:
        if not good_credentials:
            return render_template('login.html', bad_credentials=True)
        else:
            # if we get here, then we're logged in
            # return 'login successful'

            # create a cookie that contains the username/password info

            # template = render_template('login.html', bad_credentials=False, logged_in=True)
            # return template
            response_login = make_response(redirect('/'))
            response_login.set_cookie('username', username)
            response_login.set_cookie('password', password)
            return response_login


@app.route("/logout")
def logout():
    response_logout = make_response(render_template('logout.html'))
    response_logout.delete_cookie('username')
    response_logout.delete_cookie('password')
    return response_logout


@app.route("/create_account", methods=['GET', 'POST'])
def create_account():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    credentials = are_credentials_good(username, password)
    if credentials:
        print("Logged in")
        return redirect('/')

    new_username = request.form.get('new_username')
    new_password = request.form.get('new_password')
    new_password_verify = request.form.get('new_password_verify')

    if new_username is None:  # not logged in, go to create_account page
        return render_template('create_account.html')
    elif not new_username or not new_password or not new_password_verify:  # missing input
        return render_template('create_account.html', missing_input=True)
    else:  # username and password provided
        if new_password != new_password_verify:
            return render_template('create_account.html', password_mismatch=True)
        else:  # passwords match, must ensure UNIQUE constraint on username
            try:  # failure on insert command means username of new account is already taken
                with connection.begin():
                    sql = sqlalchemy.sql.text('''
                        INSERT INTO users (username, password)
                        VALUES (:username, :password)
                    ''')

                    connection.execute(sql, {
                        'username': new_username,
                        'password': new_password
                    })
                response = make_response(redirect('/'))
                response.set_cookie('username', new_username)
                response.set_cookie('password', new_password)
                return response
            except sqlalchemy.exc.IntegrityError:  # username of new account is already taken
                return render_template('create_account.html', already_exists=True)


@app.route("/create_tweet")
def create_tweet():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    credentials = are_credentials_good(username, password)
    if not credentials:
        return redirect('/')
    sql = sqlalchemy.sql.text('''
        SELECT id_user FROM users
        WHERE username = :username AND password = :password''')
    res = connection.execute(sql, {
        'username': username,
        'password': password})
    for row_user in res.fetchall():
        id_user = row_user[0]
    text = request.form.get('text')
    if text is None:
        return render_template('create_tweet.html', logged_in=credentials)
    elif not text:
        return render_template('create_tweet.html', invalid_message=True, logged_in=credentials)
    else:
        created_at = str(datetime.datetime.now()).split('.')[0]
        sql = sqlalchemy.sql.text("""
            INSERT INTO tweets (id_user, text, created_at)
            VALUES (:id_user, :text, :created_at);
        """)
        res = connection.execute(sql, {
            'id_user': id_user,
            'text': text,
            'created_at': created_at})
    return render_template('create_tweet.html', logged_in=credentials, tweet_sent=True)


@app.route("/search", methods=['GET'])
def search():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    credentials = are_credentials_good(username, password)
    page_num = int(request.args.get('page', 1))
    query = request.args.get('query', '')
    if query:
        tweets = search_tweets(query, page_num)
    else:
        tweets = get_tweets(page_num)
    next_page = page_num + 1
    prev_page = 1 if page_num == 0 else page_num - 1
    response = make_response(render_template('search.html', tweets=tweets, logged_in=credentials, username=username, page_num=page_num, next_page=next_page, prev_page=prev_page, query=query))
    return response
