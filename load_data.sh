#!/bin/sh

if [ $# -eq 0 ]; then
	echo "Usage: $0 <number_of_users> <number_of_tweets> <number_of_urls>"
	exit 1
fi

if [ $# -eq 1 ]; then
	echo "$1 rows in all tables"
	python3 load_data.py --db=postgresql://postgres:pass@localhost:1318  --num_users=$1 --num_tweets=$1 --num_urls=$1
fi

if [ $# -eq 3 ]; then
	echo "$1 Users\n$2 Tweets\n$3 Urls"
	python3 load_data.py --db=postgresql://postgres:pass@localhost:1318  --num_users=$1 --num_tweets=$2 --num_urls=$3
fi
