import os

from flask import (
    Flask,
    jsonify,
    send_from_directory,
    request,
    render_template,
    make_response
)
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from werkzeug.utils import secure_filename

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


def get_tweets(page_num = 1, tweets_per_page=25):
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
        'offset': page_offset })
    for tweet in res_tweet.fetchall():
        # get username by id_user of this tweet
        sql_user = sqlalchemy.sql.text("""
            SELECT id_user, username
            FROM users
            WHERE id_user=:id_user
        """)
        res_user = connection.execute(sql_user, {
            'id_user': tweet[0] })
        user = res_user.fetchone()
        username = user[1]
        # get text and created_at of this tweet
        text = tweet[1]
        created_at = tweet[2]
        tweets.append({
            'username': username,
            'text': tweet[1],
            'created_at': created_at})
    return tweets


@app.route("/")
def root():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    credentials = are_credentials_good(username, password)
    tweets = get_tweets()
    page_num = int(request.args.get('page', 1))
    tweets = get_tweets(page_num)#, 20)
    next_page = page_num+1
    prev_page = 1 if page_num==0 else page_num-1
    return render_template('root.html', tweets=tweets, logged_in=credentials, username=username, page_num=page_num, next_page=next_page, prev_page=prev_page)

@app.route("/logout")
def logout():
    return "logout\n"

@app.route("/create_account")
def create_account():
    return "create_account\n"

@app.route("/create_message")
def create_messages():
    return "create_messages\n"

@app.route("/search")
def search():
    return "search\n"

