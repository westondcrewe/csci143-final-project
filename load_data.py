#!/usr/bin/python3

# imports
import sqlalchemy
import datetime
import argparse
import random
import string
from datetime import datetime, timedelta

################################################################################
# helper functions
################################################################################

def generate_random_text(length):
    '''
    Generate random text of an inputted length.
    This function will be useful in creating fake usernames, passwords, tweet text, and urls.
    '''
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_random_time():
    start_date = datetime(2020, 1, 1)
    end_date = datetime.now()
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 24*60*60)
    return start_date + timedelta(days=random_days, seconds=random_seconds)

def load_users(n_users):
    '''
    Generate data to be inserted into the users table

    id_users BIGSERIAL PRIMARY KEY
    username TEXT NOT NULL UNIQUE
    password TEXT NOT NULL
    '''
    generated_usernames = set()
    for i in range(1,n_users+1):
        print("Create user ", i)

        # generate field values
        #len_un = random.randint(1,10)
        username = "user_"+generate_random_text(10)
        #check to see if this username has already been used, change if so
        while username in generated_usernames:
            username = "user_"+generate_random_text(10)
        generated_usernames.add(username)
        id_user = i
        password = generate_random_text(10)
        
        # insert into table
        sql = sqlalchemy.sql.text('''
            INSERT INTO users (
                id_user,
                username,
                password)
            VALUES (
                :id_user,
                :username,
                :password)
            ON CONFLICT DO NOTHING;
        ''')
        res = connection.execute(sql, {
            'id_user': id_user,
            'username': username,
            'password': password
            })

def load_tweets(n_tweets):
    '''
    Generate data to be inserted into the tweets table
    '''
    user_ids = [row[0] for row in connection.execute('SELECT id_user FROM users')]
    url_ids = [row[0] for row in connection.execute('SELECT id_url FROM urls')]
    for i in range(1,n_tweets+1):
        print("Create tweet ", i)
        id_tweet = i
        tweet_len = random.randint(1,255)
        text = generate_random_text(tweet_len)
        #set tweet(id_user) to be some value from user(id_user) to ensure reference constraint
        id_user = random.choice(user_ids)
        id_url = random.choice(url_ids)
        created_at = generate_random_time()

        # insert into table
        sql = sqlalchemy.sql.text('''
            INSERT INTO tweets (
                id_tweet,
                text,
                id_user,
                id_url,
                created_at)
            VALUES (
                :id_tweet,
                :text,
                :id_user,
                :id_url,
                :created_at)
            ON CONFLICT DO NOTHING;
        ''')
        res = connection.execute(sql, {
            'id_tweet': id_tweet,
            'text': text,
            'id_user': id_user,
            'id_url': id_url,
            'created_at': created_at
            })


def load_urls(n_urls):
    '''
    Generate data to be inserted into the urls table
    '''
    generated_urls = set()
    for i in range(1,n_urls+1):
        print("Create url ", i)
        url = "www.westonfaketwitter_"+generate_random_text(3)
        while url in generated_urls:
            url = "www.westonfaketwitter_"+generate_random_text(3)
        generated_urls.add(url)
        id_url = i

        # insert into table
        sql = sqlalchemy.sql.text('''
            INSERT INTO urls (
                id_url,
                url)
            VALUES (
                :id_url,
                :url)
            ON CONFLICT DO NOTHING;
        ''')
        res = connection.execute(sql, {
            'id_url': id_url,
            'url': url
            })



################################################################################
# main function
################################################################################

if __name__ == '__main__':

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--db',required=True)
    parser.add_argument('--num_users',type=int,required=True)
    parser.add_argument('--num_tweets',type=int,required=True)
    parser.add_argument('--num_urls',type=int,required=True)
    args = parser.parse_args()

    num_users = args.num_users
    num_tweets = args.num_tweets
    num_urls = args.num_urls

    # create database connection
    engine = sqlalchemy.create_engine(args.db, connect_args={
            'application_name': 'load_data.py',
            })
    connection = engine.connect()

    # call helper functions to load tables
    with connection.begin() as trans:
        load_users(num_users)
        load_urls(num_urls)
        load_tweets(num_tweets)

    # close database connection
    connection.close()
